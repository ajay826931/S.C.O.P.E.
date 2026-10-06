"""
Inference Provenance Engine: Cryptographic Signer.
Digitally binds [Image Hash + Model Hash + Inference Result] into an unforgeable signature.
"""

import os
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, Any, Tuple, Optional
import numpy as np

from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization


class InferenceSigner:
    """
    Manages local cryptographic keypairs and signs inference manifests.
    """

    def __init__(self, key_dir: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.key_dir = Path(key_dir) if key_dir else base_dir / "secure_logs" / "keys"
        self.key_dir.mkdir(parents=True, exist_ok=True)

        self.private_key_path = self.key_dir / "auditor_private_key.pem"
        self.public_key_path = self.key_dir / "auditor_public_key.pem"

        self.private_key, self.public_key = self._load_or_generate_keys()

    def _load_or_generate_keys(self) -> Tuple[rsa.RSAPrivateKey, rsa.RSAPublicKey]:
        """Loads existing RSA keypair or generates a fresh 2048-bit pair."""
        if self.private_key_path.exists() and self.public_key_path.exists():
            try:
                with open(self.private_key_path, "rb") as f:
                    private_key = serialization.load_pem_private_key(f.read(), password=None)
                with open(self.public_key_path, "rb") as f:
                    public_key = serialization.load_pem_public_key(f.read())
                return private_key, public_key
            except Exception:
                pass

        # Generate new RSA key
        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = private_key.public_key()

        # Save private key
        pem_priv = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(self.private_key_path, "wb") as f:
            f.write(pem_priv)

        # Save public key
        pem_pub = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(self.public_key_path, "wb") as f:
            f.write(pem_pub)

        return private_key, public_key

    def compute_image_hash(self, image_data: Any) -> str:
        """Computes deterministic SHA-256 hash of image pixels or file bytes."""
        if isinstance(image_data, (str, Path)):
            sha = hashlib.sha256()
            with open(image_data, "rb") as f:
                while chunk := f.read(65536):
                    sha.update(chunk)
            return sha.hexdigest()
        elif isinstance(image_data, np.ndarray):
            return hashlib.sha256(image_data.tobytes()).hexdigest()
        elif isinstance(image_data, bytes):
            return hashlib.sha256(image_data).hexdigest()
        else:
            return hashlib.sha256(str(image_data).encode("utf-8")).hexdigest()

    def sign_inference(
        self,
        image_data: Any,
        model_hash: str,
        prediction_payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Cryptographically binds image, model checkpoint, and inference output.
        Returns verifiable Provenance Receipt dictionary.
        """
        image_hash = self.compute_image_hash(image_data)
        timestamp = time.time()

        manifest = {
            "timestamp": timestamp,
            "image_sha256": image_hash,
            "model_sha256": model_hash,
            "prediction": prediction_payload
        }

        # Canonical JSON string
        canonical_bytes = json.dumps(manifest, sort_keys=True).encode("utf-8")
        manifest_hash = hashlib.sha256(canonical_bytes).hexdigest()

        # Sign manifest hash with RSA Private Key (PSS padding + SHA256)
        signature = self.private_key.sign(
            canonical_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        receipt = {
            "manifest": manifest,
            "manifest_hash": manifest_hash,
            "signature_hex": signature.hex(),
            "public_key_path": str(self.public_key_path)
        }

        return receipt
