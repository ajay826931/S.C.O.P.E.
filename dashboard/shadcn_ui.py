# -*- coding: utf-8 -*-
"""
Shadcn/UI Design Component Library & Loading/Progress Controller.
Provides high-fidelity shadcn/ui skeleton loaders, progress bars, process cards,
and cached facade resource management to prevent blank screens during loading.
"""

import streamlit as st
import time
from typing import List, Optional
from dashboard.lucide_icons import lucide
from src.facade import CVAuditorFacade


@st.cache_resource
def get_facade() -> CVAuditorFacade:
    """
    Cached singleton of the CVAuditorFacade.
    Guarantees ML libraries and cryptosystems are loaded once,
    eliminating redundant blank-screen initialization delays.
    """
    return CVAuditorFacade()


def render_skeleton_header(title_width: str = "60%", subtitle_width: str = "85%") -> str:
    """Returns HTML for a shimmering shadcn/ui header skeleton."""
    return f"""
    <div style="margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
            <div class="shadcn-skeleton" style="width: 38px; height: 38px; border-radius: 8px;"></div>
            <div class="shadcn-skeleton" style="width: {title_width}; height: 32px; border-radius: 6px;"></div>
        </div>
        <div class="shadcn-skeleton" style="width: {subtitle_width}; height: 16px; border-radius: 4px;"></div>
    </div>
    """


def render_skeleton_metrics(count: int = 4) -> str:
    """Returns HTML for shimmering shadcn/ui KPI metric card skeletons."""
    cards = []
    for _ in range(count):
        cards.append("""
        <div class="cv-card" style="margin-bottom: 12px;">
            <div class="shadcn-skeleton" style="width: 50%; height: 12px; margin-bottom: 8px; border-radius: 4px;"></div>
            <div class="shadcn-skeleton" style="width: 75%; height: 28px; margin-bottom: 10px; border-radius: 6px;"></div>
            <div class="shadcn-skeleton" style="width: 40%; height: 18px; border-radius: 9999px;"></div>
        </div>
        """)
    return f"""
    <div style="display: grid; grid-template-columns: repeat({count}, 1fr); gap: 16px; margin-bottom: 24px;">
        {''.join(cards)}
    </div>
    """


def render_skeleton_card(height_px: int = 160) -> str:
    """Returns HTML for a general shadcn/ui card skeleton."""
    return f"""
    <div class="cv-card" style="height: {height_px}px; display: flex; flex-direction: column; justify-content: space-around;">
        <div class="shadcn-skeleton" style="width: 40%; height: 18px;"></div>
        <div class="shadcn-skeleton" style="width: 90%; height: 14px;"></div>
        <div class="shadcn-skeleton" style="width: 70%; height: 14px;"></div>
        <div class="shadcn-skeleton" style="width: 30%; height: 24px; border-radius: 6px;"></div>
    </div>
    """


def render_shadcn_process_card(
    title: str,
    subtitle: str = "",
    step: Optional[int] = None,
    total_steps: Optional[int] = None,
    progress_pct: int = 0,
    steps_status: Optional[List[dict]] = None
) -> str:
    """
    Renders a live, premium shadcn/ui progress card with dynamic track,
    Lucide rotating loader, step counter, and completed step badges.
    """
    step_badge = ""
    if step and total_steps:
        step_badge = f"""
        <span class="shadcn-badge shadcn-badge-primary">
            {lucide('activity', size=12, color='#38BDF8')} Step {step}/{total_steps} • {progress_pct}%
        </span>
        """
    else:
        step_badge = f"""
        <span class="shadcn-badge shadcn-badge-primary">
            {lucide('activity', size=12, color='#38BDF8')} {progress_pct}% Complete
        </span>
        """

    # Steps breadcrumbs / pills if provided
    steps_html = ""
    if steps_status:
        chips = []
        for s in steps_status:
            status = s.get("status", "pending")
            name = s.get("name", "")
            if status == "done":
                chips.append(f"""
                <span class="shadcn-badge shadcn-badge-success" style="font-size: 0.72rem; padding: 2px 8px;">
                    {lucide('check', size=11, color='#10B981')} {name}
                </span>
                """)
            elif status == "active":
                chips.append(f"""
                <span class="shadcn-badge shadcn-badge-primary" style="font-size: 0.72rem; padding: 2px 8px; border: 1px solid #38BDF8;">
                    <span class="animate-spin">{lucide('loader-2', size=11, color='#38BDF8')}</span> {name}
                </span>
                """)
            else:
                chips.append(f"""
                <span class="shadcn-badge shadcn-badge-secondary" style="font-size: 0.72rem; padding: 2px 8px; opacity: 0.6;">
                    {lucide('clock', size=11, color='#94A3B8')} {name}
                </span>
                """)
        steps_html = f"""
        <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
            {''.join(chips)}
        </div>
        """

    html = f"""
    <div class="shadcn-loading-card">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span class="animate-spin" style="display: inline-flex; align-items: center;">
                    {lucide('loader-2', size=22, color='#38BDF8')}
                </span>
                <div>
                    <b style="font-size: 1.1rem; color: #F8FAFC; letter-spacing: -0.01em;">{title}</b>
                </div>
            </div>
            {step_badge}
        </div>
        <p style="color: #94A3B8; font-size: 0.88rem; margin: 4px 0 14px 0;">{subtitle}</p>
        <div class="shadcn-progress-track">
            <div class="shadcn-progress-indicator" style="width: {progress_pct}%;"></div>
        </div>
        {steps_html}
    </div>
    """
    return html


