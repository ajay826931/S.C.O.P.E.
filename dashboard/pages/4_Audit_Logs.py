"""
Streamlit Page 4: Immutable Audit Trail & Cryptographic Hash-Chain Ledger.
Displays append-only cryptographic logs and allows 1-click integrity verification.
"""

import streamlit as st
from pathlib import Path
import sys
import json
import pandas as pd

root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.facade import CVAuditorFacade
from dashboard.theme_helper import apply_theme

st.set_page_config(page_title="CV-Sec | Audit Ledger", page_icon="📜", layout="wide")

# Apply Dynamic Light / Dark Theme
apply_theme()

st.markdown("""
<div>
    <h1 style="margin: 0;">📜 <span class="gradient-text">Immutable Audit Ledger & Hash-Chain Visualizer</span></h1>
    <p style="color: #94A3B8; font-size: 1.05rem;">
        Append-only local blockchain JSON ledger. Every security event is chained via <code>SHA256(index | timestamp | payload | prev_hash)</code> ensuring zero undetected tampering.
    </p>
</div>
""", unsafe_allow_html=True)

facade = CVAuditorFacade()
log_file = root_dir / "secure_logs" / "system_audit_trail.json"

c_act1, c_act2, c_act3 = st.columns([1, 1, 1])

with c_act1:
    verify_clicked = st.button("🔒 Verify Ledger Integrity", type="primary", use_container_width=True)

with c_act2:
    tamper_demo = st.button("⚠️ Simulate Attack on Past Block", use_container_width=True)

with c_act3:
    restore_btn = st.button("🔄 Reset to Clean Ledger State", use_container_width=True)

if tamper_demo:
    if log_file.exists():
        with open(log_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if len(data) > 0:
            target = len(data) // 2
            data[target]["payload"]["MALICIOUS_MODIFICATION"] = "ATTACKER_ALTERED_RECORDS"
            with open(log_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            st.warning(f"⚠️ Simulated Attack: Modified Block #{target} payload without updating hash chain.")

if restore_btn:
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump([], f, indent=2)
    facade.logger.log_event("SYSTEM", "LEDGER_INITIALIZED", {"message": "Admin initialized fresh audit trail."})
    st.success("Ledger reset to clean genesis state.")

# Cryptographic chain verification
is_valid, msg, broken_idx = facade.verify_audit_trail_integrity()

logs = facade.get_audit_trail()

st.markdown("---")
# Ledger Status Card
col_stat1, col_stat2, col_stat3 = st.columns(3)

with col_stat1:
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.8rem; color: #94A3B8;">LEDGER INTEGRITY</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: {'#10B981' if is_valid else '#EF4444'};">
            {'VERIFIED INTACT' if is_valid else 'CORRUPTED'}
        </div>
        <span class="status-pill {'pill-success' if is_valid else 'pill-danger'}">
            {'✅ Hash Chain Valid' if is_valid else f'🚨 Break at Block #{broken_idx}'}
        </span>
    </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.8rem; color: #94A3B8;">TOTAL CHAIN HEIGHT</div>
        <div style="font-size: 1.8rem; font-weight: 700; color: #38BDF8;">
            {len(logs)} BLOCKS
        </div>
        <span class="status-pill pill-info">Append-Only JSON</span>
    </div>
    """, unsafe_allow_html=True)

with col_stat3:
    genesis_str = logs[0]["current_hash"][:16] + "..." if logs else "GENESIS_PENDING"
    st.markdown(f"""
    <div class="cv-card">
        <div style="font-size: 0.8rem; color: #94A3B8;">GENESIS FINGERPRINT</div>
        <div style="font-size: 1.3rem; font-weight: 600; color: #818CF8; margin: 6px 0;">
            <code>{genesis_str}</code>
        </div>
        <span class="status-pill pill-info">Immutable Anchor</span>
    </div>
    """, unsafe_allow_html=True)

if not is_valid:
    st.error(f"🚨 **SECURITY ALERT**: Hash-chain verification failed! {msg}. Forensic investigation required.")
else:
    st.success(f"🔒 {msg}")

st.markdown("### 🧱 **Interactive Block Explorer**")

if logs:
    records = []
    for entry in reversed(logs):
        records.append({
            "Block #": entry.get("index"),
            "Timestamp": entry.get("timestamp"),
            "Module": entry.get("module"),
            "Event Type": entry.get("event_type"),
            "Current Block Hash": entry.get("current_hash", "")[:24] + "...",
            "Previous Block Hash": entry.get("prev_hash", "")[:24] + "..."
        })
    st.dataframe(pd.DataFrame(records), use_container_width=True)

    with st.expander("🔍 Deep-Inspect Specific Block Payload"):
        sel_idx = st.number_input("Select Block Index:", min_value=0, max_value=len(logs)-1, value=len(logs)-1)
        st.json(logs[sel_idx])
else:
    st.info("Audit log is currently empty.")
