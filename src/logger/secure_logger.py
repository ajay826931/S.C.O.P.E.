"""
Immutable Hash-Chained Audit Logger for Antigravity CV-Sec Framework.
Provides air-gapped, append-only cryptographic logging with tamper detection.
"""

import os
import json
import hashlib
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path


class SecureAuditLogger:
    """
    Manages an append-only JSON ledger where each entry is cryptographically
    linked to the previous entry via SHA-256 hashing.
    """

    GENESIS_PREV_HASH = "0" * 64

    def __init__(self, log_path: Optional[str] = None):
        if log_path is None:
            # Default to secure_logs/system_audit_trail.json
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.log_path = base_dir / "secure_logs" / "system_audit_trail.json"
        else:
            self.log_path = Path(log_path)

        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_log_file()

    def _ensure_log_file(self) -> None:
        """Initializes empty ledger if not already present."""
        if not self.log_path.exists() or self.log_path.stat().st_size == 0:
            with open(self.log_path, "w", encoding="utf-8") as f:
                json.dump([], f, indent=2)

    def _calculate_hash(
        self,
        index: int,
        timestamp: str,
        module: str,
        event_type: str,
        payload: Dict[str, Any],
        prev_hash: str
    ) -> str:
        """Computes deterministic SHA-256 hash over block contents."""
        serialized_payload = json.dumps(payload, sort_keys=True)
        block_string = f"{index}|{timestamp}|{module}|{event_type}|{serialized_payload}|{prev_hash}"
        return hashlib.sha256(block_string.encode("utf-8")).hexdigest()

    def _read_entries(self) -> List[Dict[str, Any]]:
        """Reads all entries from disk safely."""
        self._ensure_log_file()
        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    def _write_entries(self, entries: List[Dict[str, Any]]) -> None:
        """Atomic write to disk."""
        temp_path = self.log_path.with_suffix(".tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(entries, f, indent=2)
        os.replace(temp_path, self.log_path)

    def log_event(
        self,
        module: str,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Appends a new cryptographically chained audit event.
        """
        entries = self._read_entries()

        index = len(entries)
        timestamp = datetime.now(timezone.utc).isoformat()
        prev_hash = entries[-1]["current_hash"] if entries else self.GENESIS_PREV_HASH

        current_hash = self._calculate_hash(
            index=index,
            timestamp=timestamp,
            module=module,
            event_type=event_type,
            payload=payload,
            prev_hash=prev_hash
        )

        entry = {
            "index": index,
            "timestamp": timestamp,
            "module": module,
            "event_type": event_type,
            "payload": payload,
            "prev_hash": prev_hash,
            "current_hash": current_hash
        }

        entries.append(entry)
        self._write_entries(entries)
        return entry

    def verify_integrity(self) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Audits the entire hash chain from genesis to head.
        Returns:
            (is_valid, error_message, compromised_index)
        """
        entries = self._read_entries()

        if not entries:
            return True, "Audit log is empty (clean state).", None

        for i, entry in enumerate(entries):
            # Check 1: Sequence index
            if entry.get("index") != i:
                return False, f"Broken index sequence at position {i}. Found {entry.get('index')}", i

            # Check 2: Prev-hash linkage
            expected_prev = entries[i - 1]["current_hash"] if i > 0 else self.GENESIS_PREV_HASH
            if entry.get("prev_hash") != expected_prev:
                return False, f"Hash-chain break at index {i}: prev_hash mismatch. Expected {expected_prev}, found {entry.get('prev_hash')}", i

            # Check 3: Recompute current hash
            recomputed_hash = self._calculate_hash(
                index=entry["index"],
                timestamp=entry["timestamp"],
                module=entry["module"],
                event_type=entry["event_type"],
                payload=entry["payload"],
                prev_hash=entry["prev_hash"]
            )

            if entry.get("current_hash") != recomputed_hash:
                return False, f"Tampered record detected at index {i}! Hash recomputation mismatch.", i

        return True, f"Audit chain verified successfully ({len(entries)} entries intact).", None

    def get_logs(self) -> List[Dict[str, Any]]:
        """Returns all entries."""
        return self._read_entries()
