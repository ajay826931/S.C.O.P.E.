"""
Distribution-Shift & Environmental Drift Assessment Engine.
Uses offline two-sample Kolmogorov-Smirnov (KS) tests and computer vision metrics
to calculate environmental divergence and risk scores.
"""

from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import cv2
import numpy as np
from scipy.stats import ks_2samp

from src.logger.schemas import FlagReport, InspectionResult, SeverityLevel, ModuleType
from src.logger.secure_logger import SecureAuditLogger


class DriftAnalyzer:
    """
    Monitors live inference streams against training baseline distributions offline.
    """

    def __init__(self, logger: Optional[SecureAuditLogger] = None):
        self.logger = logger or SecureAuditLogger()

    def extract_visual_features(self, images: List[np.ndarray]) -> Dict[str, np.ndarray]:
        brightness_list = []
        contrast_list = []
        sharpness_list = []
        saturation_list = []

        for img in images:
            if img is None or img.size == 0:
                continue

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV) if img.ndim == 3 else None

            # 1. Brightness
            brightness_list.append(float(np.mean(gray)))

            # 2. Contrast
            contrast_list.append(float(np.std(gray)))

            # 3. Blur / Sharpness (log scale to stabilize variance)
            lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            sharpness_list.append(float(np.log1p(max(0.0, lap_var))))

            # 4. Color Saturation
            sat_val = float(np.mean(hsv[:, :, 1])) if hsv is not None else 0.0
            saturation_list.append(sat_val)

        return {
            "brightness": np.array(brightness_list, dtype=np.float64),
            "contrast": np.array(contrast_list, dtype=np.float64),
            "sharpness": np.array(sharpness_list, dtype=np.float64),
            "saturation": np.array(saturation_list, dtype=np.float64)
        }

    def assess_drift(
        self,
        baseline_images: List[np.ndarray],
        current_images: List[np.ndarray],
        alpha: float = 0.01,
        ks_threshold: float = 0.60
    ) -> InspectionResult:
        """
        Compares baseline distribution vs live operational stream.
        Runs 2-sample Kolmogorov-Smirnov test on each feature vector.
        """
        if len(baseline_images) < 3 or len(current_images) < 3:
            return InspectionResult(
                module=ModuleType.DRIFT_DETECTION,
                status="WARNING",
                total_inspected=len(current_images),
                flags_count=1,
                flags=[FlagReport(
                    module=ModuleType.DRIFT_DETECTION,
                    severity=SeverityLevel.LOW,
                    title="Insufficient Sample Size",
                    description="Batch size too small for statistical hypothesis testing (min 3 required).",
                    target_item="input_batches"
                )],
                risk_score=20.0,
                summary="Insufficient sample size to assess distribution shift."
            )

        base_feats = self.extract_visual_features(baseline_images)
        curr_feats = self.extract_visual_features(current_images)

        flags: List[FlagReport] = []
        feature_weights = {
            "brightness": 1.2,
            "contrast": 1.0,
            "sharpness": 1.5,
            "saturation": 0.8
        }

        weighted_ks_sum = 0.0
        total_weight = sum(feature_weights.values())

        for feat_name, base_arr in base_feats.items():
            curr_arr = curr_feats[feat_name]
            if len(base_arr) == 0 or len(curr_arr) == 0:
                continue

            stat, p_value = ks_2samp(base_arr, curr_arr)
            weighted_ks_sum += stat * feature_weights.get(feat_name, 1.0)

            # Detect genuine distribution shift
            if p_value < alpha and stat >= ks_threshold:
                severity = SeverityLevel.CRITICAL if stat >= 0.85 else SeverityLevel.HIGH
                mean_base = float(np.mean(base_arr))
                mean_curr = float(np.mean(curr_arr))
                direction = "increased" if mean_curr > mean_base else "decreased"

                flag = FlagReport(
                    module=ModuleType.DRIFT_DETECTION,
                    severity=severity,
                    title=f"Significant {feat_name.capitalize()} Drift Detected",
                    description=(
                        f"Distribution of {feat_name} has {direction} significantly. "
                        f"KS-statistic: {stat:.4f}, p-value: {p_value:.4e} (Baseline mean: {mean_base:.1f}, Current: {mean_curr:.1f})."
                    ),
                    target_item=f"feature:{feat_name}",
                    metrics={
                        "feature": feat_name,
                        "ks_statistic": round(float(stat), 4),
                        "p_value": float(p_value),
                        "baseline_mean": round(mean_base, 2),
                        "current_mean": round(mean_curr, 2)
                    }
                )
                flags.append(flag)

        mean_weighted_stat = weighted_ks_sum / total_weight if total_weight > 0 else 0.0
        # If no significant flags triggered, cap risk score below 25
        if not flags:
            risk_score = round(min(20.0, mean_weighted_stat * 25.0), 2)
        else:
            risk_score = round(min(100.0, max(40.0, mean_weighted_stat * 100.0)), 2)

        status = "PASSED"
        if risk_score > 60.0 or any(f.severity == SeverityLevel.CRITICAL for f in flags):
            status = "FAILED"
        elif risk_score > 25.0 or any(f.severity == SeverityLevel.HIGH for f in flags):
            status = "WARNING"

        summary = (
            f"Drift assessment complete: Compared {len(current_images)} live samples against {len(baseline_images)} baseline samples. "
            f"Detected {len(flags)} distribution anomalies. Status: {status} (Environmental Risk Score: {risk_score}/100)."
        )

        result = InspectionResult(
            module=ModuleType.DRIFT_DETECTION,
            status=status,
            total_inspected=len(current_images),
            flags_count=len(flags),
            flags=flags,
            risk_score=risk_score,
            summary=summary
        )

        self.logger.log_event(
            module=ModuleType.DRIFT_DETECTION.value,
            event_type="DRIFT_ASSESSMENT_COMPLETED",
            payload={
                "baseline_count": len(baseline_images),
                "live_count": len(current_images),
                "risk_score": risk_score,
                "status": status,
                "flags_count": len(flags),
                "summary": summary
            }
        )

        return result
