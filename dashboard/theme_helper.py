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
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-sun"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>
            <span style="font-weight: 600; font-size: 0.95rem;">Display Theme</span>
        </div>
        """, unsafe_allow_html=True)
        current_idx = 0 if st.session_state["theme"] == "Dark" else 1
        chosen = st.radio(
            "Select UI Theme",
            ["Dark Cyber", "Crisp Light"],
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

        /* Shadcn Loading & Skeleton in Light Mode */
        .shadcn-skeleton {
            background-color: rgba(15, 23, 42, 0.06) !important;
        }
        .shadcn-skeleton::after {
            background-image: linear-gradient(
                90deg,
                rgba(255, 255, 255, 0) 0,
                rgba(255, 255, 255, 0.4) 20%,
                rgba(255, 255, 255, 0.7) 60%,
                rgba(255, 255, 255, 0)
            ) !important;
        }
        .shadcn-loading-card {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid rgba(2, 132, 199, 0.25) !important;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.05) !important;
            color: #0F172A !important;
        }
        .shadcn-progress-track {
            background-color: rgba(15, 23, 42, 0.08) !important;
        }
        .shadcn-badge-secondary {
            background: #F1F5F9 !important;
            color: #334155 !important;
            border: 1px solid #CBD5E1 !important;
        }
        [data-testid="stStatusWidget"] {
            background: rgba(255, 255, 255, 0.95) !important;
            border: 1px solid #BAE6FD !important;
            color: #0F172A !important;
        }

        /* Shadcn Table in Light Mode */
        .shadcn-table-wrapper {
            background: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05) !important;
        }
        .shadcn-table th {
            background: #F8FAFC !important;
            color: #64748B !important;
            border-bottom: 1px solid #E2E8F0 !important;
        }
        .shadcn-table td {
            color: #0F172A !important;
            border-bottom: 1px solid #F1F5F9 !important;
        }
        .shadcn-table tr:hover td {
            background-color: #F8FAFC !important;
        }
        </style>
        """
        st.markdown(light_css, unsafe_allow_html=True)
