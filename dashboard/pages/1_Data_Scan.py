# -*- coding: utf-8 -*-
"""
Streamlit Page 1: Training-Data Integrity Engine.
Audits YOLO/COCO formatted datasets for duplicates, corruptions, and poisoned annotations.
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

st.set_page_config(page_title="CV-Sec | Data Integrity", page_icon="📦", layout="wide")

# Apply Dynamic Light / Dark Theme
apply_theme()

st.markdown(f"""
<div style="margin-bottom: 20px;">
    <div style="display: flex; align-items: center; gap: 10px;">
        {lucide('database', size=32, color='#38BDF8')}
        <h1 style="margin: 0; font-size: 2.2rem;">
            <span class="gradient-text">Training-Data Integrity Scanner</span>
        </h1>
    </div>
    <p style="color: #94A3B8; font-size: 1.05rem; margin-top: 6px;">
        Automated algorithmic inspection for YOLO/COCO datasets: duplicate flood detection, bounding box outliers, and pixel corruption.
    </p>
</div>
""", unsafe_allow_html=True)

facade = get_facade()

col_input, col_preset = st.columns([2, 1])

with col_preset:
    preset = st.selectbox(
        "Choose Dataset Scenario:",
        [
            "data/poisoned_data (Injected Poison Attack Vector)",
            "data/clean_data (Verified Reference Dataset)"
        ]
    )
    chosen_path = preset.split()[0]

with col_input:
    dataset_path = st.text_input("Dataset Directory Path:", value=chosen_path)

if st.button("Run Comprehensive Dataset Audit", type="primary", use_container_width=True):
    progress_ph = st.empty()
    tracker = ShadcnProgressTracker(
        progress_ph,
        step_names=[
            "Index & Coordinate Check",
            "SSIM Perceptual Hash Duplicate Audit",
            "Pixel Variance & Outlier Extraction"
        ],
        main_title="Dataset Integrity Scanner"
    )

    tracker.update(1, "Indexing YOLO/COCO bounding boxes and checking class labels...")
    time.sleep(0.15)
    tracker.update(2, "Computing Structural Similarity Index (SSIM) and identifying duplicate floods...")
    res = facade.audit_training_data(dataset_path)
    tracker.update(3, "Evaluating pixel variance distribution across bounding boxes...")
    time.sleep(0.15)
    tracker.finish("Dataset Audit Complete!", f"Inspected {res.total_inspected} images. Status: {res.status}")

    st.markdown("---")
    st.markdown(f"""
    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
        {lucide('activity', size=20, color='#38BDF8')}
        <h3 style="margin: 0; font-size: 1.3rem;">Audit Summary & Threat Metrics</h3>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Total Inspected</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8; margin: 4px 0;">{res.total_inspected} Images</div>
            <span class="status-pill pill-info">{lucide('box', size=13, color='#38BDF8')} YOLO / COCO</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        flag_color = '#EF4444' if res.flags_count > 0 else '#10B981'
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Flags Detected</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {flag_color}; margin: 4px 0;">{res.flags_count} Issues</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {lucide('alert-triangle' if res.flags_count > 0 else 'check-circle', size=13, color=flag_color)}
                {'Anomalies Found' if res.flags_count > 0 else 'Dataset Clean'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        risk_color = '#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')
        risk_label = 'HIGH RISK' if res.risk_score > 50 else ('ELEVATED' if res.risk_score > 20 else 'LOW RISK')
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Dataset Risk Score</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {risk_color}; margin: 4px 0;">
                {res.risk_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
            </div>
            <span class="status-pill {'pill-danger' if res.risk_score > 50 else ('pill-warning' if res.risk_score > 20 else 'pill-success')}">
                {lucide('gauge', size=13, color=risk_color)} {risk_label}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        status_color = '#10B981' if res.status == 'PASSED' else ('#F59E0B' if res.status == 'WARNING' else '#EF4444')
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8; text-transform: uppercase;">Audit Result</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {status_color}; margin: 4px 0;">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else ('pill-warning' if res.status == 'WARNING' else 'pill-danger')}">
                {lucide('link', size=13, color=status_color)} Cryptographically Logged
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"**Audit Summary:** {res.summary}")

    # Interactive Tab View
    tab1, tab2, tab3 = st.tabs(["Flagged Security Events", "Visual Image & Bounding Box Inspector", "Strategy Architecture"])

    with tab1:
        if res.flags:
            st.markdown("#### Detailed Attack Vectors & Corruption Events")
            table_records = []
            for f in res.flags:
                table_records.append({
                    "Level": f.severity.value,
                    "Vulnerability": f.title,
                    "Target File / Item": f.target_item,
                    "Technical Details": f.description
                })
            st.markdown(render_shadcn_table(table_records), unsafe_allow_html=True)
        else:
            st.success("No vulnerabilities or anomalies detected! The dataset conforms to safe YOLO standards.")

    with tab2:
        st.markdown("#### Image Files & Bounding Box Inspection")
        p = Path(dataset_path)
        img_files = list(p.glob("*.png")) + list(p.glob("*.jpg"))
        if img_files:
            cols = st.columns(min(3, len(img_files)))
            for idx, img_p in enumerate(img_files[:6]):
                with cols[idx % 3]:
                    img_mat = cv2.imread(str(img_p))
                    if img_mat is not None:
                        # Draw bounding boxes if valid label exists
                        lbl_p = img_p.with_suffix(".txt")
                        lbl_text = ""
                        if lbl_p.exists():
                            with open(lbl_p, "r", encoding="utf-8") as lf:
                                lbl_text = lf.read().strip()
                            h, w, _ = img_mat.shape
                            # Draw lines for boxes
                            for line in lbl_text.splitlines():
                                parts = line.split()
                                if len(parts) >= 5:
                                    try:
                                        cid = int(parts[0])
                                        xc = float(parts[1]) * w
                                        yc = float(parts[2]) * h
                                        bw = float(parts[3]) * w
                                        bh = float(parts[4]) * h
                                        x1, y1 = int(xc - bw/2), int(yc - bh/2)
                                        x2, y2 = int(xc + bw/2), int(yc + bh/2)
                                        cv2.rectangle(img_mat, (x1, y1), (x2, y2), (0, 255, 0) if cid >= 0 else (0, 0, 255), 2)
                                    except Exception:
                                        pass

                        img_rgb = cv2.cvtColor(img_mat, cv2.COLOR_BGR2RGB)
                        st.image(img_rgb, caption=img_p.name, use_container_width=True)
                        if lbl_text:
                            with st.expander(f"View Annotation: {lbl_p.name}"):
                                st.code(lbl_text, language="text")
        else:
            st.warning("No image files (.png, .jpg) found in the selected folder.")

    with tab3:
        st.markdown("""
        #### Active Algorithmic Defense Strategies
        - **1. Structural Similarity Index (SSIM):** Compares perceptual representations to identify duplicate dataset floods without computational bottleneck.
        - **2. Bounding Box Boundary Strategy:** Enforces normalized $[0.0, 1.0]$ ranges, flags negative class IDs, and detects extreme aspect ratio corruptions.
        - **3. Pixel Variance Strategy:** Tests for uniform frames, camera sensor dropouts, or solid-color blank attacks.
        """)
