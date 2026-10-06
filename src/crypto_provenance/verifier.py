"""
Inference Provenance Engine: Cryptographic Verifier.
Verifies digital signatures and detects Man-in-the-Middle (MITM) result tampering.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np

from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature

from src.logger.schemas import FlagReport, SeverityLevel, ModuleType
from src.logger.secure_logger import SecureAuditLogger
from src.crypto_provenance.signer import InferenceSigner


class InferenceVerifier:
    """
    Validates provenance receipts against raw inputs and the auditor's public key.
    """

    def __init__(self, public_key_path: Optional[str] = None, logger: Optional[SecureAuditLogger] = None):
        self.logger = logger or SecureAuditLogger()
        if public_key_path:
            self.public_key_path = Path(public_key_path)
        else:
            base_dir = Path(__file__).resolve().parent.parent.parent
            self.public_key_path = base_dir / "secure_logs" / "keys" / "auditor_public_key.pem"

        self.signer_helper = InferenceSigner()
        self.public_key = self._load_public_key()

    def _load_public_key(self):
        if not self.public_key_path.exists():
            return None
        with open(self.public_key_path, "rb") as f:
            return serialization.load_pem_public_key(f.read())

    def verify_receipt(
        self,
        receipt: Dict[str, Any],
        actual_image: Optional[Any] = None,
        actual_model_hash: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Verifies cryptographic integrity of the receipt.
        Returns: (is_valid, message, audit_details)
        """
        manifest = receipt.get("manifest", {})
        signature_hex = receipt.get("signature_hex", "")

        # Check 1: Image hash integrity (if actual image provided)
        if actual_image is not None:
            actual_img_hash = self.signer_helper.compute_image_hash(actual_image)
            recorded_img_hash = manifest.get("image_sha256", "")
            if actual_img_hash != recorded_img_hash:
                reason = "Image tampering detected! Raw image SHA-256 does not match signed manifest."
                self._log_tamper_attempt("IMAGE_TAMPERING", reason, {
                    "expected": recorded_img_hash,
                    "actual": actual_img_hash
                })
                return False, reason, {"tamper_field": "image", "expected": recorded_img_hash, "actual": actual_img_hash}

        # Check 2: Model hash integrity (if actual model hash provided)
        if actual_model_hash is not None:
            recorded_model_hash = manifest.get("model_sha256", "")
            if actual_model_hash != recorded_model_hash:
                reason = "Model mismatch! Model checkpoint hash differs from signed manifest."
                self._log_tamper_attempt("MODEL_TAMPERING", reason, {
                    "expected": recorded_model_hash,
                    "actual": actual_model_hash
                })
                return False, reason, {"tamper_field": "model", "expected": recorded_model_hash, "actual": actual_model_hash}

        # Check 3: Manifest re-serialization integrity
        canonical_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
        recomputed_manifest_hash = hashlib.sha256(canonical_bytes).hexdigest()
        if recomputed_manifest_hash != receipt.get("manifest_hash"):
            reason = "Manifest tampering detected! Payload content was altered after signing."
            self._log_tamper_attempt("PAYLOAD_TAMPERING", reason, {
                "expected": receipt.get("manifest_hash"),
                "actual": recomputed_manifest_hash
            })
            return False, reason, {"tamper_field": "manifest", "expected": receipt.get("manifest_hash"), "actual": recomputed_manifest_hash}

        # Check 4: RSA Public Key Signature verification
        if self.public_key is None:
            self.public_key = self._load_public_key()
            if self.public_key is None:
                return False, "Public key not found for signature verification.", {}

        try:
            signature_bytes = bytes.fromhex(signature_hex)
            self.public_key.verify(
                signature_bytes,
                canonical_bytes,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
        except (InvalidSignature, ValueError) as e:
            reason = f"Cryptographic signature verification FAILED! Signature does not match public key: {e}"
            self._log_tamper_attempt("SIGNATURE_FORGERY", reason, {"signature": signature_hex})
            return False, reason, {"tamper_field": "signature", "error": str(e)}

        return True, "Provenance signature verified successfully. Input, model, and output are intact.", {
            "image_sha256": manifest.get("image_sha256"),
            "model_sha256": manifest.get("model_sha256"),
            "prediction": manifest.get("prediction"),
            "timestamp": manifest.get("timestamp")
        }

    def _log_tamper_attempt(self, tamper_type: str, reason: str, details: Dict[str, Any]) -> None:
        """Appends alert to the immutable audit ledger."""
        self.logger.log_event(
            module=ModuleType.CRYPTO_PROVENANCE.value,
            event_type="TAMPER_ATTEMPT_BLOCKED",
            payload={
                "tamper_type": tamper_type,
                "reason": reason,
                "details": details
            }
        )
