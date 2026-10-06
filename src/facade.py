"""
CVAuditorFacade: Unified Entry Point implementing the Facade Pattern.
Orchestrates all 5 CV-Sec modules under a clean, unified API for the UI and CLI.
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np

from src.logger.schemas import InspectionResult, FlagReport, ModuleType
from src.logger.secure_logger import SecureAuditLogger
from src.data_integrity.scanner import DataIntegrityScanner
from src.model_integrity.backdoor_detector import BackdoorDetector
from src.model_integrity.fallback_handler import load_model_adapter
from src.crypto_provenance.signer import InferenceSigner
from src.crypto_provenance.verifier import InferenceVerifier
from src.drift_detection.drift_analyzer import DriftAnalyzer


class CVAuditorFacade:
    """
    Master Auditor Facade. The single interface coordinating:
    1. Training Data Integrity
    2. Model Integrity & Trojan Detection
    3. Inference Provenance (Cryptographic Signing & Verifying)
    4. Distribution-Shift / Drift Assessment
    5. Immutable Hash-Chained Audit Logging
    """

    def __init__(self, log_path: Optional[str] = None):
        self.logger = SecureAuditLogger(log_path)
        self.data_scanner = DataIntegrityScanner(logger=self.logger)
        self.backdoor_detector = BackdoorDetector(logger=self.logger)
        self.signer = InferenceSigner()
        self.verifier = InferenceVerifier(logger=self.logger)
        self.drift_analyzer = DriftAnalyzer(logger=self.logger)

    # 1. Training-Data Integrity
    def audit_training_data(self, dataset_path: str) -> InspectionResult:
        """Runs full integrity scan on a YOLO/COCO dataset directory."""
        return self.data_scanner.scan(dataset_path)

    # 2. Model Integrity
    def audit_model(
        self,
        model_path: str,
        test_images: Optional[np.ndarray] = None
    ) -> InspectionResult:
        """Audits a PyTorch (.pt) or ONNX (.onnx) model for hidden Trojans."""
        return self.backdoor_detector.audit_model(model_path, test_images=test_images)

    # 3. Inference Provenance
    def sign_inference(
        self,
        image_data: Any,
        model_path: str,
        prediction: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Binds [Image + Model Hash + Prediction] into an RSA digital signature."""
        adapter = load_model_adapter(model_path)
        return self.signer.sign_inference(image_data, adapter.model_hash, prediction)

    def verify_provenance(
        self,
        receipt: Dict[str, Any],
        actual_image: Optional[Any] = None,
        model_path: Optional[str] = None
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """Validates receipt signature and checks against MITM tampering."""
        actual_model_hash = None
        if model_path:
            adapter = load_model_adapter(model_path)
            actual_model_hash = adapter.model_hash

        return self.verifier.verify_receipt(
            receipt=receipt,
            actual_image=actual_image,
            actual_model_hash=actual_model_hash
        )

    # 4. Distribution-Shift Assessment
    def assess_environmental_drift(
        self,
        baseline_images: List[np.ndarray],
        current_images: List[np.ndarray]
    ) -> InspectionResult:
        """Compares baseline vs live stream distributions via KS-testing."""
        return self.drift_analyzer.assess_drift(baseline_images, current_images)

    # 5. Immutable Audit Trail
    def verify_audit_trail_integrity(self) -> Tuple[bool, str, Optional[int]]:
        """Audits the cryptographic SHA-256 hash chain for tampering."""
        return self.logger.verify_integrity()

    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Fetches all logged immutable audit events."""
        return self.logger.get_logs()
