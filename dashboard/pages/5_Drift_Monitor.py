# -*- coding: utf-8 -*-
"""
Streamlit Page 5: Environmental Drift & Distribution-Shift Monitor.
Monitors live camera streams against training baselines using two-sample Kolmogorov-Smirnov (KS) tests.
Styled with shadcn/ui design standards and Lucide icons.
"""

import streamlit as st
import time
from pathlib import Path
import sys
import numpy as np
import cv2

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from dashboard.theme_helper import apply_theme
from dashboard.lucide_icons import lucide
from dashboard.shadcn_ui import get_facade, ShadcnProgressTracker, render_shadcn_table

st.set_page_config(page_title="CV-Sec | Drift Monitor", page_icon="📈", layout="wide")

# Apply Dynamic Light / Dark Theme
apply_theme()

st.markdown(f"""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        {lucide('activity', size=32, color='#38BDF8')}
        <h1 style="margin: 0; font-size: 2.2rem;">
            <span class="gradient-text">Environmental Drift & Distribution-Shift Monitor</span>
        </h1>
    </div>
    <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 6px;">
        Statistical hypothesis testing via <b>Two-Sample Kolmogorov-Smirnov (KS) tests</b> tracking luminance, contrast, blur/defocus, and color saturation in real-time camera streams.
    </p>
</div>
""", unsafe_allow_html=True)

facade = get_facade()

col_sim1, col_sim2 = st.columns(2)

with col_sim1:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        {lucide('camera', size=18, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.25rem;">1. Baseline Reference Distribution (Daytime)</h3>
    </div>
    """, unsafe_allow_html=True)
    rng = np.random.default_rng(42)
    base_imgs = [cv2.GaussianBlur(rng.integers(100, 220, (64, 64, 3), dtype=np.uint8), (3, 3), 0) for _ in range(12)]
    st.image(cv2.cvtColor(base_imgs[0], cv2.COLOR_BGR2RGB), caption="Sample Baseline Reference Frame (Daylight)", width=200)

with col_sim2:
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
        {lucide('sliders', size=18, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.25rem;">2. Live Operational Stream Scenario</h3>
    </div>
    """, unsafe_allow_html=True)
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

if st.button("Run Statistical KS-Drift Assessment", type="primary", use_container_width=True):
    progress_ph = st.empty()
    tracker = ShadcnProgressTracker(
        progress_ph,
        step_names=[
            "Frame Feature Extraction",
            "Color & Blur Variance Analysis",
            "Two-Sample KS Hypothesis Testing"
        ],
        main_title="Distribution Drift Assessor"
    )
    tracker.update(1, "Sampling frame matrices and extracting luminance histograms...")
    time.sleep(0.12)
    tracker.update(2, "Measuring Laplacian blur variance and channel contrast ratios...")
    time.sleep(0.12)
    tracker.update(3, "Executing SciPy 2-sample Kolmogorov-Smirnov statistical tests...")
    res = facade.assess_environmental_drift(base_imgs, live_imgs)
    tracker.finish("Drift Assessment Complete!", f"Risk Score: {res.risk_score}/100 • Status: {res.status}")

    st.markdown("---")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        {lucide('activity', size=20, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.3rem;">Statistical Drift Summary</h3>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Stream Samples</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8; margin: 4px 0;">{res.total_inspected} Frames</div>
            <span class="status-pill pill-info">{lucide('camera', size=13, color='#38BDF8')} Live Inspection</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        drift_color = '#EF4444' if res.flags_count > 0 else '#10B981'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Feature Drifts</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {drift_color}; margin: 4px 0;">{res.flags_count} Detected</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {lucide('alert-triangle' if res.flags_count > 0 else 'check-circle', size=13, color=drift_color)}
                {'Out of Spec' if res.flags_count > 0 else 'Stable'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        risk_color = '#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')
        risk_label = 'HIGH DRIFT' if res.risk_score > 50 else 'ACCEPTABLE'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Environment Risk Score</div>
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
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Stream Status</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {status_color}; margin: 4px 0;">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else 'pill-danger'}">
                Alpha = 0.01
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"**Audit Summary:** {res.summary}")

    if res.flags:
        st.markdown("#### Dimension-by-Dimension KS Drift Metrics")
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
        st.markdown(render_shadcn_table(drift_data), unsafe_allow_html=True)
    else:
        st.success("Operational stream distribution is statistically consistent with baseline reference data.")
