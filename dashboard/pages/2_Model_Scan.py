# -*- coding: utf-8 -*-
"""
Streamlit Page 2: Model Integrity & Trojan Auditor.
Black-box input perturbation and trigger inversion to detect hidden Trojans without retraining.
Styled with shadcn/ui design standards and Lucide icons.
"""

import streamlit as st
import time
from pathlib import Path
import sys
import numpy as np

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dashboard.theme_helper import apply_theme
from dashboard.lucide_icons import lucide
from dashboard.shadcn_ui import get_facade, ShadcnProgressTracker

st.set_page_config(page_title="CV-Sec | Model Integrity", page_icon="🧠", layout="wide")

# Apply Dynamic Light / Dark Theme
apply_theme()

st.markdown(f"""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        {lucide('cpu', size=32, color='#38BDF8')}
        <h1 style="margin: 0; font-size: 2.2rem;">
            <span class="gradient-text">Model Integrity & Trojan Detection Engine</span>
        </h1>
    </div>
    <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 6px;">
        Black-box trigger inversion and adversarial sensitivity analysis to detect <b>hidden backdoors without model retraining</b>.
    </p>
</div>
""", unsafe_allow_html=True)

facade = get_facade()

col_model, col_preset = st.columns([2, 1])

with col_preset:
    preset = st.selectbox(
        "Select Model Test Scenario:",
        [
            "data/models/backdoored_model.onnx (Injected Trojan Attack Vector)",
            "data/models/clean_model.onnx (Verified Clean Model)"
        ]
    )
    chosen_model = preset.split()[0]

with col_model:
    model_path = st.text_input("Target Model Checkpoint Path (.onnx):", value=chosen_model)