class ShadcnProgressTracker:
    """
    Interactive shadcn/ui multi-step execution tracker.
    Updates an in-place Streamlit placeholder container with zero screen blanking.
    """

    def __init__(self, placeholder, step_names: List[str], main_title: str = "Executing Security Verification"):
        self.placeholder = placeholder
        self.step_names = step_names
        self.total_steps = len(step_names)
        self.main_title = main_title
        self.current_step = 1
        self.steps_data = [{"name": name, "status": "pending"} for name in step_names]

    def update(self, step_idx: int, subtitle: str = ""):
        """Advance to step_idx (1-indexed) and update UI immediately."""
        self.current_step = step_idx
        for i, s in enumerate(self.steps_data):
            idx = i + 1
            if idx < step_idx:
                s["status"] = "done"
            elif idx == step_idx:
                s["status"] = "active"
            else:
                s["status"] = "pending"

        pct = int(((step_idx - 1) / self.total_steps) * 100)
        curr_name = self.step_names[step_idx - 1] if step_idx <= self.total_steps else "Processing"
        html = render_shadcn_process_card(
            title=f"{self.main_title} — {curr_name}",
            subtitle=subtitle,
            step=step_idx,
            total_steps=self.total_steps,
            progress_pct=pct,
            steps_status=self.steps_data
        )
        self.placeholder.markdown(html, unsafe_allow_html=True)

    def finish(self, final_title: str = "Execution Complete", final_subtitle: str = "All verification checks passed."):
        """Mark all steps complete with a checkmark banner."""
        for s in self.steps_data:
            s["status"] = "done"

        html = f"""
        <div class="shadcn-loading-card" style="border-color: rgba(16, 185, 129, 0.4);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                    {lucide('check-circle', size=22, color='#10B981')}
                    <b style="font-size: 1.1rem; color: #F8FAFC;">{final_title}</b>
                </div>
                <span class="shadcn-badge shadcn-badge-success">
                    {lucide('check', size=12, color='#10B981')} 100% COMPLETE
                </span>
            </div>
            <p style="color: #94A3B8; font-size: 0.88rem; margin: 4px 0 12px 0;">{final_subtitle}</p>
            <div class="shadcn-progress-track">
                <div class="shadcn-progress-indicator" style="width: 100%; background: #10B981; box-shadow: 0 0 12px rgba(16, 185, 129, 0.5);"></div>
            </div>
            <div style="display: flex; flex-wrap: wrap; gap: 6px; margin-top: 14px; padding-top: 12px; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                {''.join([f'<span class="shadcn-badge shadcn-badge-success" style="font-size: 0.72rem; padding: 2px 8px;">{lucide("check", size=11, color="#10B981")} {s["name"]}</span>' for s in self.steps_data])}
            </div>
        </div>
        """
        self.placeholder.markdown(html, unsafe_allow_html=True)


def render_shadcn_table(records: List[dict], max_rows: int = 50) -> str:
    """
    Renders an official shadcn/ui Table component (https://ui.shadcn.com/docs/components/table).
    Pure HTML/CSS with dark/light theme support, zero external dependencies on pandas/DLLs.
    """
    if not records:
        return """
        <div class="cv-card" style="text-align: center; color: #94A3B8; padding: 24px;">
            No records to display.
        </div>
        """

    headers = list(records[0].keys())
    th_cells = "".join([f'<th>{h}</th>' for h in headers])

    rows_html = []
    for row in records[:max_rows]:
        td_cells = []
        for h in headers:
            val = str(row.get(h, ""))
            if any(term in val for term in ["...", "0x", "SHA", "sha256", "data/"]):
                td_cells.append(f'<td style="font-family: \'JetBrains Mono\', monospace; color: #38BDF8; font-size: 0.82rem;">{val}</td>')
            elif val in ["PASSED", "VERIFIED", "SAFE", "CLEAN", "INTACT", "True"]:
                td_cells.append(f'<td><span class="shadcn-badge shadcn-badge-success">{val}</span></td>')
            elif val in ["FAILED", "FLAGGED", "COMPROMISED", "TAMPER_ATTEMPT_BLOCKED", "False", "High"]:
                td_cells.append(f'<td><span class="status-pill pill-danger">{val}</span></td>')
            else:
                td_cells.append(f'<td>{val}</td>')
        rows_html.append(f'<tr>{"".join(td_cells)}</tr>')

    return f"""
    <div class="shadcn-table-wrapper">
        <table class="shadcn-table">
            <thead>
                <tr>{th_cells}</tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    """

