"""
Streamlit Page 1: Training-Data Integrity Engine.
Audits YOLO/COCO formatted datasets for duplicates, corruptions, and poisoned annotations.
"""

import streamlit as st
from pathlib import Path
import sys
import pandas as pd
import numpy as np
import cv2

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.facade import CVAuditorFacade

st.set_page_config(page_title="CV-Sec | Data Integrity", page_icon="📦", layout="wide")

# Load CSS
css_path = root_dir / "dashboard" / "assets" / "style.css"
if css_path.exists():
    with open(css_path, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown("""
<div>
    <h1 style="margin: 0;">📦 <span class="gradient-text">Training-Data Integrity Scanner</span></h1>
    <p style="color: #94A3B8; font-size: 1.05rem;">
        Automated algorithmic inspection for YOLO/COCO datasets: duplicate flood detection, bounding box outliers, and pixel corruption.
    </p>
</div>
""", unsafe_allow_html=True)

facade = CVAuditorFacade()

col_input, col_preset = st.columns([2, 1])

with col_preset:
    preset = st.selectbox(
        "⚡ Choose Dataset Scenario:",
        [
            "data/poisoned_data (Injected Poison Attack Demo)",
            "data/clean_data (Verified Reference Dataset)"
        ]
    )
    chosen_path = preset.split()[0]

with col_input:
    dataset_path = st.text_input("Dataset Directory Path:", value=chosen_path)

if st.button("🚀 Run Comprehensive Dataset Audit", type="primary", use_container_width=True):
    with st.spinner("Executing SSIM duplicate detection, bounding box outlier analysis, and pixel variance tests..."):
        res = facade.audit_training_data(dataset_path)

    st.markdown("---")
    st.markdown("### 📊 **Audit Summary & Threat Metrics**")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">TOTAL INSPECTED</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8;">{res.total_inspected} Images</div>
            <span class="status-pill pill-info">YOLO / COCO</span>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">FLAGS DETECTED</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.flags_count > 0 else '#10B981'};">{res.flags_count} Issues</div>
            <span class="status-pill {'pill-danger' if res.flags_count > 0 else 'pill-success'}">
                {'⚠️ Anomalies' if res.flags_count > 0 else '✅ Clean'}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">DATASET RISK SCORE</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#EF4444' if res.risk_score > 50 else ('#F59E0B' if res.risk_score > 20 else '#10B981')};">
                {res.risk_score} <span style="font-size: 1rem; color: #94A3B8;">/ 100</span>
            </div>
            <span class="status-pill {'pill-danger' if res.risk_score > 50 else ('pill-warning' if res.risk_score > 20 else 'pill-success')}">
                {'HIGH RISK' if res.risk_score > 50 else ('ELEVATED' if res.risk_score > 20 else 'LOW RISK')}
            </span>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="cv-card">
            <div style="font-size: 0.8rem; color: #94A3B8;">AUDIT RESULT</div>
            <div style="font-size: 1.8rem; font-weight: 700; color: {'#10B981' if res.status == 'PASSED' else ('#F59E0B' if res.status == 'WARNING' else '#EF4444')};">
                {res.status}
            </div>
            <span class="status-pill {'pill-success' if res.status == 'PASSED' else ('pill-warning' if res.status == 'WARNING' else 'pill-danger')}">
                Cryptographically Logged
            </span>
        </div>
        """, unsafe_allow_html=True)

    st.info(f"📋 **Summary:** {res.summary}")

    # Interactive Tab View
    tab1, tab2, tab3 = st.tabs(["⚠️ Flagged Anomalies & Security Events", "🖼️ Visual Image & Annotation Inspector", "🔬 Strategy Breakdown"])

    with tab1:
        if res.flags:
            st.markdown("#### 🚨 Detailed Attack Vectors & Corruption Events")
            table_records = []
            for f in res.flags:
                sev_icon = "🔴" if f.severity.value == "CRITICAL" else ("🟠" if f.severity.value == "HIGH" else "🟡")
                table_records.append({
                    "Level": f"{sev_icon} {f.severity.value}",
                    "Vulnerability": f.title,
                    "Target File / Item": f.target_item,
                    "Technical Details": f.description
                })
            st.dataframe(pd.DataFrame(table_records), use_container_width=True)
        else:
            st.success("🎉 No vulnerabilities or anomalies detected! The dataset conforms to safe YOLO standards.")

    with tab2:
        st.markdown("#### 🖼️ Image Files & Bounding Box Inspection")
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
        #### ⚙️ Active Algorithmic Defense Strategies
        - **1. Structural Similarity Index (SSIM):** Compares perceptual representations to identify duplicate dataset floods without computational bottleneck.
        - **2. Bounding Box Boundary Strategy:** Enforces normalized $[0.0, 1.0]$ ranges, flags negative class IDs, and detects extreme aspect ratio corruptions.
        - **3. Pixel Variance Strategy:** Tests for uniform frames, camera sensor dropouts, or solid-color blank attacks.
        """)
