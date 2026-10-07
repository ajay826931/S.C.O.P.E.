# -*- coding: utf-8 -*-
"""
Streamlit Page 3: Inference Provenance & Cryptographic Tamper Defense.
Digitally binds [Image + Model Hash + Prediction] into an RSA-2048 digital signature.
Styled with shadcn/ui design standards and Lucide icons.
"""

import streamlit as st
import time
from pathlib import Path
import sys
import json
import numpy as np
import cv2

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dashboard.theme_helper import apply_theme
from dashboard.lucide_icons import lucide
from dashboard.shadcn_ui import get_facade, ShadcnProgressTracker

st.set_page_config(page_title="CV-Sec | Inference Provenance", page_icon="🔐", layout="wide")

# Apply Dynamic Light / Dark Theme
apply_theme()

st.markdown(f"""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        {lucide('lock', size=32, color='#38BDF8')}
        <h1 style="margin: 0; font-size: 2.2rem;">
            <span class="gradient-text">Inference Provenance & Tamper Protection</span>
        </h1>
    </div>
    <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 6px;">
        Cryptographically bind <code>[Raw Image Hash + Model Checkpoint SHA-256 + Inference Prediction]</code> into an unforgeable RSA-2048 digital signature to defeat Man-in-the-Middle (MITM) attacks.
    </p>
</div>
""", unsafe_allow_html=True)