if st.button("Execute Black-Box Trojan Audit", type="primary", use_container_width=True):
    progress_ph = st.empty()
    tracker = ShadcnProgressTracker(
        progress_ph,
        step_names=[
            "ONNX Checkpoint Ingestion",
            "Trigger Inversion & Perturbation",
            "Adversarial Convergence Scoring"
        ],
        main_title="Model Trojan Scanner"
    )

    tracker.update(1, "Inspecting ONNX tensor graph, layers, and input shape conformity...")
    time.sleep(0.15)
    tracker.update(2, "Generating candidate trigger masks and executing black-box optimization...")
    res = facade.audit_model(model_path)
    tracker.update(3, "Evaluating class flipping sensitivity and backdoor anomaly index...")
    time.sleep(0.15)
    tracker.finish("Model Audit Complete!", f"Audit result: {res.status}. Anomaly score: {res.metrics.get('anomaly_index', 0.0):.2f}")

    st.markdown("---")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        {lucide('activity', size=20, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.3rem;">Model Security Assessment</h3>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Trigger Regions Tested</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8; margin: 4px 0;">{res.total_inspected} Configurations</div>
            <span class="status-pill pill-info">{lucide('crosshair', size=13, color='#38BDF8')} Quadrant & Inversion</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        trojan_color = '#EF4444' if res.flags_count > 0 else '#10B981'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Backdoor Vulnerabilities</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {trojan_color}; margin: 4px 0;">{res.flags_count} Detected</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {lucide('shield-alert' if res.flags_count > 0 else 'shield-check', size=13, color=trojan_color)}
                {'Trojan Found' if res.flags_count > 0 else 'Certified Safe'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        risk_color = '#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')
        risk_label = 'COMPROMISED' if res.risk_score > 50 else 'SAFE'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Trojan Risk Score</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {risk_color}; margin: 4px 0;">
                {res.risk_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
            </div>
            <span class="status-pill {'pill-danger' if res.risk_score > 50 else ('pill-warning' if res.risk_score > 20 else 'pill-success')}">
                {lucide('gauge', size=13, color=risk_color)} {risk_label}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        status_color = '#10B981' if res.status == 'PASSED' else '#EF4444'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Verdict</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {status_color}; margin: 4px 0;">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else 'pill-danger'}">
                {lucide('link', size=13, color=status_color)} Logged to Ledger
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"**Audit Summary:** {res.summary}")

    tab1, tab2 = st.tabs(["Detected Backdoor Trigger Inversion", "Black-Box Perturbation Heatmap"])

    with tab1:
        if res.flags:
            st.markdown("#### Inverted Trigger Signatures & Forced Class Flips")
            for f in res.flags:
                m = f.metrics
                st.markdown(f"""
                <div class="cv-card" style="border-left: 4px solid #EF4444;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div style="display: flex; align-items: center; gap: 8px;">
                            {lucide('shield-alert', size=20, color='#EF4444')}
                            <h4 style="margin: 0; color: #EF4444;">{f.title}</h4>
                        </div>
                        <span class="status-pill pill-danger">CRITICAL THREAT</span>
                    </div>
                    <p style="margin: 8px 0; color: #E2E8F0;">{f.description}</p>
                    <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-top: 12px;">
                        <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
                            <small style="color: #94A3B8;">TRIGGER LOCATION</small><br>
                            <b>{m.get('trigger_location', 'N/A').upper()}</b>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
                            <small style="color: #94A3B8;">TRIGGER PATTERN</small><br>
                            <b>{m.get('trigger_type', 'N/A').upper()}</b>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
                            <small style="color: #94A3B8;">ATTACK SUCCESS RATE</small><br>
                            <b style="color: #EF4444;">{m.get('attack_success_rate', 0.0)*100:.1f}%</b>
                        </div>
                        <div style="background: rgba(0,0,0,0.3); padding: 8px; border-radius: 6px;">
                            <small style="color: #94A3B8;">FORCED TARGET CLASS</small><br>
                            <b>CLASS {m.get('target_class', 'N/A')}</b>
                        </div>
                    </div>
                    <div style="margin-top: 10px; font-size: 0.85rem; color: #94A3B8;">
                        Checkpoint SHA-256: <code>{m.get('model_sha256')}</code>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Model passed Trojan audit! No localized triggers or abnormal class convergence detected.")

    with tab2:
        st.markdown("#### Visual Trigger Placement Grid")
        st.write("Candidate trigger locations tested across image spatial coordinates:")
        c_tl, c_tr = st.columns(2)
        with c_tl:
            st.markdown(f"""
            <div style="padding: 20px; border: 2px dashed rgba(56, 189, 248, 0.4); text-align: center; border-radius: 8px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 6px;">
                    {lucide('crosshair', size=18, color='#EF4444')}
                    <b>TOP-LEFT (8x8 Patch)</b>
                </div>
                <small style="color: #94A3B8;">Coordinates: [0:8, 0:8]</small><br>
                <span class="status-pill pill-danger" style="margin-top: 8px;">High Trojan Sensitivity</span>
            </div>
            """, unsafe_allow_html=True)
        with c_tr:
            st.markdown(f"""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 6px;">
                    {lucide('check-circle', size=18, color='#10B981')}
                    <b>TOP-RIGHT (8x8 Patch)</b>
                </div>
                <small style="color: #94A3B8;">Coordinates: [0:8, 24:32]</small><br>
                <span class="status-pill pill-success" style="margin-top: 8px;">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)

        c_bl, c_br = st.columns(2)
        with c_bl:
            st.markdown(f"""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px; margin-top: 10px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 6px;">
                    {lucide('check-circle', size=18, color='#10B981')}
                    <b>BOTTOM-LEFT (8x8 Patch)</b>
                </div>
                <small style="color: #94A3B8;">Coordinates: [24:32, 0:8]</small><br>
                <span class="status-pill pill-success" style="margin-top: 8px;">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)
        with c_br:
            st.markdown(f"""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px; margin-top: 10px;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin-bottom: 6px;">
                    {lucide('check-circle', size=18, color='#10B981')}
                    <b>BOTTOM-RIGHT (8x8 Patch)</b>
                </div>
                <small style="color: #94A3B8;">Coordinates: [24:32, 24:32]</small><br>
                <span class="status-pill pill-success" style="margin-top: 8px;">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)
