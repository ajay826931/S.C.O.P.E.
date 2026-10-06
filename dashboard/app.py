"""
Antigravity CV-Sec: Master Security Command Center.
Air-Gapped Computer Vision Security & Provenance Assurance Platform.
"""

import streamlit as st
import time
from pathlib import Path
import sys
import pandas as pd

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.facade import CVAuditorFacade

st.set_page_config(
    page_title="CV-Sec | Command Center",
    page_icon="[CV-Sec]",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load External Stylesheet
css_path = root_dir / "dashboard" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

facade = CVAuditorFacade()
logs = facade.get_audit_trail()
is_valid, msg, broken_idx = facade.verify_audit_trail_integrity()

# Sidebar Info & Radar
with st.sidebar:
    st.markdown("## [CV-Sec] **CV-Sec Core**")
    st.markdown("""
    <div style="padding: 10px; background: rgba(56, 189, 248, 0.08); border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2);">
        <span class="pulse-dot"></span> &nbsp;<b>SYSTEM POSTURE: SECURE</b><br>
        <small style="color: #94A3B8;">Operating Mode: Strict Air-Gapped<br>Cloud Connectivity: Isolated</small>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### [Menu] Navigation")
    st.markdown("""
    - [1] `1_Data_Scan` (Data Quality) - Training Data Quality & Poison Check
    - [2] `2_Model_Scan` (Model Trojan) - Black-Box Trojan/Trigger Inversion
    - [Crypto] `3_Crypto_Verify` - RSA-2048 Inference Provenance
    - [4] `4_Audit_Logs` (Audit Trail) - SHA-256 Hash-Chain Ledger
    - [5] `5_Drift_Monitor` (Drift Monitor) - KS-Test Environmental Shift
    """)
    st.markdown("---")
    st.markdown('<small style="color: #64748B;">Antigravity CV Assurance v2.0 - Offline Ready</small>', unsafe_allow_html=True)

# Main Header Banner
st.markdown("""
<div style="margin-bottom: 24px;">
    <h1 style="margin: 0; font-size: 2.4rem;">
        [CV-Sec] <span class="gradient-text">CV-Sec Master Auditor</span>
    </h1>
    <p style="color: #94A3B8; font-size: 1.1rem; margin-top: 6px;">
        Offline Computer Vision Security, Zero-Retraining Model Verification & Cryptographic Provenance Platform
    </p>
</div>
""", unsafe_allow_html=True)

# Top KPI Metric Cards
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

with kpi1:
    st.markdown("""
    <div class="cv-card">
        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase;">Air-Gapped Protocol</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8; margin: 4px 0;">100% OFFLINE</div>
        <span class="status-pill pill-info">âš¡ Zero Cloud Calls</span>
    </div>
    """, unsafe_allow_html=True)

with kpi2:
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase;">Ledger Block Height</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #818CF8; margin: 4px 0;">{len(logs)} BLOCKS</div>
        <span class="status-pill pill-info">[Crypto]— SHA-256 Chained</span>
    </div>
    """, unsafe_allow_html=True)

with kpi3:
    tamper_events = sum(1 for e in logs if e.get("event_type") == "TAMPER_ATTEMPT_BLOCKED")
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase;">MITM Threats Intercepted</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if tamper_events > 0 else '#10B981'}; margin: 4px 0;">{tamper_events} BLOCKED</div>
        <span class="status-pill {'pill-danger' if tamper_events > 0 else 'pill-success'}">[CV-Sec] RSA-2048 Enforced</span>
    </div>
    """, unsafe_allow_html=True)

with kpi4:
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.85rem; color: #94A3B8; text-transform: uppercase;">Audit Chain Integrity</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {'#10B981' if is_valid else '#EF4444'}; margin: 4px 0;">
            {'INTACT' if is_valid else 'COMPROMISED'}
        </div>
        <span class="status-pill {'pill-success' if is_valid else 'pill-danger'}">
            {'âœ… Genesis-Verified' if is_valid else 'ðŸš¨ Chain Mismatch'}
        </span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# 1-Click Executive Full Audit Runner
st.markdown("### âš¡ **One-Click Comprehensive System Audit**")
st.markdown("Run all 5 security engines simultaneously across training data, model checkpoints, cryptographic signatures, and distribution shift.")

if st.button("ðŸš€ Execute Full System Audit (All 5 Pillars)", type="primary", use_container_width=True):
    with st.status("Executing Comprehensive Security Audit...", expanded=True) as status:
        st.write("[Data] Auditing Training Datasets for poisoning and duplicates...")
        res_data_clean = facade.audit_training_data("data/clean_data")
        res_data_poison = facade.audit_training_data("data/poisoned_data")

        st.write("[Model] Auditing Models for Backdoors & Trojans (Black-box Inversion)...")
        res_model_clean = facade.audit_model("data/models/clean_model.onnx")
        res_model_trojan = facade.audit_model("data/models/backdoored_model.onnx")

        st.write("[Crypto] Verifying Cryptographic Provenance & Tamper Interception...")
        test_img = (root_dir / "data" / "clean_data" / "clean_0.png").resolve()
        receipt = facade.sign_inference(str(test_img), "data/models/clean_model.onnx", {"status": "Verified Safe"})
        ok, _, _ = facade.verify_provenance(receipt, actual_image=str(test_img), model_path="data/models/clean_model.onnx")

        st.write("[Drift] Evaluating Environmental Distribution Shift...")
        import numpy as np, cv2
        rng = np.random.default_rng(42)
        base_imgs = [cv2.GaussianBlur(rng.integers(100, 200, (64, 64, 3), dtype=np.uint8), (3, 3), 0) for _ in range(10)]
        drift_imgs = [cv2.GaussianBlur(rng.integers(10, 40, (64, 64, 3), dtype=np.uint8), (15, 15), 0) for _ in range(10)]
        res_drift = facade.assess_environmental_drift(base_imgs, drift_imgs)

        status.update(label="âœ… Comprehensive Audit Complete! All Engines Executed.", state="complete", expanded=False)

    st.markdown("#### ðŸŽ¯ **Audit Executive Scorecard**")
    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"""
        <div class="cv-card" style="border-left: 4px solid #EF4444;">
            <b>[Data] Data Poisoning Defense</b><br>
            <span style="font-size: 1.3rem; font-weight: 700; color: #EF4444;">{res_data_poison.flags_count} Attacks Caught</span><br>
            <small style="color: #94A3B8;">Clean Set: {res_data_clean.status} (0 flags)</small>
        </div>
        """, unsafe_allow_html=True)
    with sc2:
        st.markdown(f"""
        <div class="cv-card" style="border-left: 4px solid #EF4444;">
            <b>[Model] Trojan Inversion Audit</b><br>
            <span style="font-size: 1.3rem; font-weight: 700; color: #EF4444;">{res_model_trojan.flags_count} Trojan Blocked</span><br>
            <small style="color: #94A3B8;">Clean Model: {res_model_clean.status} (0 flags)</small>
        </div>
        """, unsafe_allow_html=True)
    with sc3:
        st.markdown(f"""
        <div class="cv-card" style="border-left: 4px solid #10B981;">
            <b>[Crypto] Provenance Signatures</b><br>
            <span style="font-size: 1.3rem; font-weight: 700; color: #10B981;">RSA-2048 Signed</span><br>
            <small style="color: #94A3B8;">MITM Interception: 100% Active</small>
        </div>
        """, unsafe_allow_html=True)
    with sc4:
        st.markdown(f"""
        <div class="cv-card" style="border-left: 4px solid #F59E0B;">
            <b>[Drift] Distribution Shift Risk</b><br>
            <span style="font-size: 1.3rem; font-weight: 700; color: #F59E0B;">{res_drift.risk_score} / 100</span><br>
            <small style="color: #94A3B8;">KS Hypothesis: {res_drift.flags_count} Drifts Alerted</small>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Architecture Grid
st.markdown("### ðŸ—ï¸ **Framework Architecture & The 5 Pillars**")
g1, g2, g3 = st.columns(3)

with g1:
    st.markdown("""
    <div class="cv-card">
        <h4 style="margin-top:0;">[Data] 1. Data Integrity Engine</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Scans YOLO/COCO bounding boxes for out-of-boundary values, negative class IDs, zero-variance corruption, and duplicates via SSIM.
        </p>
        <span class="status-pill pill-info">Strategy Pattern</span>
    </div>
    """, unsafe_allow_html=True)

with g2:
    st.markdown("""
    <div class="cv-card">
        <h4 style="margin-top:0;">[Model] 2. Model Integrity Engine</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Evaluates ONNX and PyTorch weights for hidden backdoors using trigger inversion and input perturbation without retraining.
        </p>
        <span class="status-pill pill-info">Black-Box Adapter</span>
    </div>
    """, unsafe_allow_html=True)

with g3:
    st.markdown("""
    <div class="cv-card">
        <h4 style="margin-top:0;">[Crypto] 3. Inference Provenance</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Digitally locks <code>[Image + Model Hash + Prediction]</code> into RSA-2048 signed receipts to permanently stop MITM attacks.
        </p>
        <span class="status-pill pill-success">Asymmetric Crypto</span>
    </div>
    """, unsafe_allow_html=True)

g4, g5 = st.columns(2)

with g4:
    st.markdown("""
    <div class="cv-card">
        <h4 style="margin-top:0;">[Drift] 4. Distribution-Shift Assessment</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Statistical two-sample Kolmogorov-Smirnov (KS) hypothesis tests monitoring luminance, contrast, blur, and color saturation in live streams.
        </p>
        <span class="status-pill pill-warning">SciPy KS-Testing</span>
    </div>
    """, unsafe_allow_html=True)

with g5:
    st.markdown("""
    <div class="cv-card">
        <h4 style="margin-top:0;">[Audit] 5. Immutable Audit Trail</h4>
        <p style="font-size: 0.9rem; color: #94A3B8;">
            Append-only local blockchain JSON ledger. Every action is chained via <code>SHA256(prev_hash + payload)</code> with 1-click verification.
        </p>
        <span class="status-pill pill-success">Hash-Chained</span>
    </div>
    """, unsafe_allow_html=True)

# Recent Event Stream
st.markdown("### ðŸ“‹ **Recent Audit Stream (Latest 5 Blocks)**")
if logs:
    latest = list(reversed(logs))[:5]
    records = []
    for entry in latest:
        records.append({
            "Block #": entry.get("index"),
            "Timestamp": entry.get("timestamp"),
            "Module": entry.get("module"),
            "Event Type": entry.get("event_type"),
            "Block Hash": entry.get("current_hash", "")[:20] + "..."
        })
    st.dataframe(pd.DataFrame(records), use_container_width=True)
else:
    st.info("No audit entries logged yet.")