facade = get_facade()

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        {lucide('camera', size=18, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.25rem;">1. Input Image & Model Inference</h3>
    </div>
    """, unsafe_allow_html=True)
    
    model_choice = st.selectbox(
        "Select Certified Model Checkpoint:",
        ["data/models/clean_model.onnx", "data/models/backdoored_model.onnx"]
    )

    clean_sample_p = root_dir / "data" / "clean_data" / "clean_0.png"
    if clean_sample_p.exists():
        test_img = cv2.imread(str(clean_sample_p))
    else:
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.circle(test_img, (50, 50), 30, (56, 189, 248), -1)

    st.image(cv2.cvtColor(test_img, cv2.COLOR_BGR2RGB), caption="Incoming Video Stream Frame (64x64 Raw Sensor Feed)", width=240)

    prediction_input = st.text_area(
        "Inference Result Payload (JSON):",
        value=json.dumps({
            "target": "Restricted Zone Intruder",
            "confidence": 0.988,
            "threat_level": "CRITICAL_ALERT",
            "bounding_box": [0.25, 0.25, 0.50, 0.50]
        }, indent=2),
        height=160
    )

    if st.button("Generate Signed Provenance Certificate", type="primary", use_container_width=True):
        progress_ph = st.empty()
        tracker = ShadcnProgressTracker(
            progress_ph,
            step_names=[
                "Image & Model SHA-256 Hashing",
                "Payload Serialization",
                "RSA-2048/PSS Digital Signature"
            ],
            main_title="Cryptographic Signer"
        )
        try:
            tracker.update(1, "Hashing raw camera frame and ONNX checkpoint...")
            time.sleep(0.12)
            tracker.update(2, "Constructing canonical JSON manifest and digest...")
            pred_dict = json.loads(prediction_input)
            time.sleep(0.12)
            tracker.update(3, "Signing manifest with private RSA key using PSS padding...")
            receipt = facade.sign_inference(test_img, model_choice, pred_dict)
            st.session_state["active_receipt"] = receipt
            st.session_state["active_img"] = test_img
            st.session_state["active_model"] = model_choice
            tracker.finish("Certificate Generated!", "Provenance receipt cryptographically signed and stored.")
            st.success("Provenance receipt signed with RSA Private Key (SHA-256/PSS)!")
        except Exception as e:
            st.error(f"Error signing inference: {e}")

with col_right:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        {lucide('shield-check', size=18, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.25rem;">2. Provenance Certificate & MITM Defense</h3>
    </div>
    """, unsafe_allow_html=True)

    if "active_receipt" in st.session_state:
        receipt = st.session_state["active_receipt"]
        manifest = receipt["manifest"]

        st.markdown(f"""
        <div class="cv-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; align-items: center; gap: 6px;">
                    {lucide('lock', size=16, color='#10B981')}
                    <b>CRYPTOGRAPHIC RECEIPT</b>
                </div>
                <span class="status-pill pill-success">{lucide('check-circle', size=12, color='#10B981')} RSA-2048 VALID</span>
            </div>
            <div style="margin-top: 10px; font-size: 0.85rem;">
                <b>Manifest SHA-256:</b><br>
                <code style="color: #38BDF8;">{receipt['manifest_hash']}</code><br><br>
                <b>Image Fingerprint:</b><br>
                <code>{manifest['image_sha256'][:32]}...</code><br><br>
                <b>Model Fingerprint:</b><br>
                <code>{manifest['model_sha256'][:32]}...</code><br><br>
                <b>Digital Signature:</b><br>
                <code style="word-break: break-all; color: #818CF8;">{receipt['signature_hex'][:64]}...</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 8px; margin: 16px 0 8px 0;">
            {lucide('crosshair', size=18, color='#EF4444')}
            <h3 style="margin: 0; font-size: 1.25rem;">3. Live MITM Tamper Simulation</h3>
        </div>
        """, unsafe_allow_html=True)
        
        tamper_mode = st.radio(
            "Select Attack Simulation Scenario:",
            [
                "Genuine Untampered Stream (Normal Operation)",
                "MITM Attack: Adversary alters prediction to 'Normal / No Threat'",
                "MITM Attack: Adversary injects noise pixel into Camera Frame"
            ]
        )

        if st.button("Verify Cryptographic Integrity", use_container_width=True):
            progress_ph = st.empty()
            tracker = ShadcnProgressTracker(
                progress_ph,
                step_names=[
                    "Recomputing Digests",
                    "RSA PSS Signature Decryption",
                    "Ledger Audit Logging"
                ],
                main_title="Cryptographic Validator"
            )
            tracker.update(1, "Recalculating SHA-256 digests for current image, model, and payload...")
            actual_img = st.session_state["active_img"].copy()
            receipt_to_verify = json.loads(json.dumps(receipt))

            if "Adversary alters prediction" in tamper_mode:
                receipt_to_verify["manifest"]["prediction"]["target"] = "Normal / Authorized Personnel"
                receipt_to_verify["manifest"]["prediction"]["threat_level"] = "CLEAR"
            elif "Adversary injects noise pixel" in tamper_mode:
                actual_img[0, 0] = [255, 0, 0]

            time.sleep(0.12)
            tracker.update(2, "Verifying RSA-2048 signature using public key and PSS padding...")
            ok, msg, details = facade.verify_provenance(
                receipt=receipt_to_verify,
                actual_image=actual_img,
                model_path=st.session_state["active_model"]
            )
            time.sleep(0.12)
            tracker.update(3, "Logging verification event to immutable SHA-256 audit ledger...")
            time.sleep(0.12)
            tracker.finish(
                "Verification Complete!",
                "Provenance validated." if ok else "MITM tampering intercepted and neutralized."
            )

            if ok:
                st.markdown(f"""
                <div class="cv-card" style="border-left: 4px solid #10B981; background: rgba(16, 185, 129, 0.08);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        {lucide('check-circle', size=20, color='#10B981')}
                        <h3 style="margin: 0; color: #10B981;">PROVENANCE VERIFIED</h3>
                    </div>
                    <p style="margin: 6px 0; color: #E2E8F0;">{msg}</p>
                    <small style="color: #94A3B8;">Input Frame, Model Weights, and Output Payload are 100% authentic.</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="cv-card" style="border-left: 4px solid #EF4444; background: rgba(239, 68, 68, 0.08);">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                        {lucide('shield-alert', size=20, color='#EF4444')}
                        <h3 style="margin: 0; color: #EF4444;">TAMPERING DETECTED! ATTACK BLOCKED</h3>
                    </div>
                    <p style="margin: 6px 0; color: #E2E8F0;"><b>Reason:</b> {msg}</p>
                    <span class="status-pill pill-danger">{lucide('alert-triangle', size=12, color='#EF4444')} MITM INTERCEPTED</span> &nbsp;
                    <small style="color: #EF4444;">Malicious tampering logged into immutable ledger.</small>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Generate a signed certificate on the left to activate cryptographic verification.")
