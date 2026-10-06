"""
Streamlit Page 5: Environmental Drift & Distribution-Shift Monitor.
Monitors live camera streams against training baselines using two-sample Kolmogorov-Smirnov (KS) tests.
"""

import streamlit as st
from pathlib import Path
import sys
import numpy as np
import cv2
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.facade import CVAuditorFacade

st.set_page_config(page_title="CV-Sec | Drift Monitor", page_icon="📈", layout="wide")

# Load CSS
css_path = root_dir / "dashboard" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div>
    <h1 style="margin: 0;">📈 <span class="gradient-text">Environmental Drift & Distribution-Shift Monitor</span></h1>
    <p style="color: #94A3B8; font-size: 1.05rem;">
        Statistical hypothesis testing via <b>Two-Sample Kolmogorov-Smirnov (KS) tests</b> tracking luminance, contrast, blur/defocus, and color saturation in real-time camera streams.
    </p>
</div>
""", unsafe_allow_html=True)

facade = CVAuditorFacade()

col_sim1, col_sim2 = st.columns(2)

with col_sim1:
    st.markdown("### ☀️ **1. Baseline Reference Distribution (Daytime)**")
    rng = np.random.default_rng(42)
    # Baseline: 12 clear daytime images
    base_imgs = [cv2.GaussianBlur(rng.integers(100, 220, (64, 64, 3), dtype=np.uint8), (3, 3), 0) for _ in range(12)]
    st.image(cv2.cvtColor(base_imgs[0], cv2.COLOR_BGR2RGB), caption="Sample Baseline Reference Frame (Daylight)", width=200)

with col_sim2:
    st.markdown("### 🌧️ **2. Live Operational Stream Scenario**")
    stream_type = st.selectbox(
        "Select Live Stream Condition:",
        [
            "Severe Environmental Shift (Night Camera + Heavy Fog/Blur Attack)",
            "Normal Operational Stream (Slight Illumination Variance)"
        ]
    )

    if "Severe Environmental Shift" in stream_type:
        live_imgs = [cv2.GaussianBlur(rng.integers(10, 35, (64, 64, 3), dtype=np.uint8), (15, 15), 0) for _ in range(12)]
    else:
        live_imgs = [cv2.GaussianBlur(rng.integers(95, 225, (64, 64, 3), dtype=np.uint8), (3, 3), 0) for _ in range(12)]

    st.image(cv2.cvtColor(live_imgs[0], cv2.COLOR_BGR2RGB), caption=f"Live Feed: {stream_type.split()[0]}", width=200)

if st.button("📊 Run Statistical KS-Drift Assessment", type="primary", use_container_width=True):
    with st.spinner("Extracting luminance, contrast, Laplacian sharpness, and running KS hypothesis tests..."):
        res = facade.assess_environmental_drift(base_imgs, live_imgs)

    st.markdown("---")
    st.markdown("### 📊 **Statistical Drift Summary**")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">STREAM SAMPLES</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8;">{res.total_inspected} Frames</div>
            <span class="status-pill pill-info">Live Inspection</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">FEATURE DRIFTS</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.flags_count > 0 else '#10B981'};">{res.flags_count} Detected</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {'⚠️ Out of Spec' if res.flags_count > 0 else '✅ Stable'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">ENVIRONMENT RISK SCORE</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')};">
                {res.risk_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
            </div>
            <span class="status-pill {'pill-danger' if res.risk_score > 50 else ('pill-warning' if res.risk_score > 20 else 'pill-success')}">
                {'HIGH DRIFT' if res.risk_score > 50 else 'ACCEPTABLE'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">STREAM STATUS</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#10B981' if res.status == 'PASSED' else '#EF4444'};">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else 'pill-danger'}">
                Alpha = 0.01
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"📋 **Summary:** {res.summary}")

    if res.flags:
        st.markdown("#### 🚨 Dimension-by-Dimension KS Drift Metrics")
        drift_data = []
        for f in res.flags:
            m = f.metrics
            drift_data.append({
                "Visual Dimension": m.get("feature", "N/A").upper(),
                "KS-Statistic (D)": m.get("ks_statistic"),
                "p-value": f"{m.get('p_value', 1.0):.4e}",
                "Baseline Mean": m.get("baseline_mean"),
                "Live Current Mean": m.get("current_mean"),
                "Drift Diagnosis": f.description
            })
        st.dataframe(pd.DataFrame(drift_data), use_container_width=True)
    else:
        st.success("✅ Operational stream distribution is statistically consistent with baseline reference data.")
