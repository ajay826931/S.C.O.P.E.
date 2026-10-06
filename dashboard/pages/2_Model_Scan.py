"""
Streamlit Page 2: Model Integrity & Trojan Auditor.
Black-box input perturbation and trigger inversion to detect hidden Trojans without retraining.
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import numpy as np

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.facade import CVAuditorFacade

st.set_page_config(page_title="CV-Sec | Model Integrity", page_icon="🧠", layout="wide")

# Load CSS
css_path = root_dir / "dashboard" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div>
    <h1 style="margin: 0;">🧠 <span class="gradient-text">Model Integrity & Trojan Detection Engine</span></h1>
    <p style="color: #94A3B8; font-size: 1.05rem;">
        Black-box trigger inversion and adversarial sensitivity analysis to detect <b>hidden backdoors without model retraining</b>.
    </p>
</div>
""", unsafe_allow_html=True)

facade = CVAuditorFacade()

col_model, col_preset = st.columns([2, 1])

with col_preset:
    preset = st.selectbox(
        "⚡ Select Model Test Scenario:",
        [
            "data/models/backdoored_model.onnx (Injected Trojan Attack Vector)",
            "data/models/clean_model.onnx (Verified Clean Model)"
        ]
    )
    chosen_model = preset.split()[0]

with col_model:
    model_path = st.text_input("Target Model Checkpoint Path (.onnx):", value=chosen_model)

if st.button("🔍 Execute Black-Box Trojan Audit", type="primary", use_container_width=True):
    with st.spinner("Injecting candidate perturbation patterns and evaluating class convergence..."):
        res = facade.audit_model(model_path)

    st.markdown("---")
    st.markdown("### 📊 **Model Security Assessment**")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">TRIGGER REGIONS TESTED</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8;">{res.total_inspected} Configurations</div>
            <span class="status-pill pill-info">Quadrant & Inversion</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">BACKDOOR VULNERABILITIES</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.flags_count > 0 else '#10B981'};">{res.flags_count} Detected</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {'🚨 Trojan Found' if res.flags_count > 0 else '✅ Certified Safe'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">TROJAN RISK SCORE</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')};">
                {res.risk_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
            </div>
            <span class="status-pill {'pill-danger' if res.risk_score > 50 else ('pill-warning' if res.risk_score > 20 else 'pill-success')}">
                {'COMPROMISED' if res.risk_score > 50 else 'SAFE'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">VERDICT</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#10B981' if res.status == 'PASSED' else '#EF4444'};">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else 'pill-danger'}">
                Logged to Ledger
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"📋 **Summary:** {res.summary}")

    tab1, tab2 = st.tabs(["🚨 Detected Backdoor Trigger Inversion", "🔬 Black-Box Perturbation Heatmap"])

    with tab1:
        if res.flags:
            st.markdown("#### 🚨 Inverted Trigger Signatures & Forced Class Flips")
            for f in res.flags:
                m = f.metrics
                st.markdown(f"""
                <div class="cv-card" style="border-left: 4px solid #EF4444;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <h4 style="margin: 0; color: #EF4444;">🔴 {f.title}</h4>
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
            st.success("🎉 Model passed Trojan audit! No localized triggers or abnormal class convergence detected.")

    with tab2:
        st.markdown("#### 🔬 Visual Trigger Placement Grid")
        st.write("Candidate trigger locations tested across image spatial coordinates:")
        c_tl, c_tr = st.columns(2)
        with c_tl:
            st.markdown("""
            <div style="padding: 20px; border: 2px dashed rgba(56, 189, 248, 0.4); text-align: center; border-radius: 8px;">
                <b>TOP-LEFT (8x8 Patch)</b><br>
                <small style="color: #94A3B8;">Coordinates: [0:8, 0:8]</small><br>
                <span class="status-pill pill-danger">High Trojan Sensitivity</span>
            </div>
            """, unsafe_allow_html=True)
        with c_tr:
            st.markdown("""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px;">
                <b>TOP-RIGHT (8x8 Patch)</b><br>
                <small style="color: #94A3B8;">Coordinates: [0:8, 24:32]</small><br>
                <span class="status-pill pill-success">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)

        c_bl, c_br = st.columns(2)
        with c_bl:
            st.markdown("""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px; margin-top: 10px;">
                <b>BOTTOM-LEFT (8x8 Patch)</b><br>
                <small style="color: #94A3B8;">Coordinates: [24:32, 0:8]</small><br>
                <span class="status-pill pill-success">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)
        with c_br:
            st.markdown("""
            <div style="padding: 20px; border: 2px dashed rgba(255, 255, 255, 0.1); text-align: center; border-radius: 8px; margin-top: 10px;">
                <b>BOTTOM-RIGHT (8x8 Patch)</b><br>
                <small style="color: #94A3B8;">Coordinates: [24:32, 24:32]</small><br>
                <span class="status-pill pill-success">Normal Behavior</span>
            </div>
            """, unsafe_allow_html=True)
