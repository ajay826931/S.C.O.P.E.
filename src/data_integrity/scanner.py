"""
Data Integrity Scanner orchestrating the Strategy Pattern.
Executes dataset scans and reports findings to the Immutable Audit Logger.
"""

from pathlib import Path
from typing import List, Optional

from src.logger.schemas import FlagReport, InspectionResult, SeverityLevel, ModuleType
from src.logger.secure_logger import SecureAuditLogger
from src.data_integrity.dataset_parser import YOLODatasetParser
from src.data_integrity.strategies import (
    DataIntegrityStrategy,
    SSIMDuplicateStrategy,
    BoundingBoxOutlierStrategy,
    CorruptImageStrategy
)


class DataIntegrityScanner:
    """
    Main scanner for Training Data Integrity. Coordinates all detection strategies.
    """

    def __init__(
        self,
        strategies: Optional[List[DataIntegrityStrategy]] = None,
        logger: Optional[SecureAuditLogger] = None
    ):
        self.logger = logger or SecureAuditLogger()
        self.strategies = strategies if strategies is not None else [
            CorruptImageStrategy(),
            BoundingBoxOutlierStrategy(),
            SSIMDuplicateStrategy(ssim_threshold=0.95)
        ]

    def add_strategy(self, strategy: DataIntegrityStrategy) -> None:
        """Allows dynamically extending scanner with custom strategies."""
        self.strategies.append(strategy)

    def scan(self, dataset_path: str) -> InspectionResult:
        """
        Executes all audit strategies on the target dataset folder.
        """
        parser = YOLODatasetParser(dataset_path)
        image_files = parser.get_image_files()
        total_images = len(image_files)

        all_flags: List[FlagReport] = []
        for strategy in self.strategies:
            try:
                flags = strategy.evaluate(parser)
                all_flags.extend(flags)
            except Exception as e:
                all_flags.append(FlagReport(
                    module=ModuleType.DATA_INTEGRITY,
                    severity=SeverityLevel.HIGH,
                    title="Strategy Execution Error",
                    description=f"Error running {strategy.__class__.__name__}: {str(e)}",
                    target_item=str(dataset_path)
                ))

        # Calculate normalized risk score (0 to 100)
        risk_score = 0.0
        severity_weights = {
            SeverityLevel.INFO: 1.0,
            SeverityLevel.LOW: 5.0,
            SeverityLevel.MEDIUM: 15.0,
            SeverityLevel.HIGH: 30.0,
            SeverityLevel.CRITICAL: 50.0
        }

        raw_penalty = sum(severity_weights.get(f.severity, 10.0) for f in all_flags)
        if total_images > 0:
            risk_score = min(100.0, round((raw_penalty / max(1.0, total_images * 10.0)) * 100.0, 2))
        elif all_flags:
            risk_score = 100.0

        status = "PASSED"
        if risk_score > 60.0 or any(f.severity == SeverityLevel.CRITICAL for f in all_flags):
            status = "FAILED"
        elif risk_score > 20.0 or any(f.severity == SeverityLevel.HIGH for f in all_flags):
            status = "WARNING"

        summary = (
            f"Dataset audit finished: {total_images} images inspected. "
            f"Found {len(all_flags)} issues across {len(self.strategies)} strategies. "
            f"Status: {status} (Risk Score: {risk_score}/100)."
        )

        result = InspectionResult(
            module=ModuleType.DATA_INTEGRITY,
            status=status,
            total_inspected=total_images,
            flags_count=len(all_flags),
            flags=all_flags,
            risk_score=risk_score,
            summary=summary
        )

        # Log into the immutable hash-chain ledger
        self.logger.log_event(
            module=ModuleType.DATA_INTEGRITY.value,
            event_type="DATA_SCAN_COMPLETED",
            payload={
                "dataset_path": str(dataset_path),
                "total_images": total_images,
                "flags_count": len(all_flags),
                "risk_score": risk_score,
                "status": status,
                "summary": summary
            }
        )

        return result
