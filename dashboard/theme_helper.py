# -*- coding: utf-8 -*-
"""
Theme Helper for S.C.O.P.E. Dashboard.
Provides interactive Light / Dark Mode toggling with dynamic CSS injection.
"""

import streamlit as st
from pathlib import Path


def apply_theme():
    """Applies current theme and renders sidebar toggle."""
    if "theme" not in st.session_state:
        st.session_state["theme"] = "Dark"

    with st.sidebar:
        st.markdown("### 🎨 **Display Theme**")
        current_idx = 0 if st.session_state["theme"] == "Dark" else 1
        chosen = st.radio(
            "Select UI Theme",
            ["🌙 Dark Cyber", "☀️ Crisp Light"],
            index=current_idx,
            label_visibility="collapsed",
            key="theme_selector_radio"
        )
        new_theme = "Dark" if "Dark" in chosen else "Light"
        if new_theme != st.session_state["theme"]:
            st.session_state["theme"] = new_theme
            st.rerun()

    # Base stylesheet
    css_path = Path(__file__).resolve().parent / "assets" / "style.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # Dynamic Light Mode injection if active
    if st.session_state["theme"] == "Light":
        light_css = """
        <style>
        /* Light Theme Overrides */
        .stApp {
            background-color: #F8FAFC !important;
            color: #0F172A !important;
        }

        [data-testid="stSidebar"] {
            background-color: #F1F5F9 !important;
            border-right: 1px solid #CBD5E1 !important;
        }

        .cv-card {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(203, 213, 225, 0.8) !important;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06) !important;
            color: #0F172A !important;
        }

        .cv-card:hover {
            border-color: #0284C7 !important;
            box-shadow: 0 8px 25px rgba(2, 132, 199, 0.15) !important;
        }

        h1, h2, h3, h4, h5, h6, p, label {
            color: #0F172A !important;
        }

        small, .subtext {
            color: #475569 !important;
        }

        /* Metric cards */
        [data-testid="stMetricValue"] {
            color: #0F172A !important;
        }
        [data-testid="stMetricLabel"] {
            color: #475569 !important;
        }

        /* Pills in Light Mode */
        .pill-info {
            background: #E0F2FE !important;
            color: #0369A1 !important;
            border: 1px solid #BAE6FD !important;
        }
        .pill-success {
            background: #DCFCE7 !important;
            color: #15803D !important;
            border: 1px solid #BBF7D0 !important;
        }
        .pill-danger {
            background: #FEE2E2 !important;
            color: #B91C1C !important;
            border: 1px solid #FECACA !important;
        }
        .pill-warning {
            background: #FEF3C7 !important;
            color: #B45309 !important;
            border: 1px solid #FDE68A !important;
        }

        /* Code & Pre */
        code, pre {
            background-color: #E2E8F0 !important;
            color: #0F172A !important;
        }

        .gradient-text {
            background: linear-gradient(135deg, #0284C7 0%, #4F46E5 100%) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
        }
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)
