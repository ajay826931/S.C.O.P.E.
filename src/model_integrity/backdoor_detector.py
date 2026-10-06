"""
Model Integrity & Backdoor/Trojan Detection Engine.
Performs black-box trigger inversion and adversarial perturbation checks offline.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from src.logger.schemas import FlagReport, InspectionResult, SeverityLevel, ModuleType
from src.logger.secure_logger import SecureAuditLogger
from src.model_integrity.fallback_handler import BaseModelAdapter, load_model_adapter


class BackdoorDetector:
    """
    Evaluates pre-trained models for Trojans/Backdoors using localized perturbation
    and trigger sensitivity analysis without requiring model retraining.
    """

    def __init__(self, logger: Optional[SecureAuditLogger] = None):
        self.logger = logger or SecureAuditLogger()

    def _generate_synthetic_baseline(self, shape: Tuple[int, ...], count: int = 12) -> np.ndarray:
        """
        Generates diverse baseline inputs for black-box testing.
        Normalized to standard [0.0, 1.0] range.
        """
        full_shape = (count,) + shape[1:]
        rng = np.random.default_rng(42)
        samples = np.full(full_shape, 0.25, dtype=np.float32)

        # Introduce channel and quadrant diversity across images so baseline predictions vary
        is_nchw = (len(shape) == 4 and shape[1] in [1, 3])
        for i in range(count):
            target_ch = i % 3
            if is_nchw:
                samples[i, target_ch] += 0.35
                samples[i] += rng.uniform(-0.05, 0.05, size=samples[i].shape).astype(np.float32)
            else:
                samples[i, ..., target_ch] += 0.35
                samples[i] += rng.uniform(-0.05, 0.05, size=samples[i].shape).astype(np.float32)

        return np.clip(samples, 0.0, 1.0)

    def _inject_trigger_patch(
        self,
        image_batch: np.ndarray,
        location: str = "top_left",
        patch_size: int = 8,
        trigger_type: str = "solid"
    ) -> np.ndarray:
        """Applies a candidate trigger pattern onto a batch of images."""
        batch = image_batch.copy()
        is_nchw = (batch.ndim == 4 and batch.shape[1] in [1, 3])

        b_size = batch.shape[0]
        h = batch.shape[2] if is_nchw else batch.shape[1]
        w = batch.shape[3] if is_nchw else batch.shape[2]

        ps = min(patch_size, max(2, min(h, w) // 4))

        if location == "top_left":
            r_start, c_start = 0, 0
        elif location == "top_right":
            r_start, c_start = 0, w - ps
        elif location == "bottom_left":
            r_start, c_start = h - ps, 0
        else:  # bottom_right
            r_start, c_start = h - ps, w - ps

        # Create trigger pattern
        pattern = np.ones((ps, ps), dtype=np.float32)
        if trigger_type == "checkerboard":
            pattern[::2, ::2] = 0.0
            pattern[1::2, 1::2] = 0.0

        for i in range(b_size):
            if is_nchw:
                for c in range(batch.shape[1]):
                    batch[i, c, r_start:r_start+ps, c_start:c_start+ps] = pattern
            else:
                for c in range(batch.shape[-1]):
                    batch[i, r_start:r_start+ps, c_start:c_start+ps] = pattern

        return batch

    def audit_model(
        self,
        model_source: Any,
        test_images: Optional[np.ndarray] = None
    ) -> InspectionResult:
        """
        Executes black-box Trojan analysis across multiple trigger candidates.
        """
        if isinstance(model_source, str) or isinstance(model_source, Path):
            adapter = load_model_adapter(str(model_source))
        else:
            adapter = model_source

        shape = adapter.get_input_shape()

        if test_images is None:
            test_batch = self._generate_synthetic_baseline(shape, count=12)
        else:
            test_batch = test_images

        # 1. Clean Baseline Prediction
        clean_preds = adapter.predict(test_batch)
        clean_classes = np.argmax(clean_preds, axis=-1)

        candidate_locations = ["top_left", "top_right", "bottom_left", "bottom_right"]
        candidate_triggers = ["solid", "checkerboard"]

        flags: List[FlagReport] = []
        highest_asr = 0.0

        for loc in candidate_locations:
            for trig in candidate_triggers:
                perturbed_batch = self._inject_trigger_patch(
                    test_batch, location=loc, patch_size=8, trigger_type=trig
                )
                perturbed_preds = adapter.predict(perturbed_batch)
                perturbed_classes = np.argmax(perturbed_preds, axis=-1)

                flips = np.sum(perturbed_classes != clean_classes)
                flip_rate = float(flips) / float(len(clean_classes))

                unique_classes, counts = np.unique(perturbed_classes, return_counts=True)
                dominant_count = counts.max()
                convergence_rate = float(dominant_count) / float(len(perturbed_classes))
                target_class = int(unique_classes[np.argmax(counts)])

                # Alert if high percentage flip and converge to the SAME target class
                if flip_rate >= 0.50 and convergence_rate >= 0.75:
                    severity = SeverityLevel.CRITICAL if flip_rate >= 0.80 else SeverityLevel.HIGH
                    flag = FlagReport(
                        module=ModuleType.MODEL_INTEGRITY,
                        severity=severity,
                        title="Potential Backdoor/Trojan Detected",
                        description=(
                            f"Model exhibits severe sensitivity to {trig} trigger at {loc}. "
                            f"{flips}/{len(clean_classes)} samples flipped to Target Class {target_class} "
                            f"(Attack Success Rate: {flip_rate*100:.1f}%, Convergence: {convergence_rate*100:.1f}%)."
                        ),
                        target_item=f"{adapter.model_path.name} @ {loc}:{trig}",
                        metrics={
                            "trigger_location": loc,
                            "trigger_type": trig,
                            "target_class": target_class,
                            "attack_success_rate": round(flip_rate, 4),
                            "convergence_rate": round(convergence_rate, 4),
                            "model_sha256": adapter.model_hash
                        }
                    )
                    flags.append(flag)

                    if flip_rate > highest_asr:
                        highest_asr = flip_rate

        risk_score = round(highest_asr * 100.0, 2)
        status = "PASSED"
        if any(f.severity == SeverityLevel.CRITICAL for f in flags):
            status = "FAILED"
        elif any(f.severity == SeverityLevel.HIGH for f in flags):
            status = "WARNING"

        summary = (
            f"Model integrity audit complete for {adapter.model_path.name}. "
            f"Checkpoint SHA-256: {adapter.model_hash[:16]}... "
            f"Detected {len(flags)} backdoor vulnerability indicators. "
            f"Status: {status} (Trojan Risk Score: {risk_score}/100)."
        )

        result = InspectionResult(
            module=ModuleType.MODEL_INTEGRITY,
            status=status,
            total_inspected=len(candidate_locations) * len(candidate_triggers),
            flags_count=len(flags),
            flags=flags,
            risk_score=risk_score,
            summary=summary
        )

        self.logger.log_event(
            module=ModuleType.MODEL_INTEGRITY.value,
            event_type="MODEL_SCAN_COMPLETED",
            payload={
                "model_name": adapter.model_path.name,
                "model_hash": adapter.model_hash,
                "risk_score": risk_score,
                "status": status,
                "flags_count": len(flags),
                "summary": summary
            }
        )

        return result
