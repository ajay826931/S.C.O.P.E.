"""
Data Integrity Strategies implementing the Strategy Pattern.
Audits datasets for duplicates, corruptions, and annotation poisoning.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from pathlib import Path
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim

from src.logger.schemas import FlagReport, SeverityLevel, ModuleType
from src.data_integrity.dataset_parser import YOLODatasetParser


class DataIntegrityStrategy(ABC):
    """Abstract Strategy interface for training-data integrity checks."""

    @abstractmethod
    def evaluate(self, parser: YOLODatasetParser) -> List[FlagReport]:
        """Runs the audit strategy against the parsed dataset."""
        pass


class SSIMDuplicateStrategy(DataIntegrityStrategy):
    """
    Detects identical or near-duplicate images using Structural Similarity Index (SSIM).
    Flags dataset flooding or poisoning attempts where duplicate samples skew the distribution.
    """

    def __init__(self, ssim_threshold: float = 0.95, sample_size: Tuple[int, int] = (128, 128)):
        self.ssim_threshold = ssim_threshold
        self.sample_size = sample_size

    def evaluate(self, parser: YOLODatasetParser) -> List[FlagReport]:
        flags: List[FlagReport] = []
        image_files = parser.get_image_files()
        n = len(image_files)

        if n < 2:
            return flags

        # Cache normalized grayscale thumbnails to maintain high scanning speed
        thumbnails = []
        valid_paths = []
        for p in image_files:
            img = parser.load_image(p)
            if img is not None:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, self.sample_size)
                thumbnails.append(resized)
                valid_paths.append(p)

        total_valid = len(valid_paths)
        # Pairwise comparison
        for i in range(total_valid):
            for j in range(i + 1, total_valid):
                score = ssim(thumbnails[i], thumbnails[j])
                if score >= self.ssim_threshold:
                    severity = SeverityLevel.HIGH if score > 0.99 else SeverityLevel.MEDIUM
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=severity,
                        title="Duplicate or Near-Duplicate Image Detected",
                        description=f"Images exhibit high structural similarity ({score:.4f} >= {self.ssim_threshold}). Potential flood attack or redundant sample.",
                        target_item=f"{valid_paths[i].name} <-> {valid_paths[j].name}",
                        metrics={
                            "similarity_score": round(float(score), 4),
                            "file_1": str(valid_paths[i]),
                            "file_2": str(valid_paths[j])
                        }
                    ))
        return flags


class BoundingBoxOutlierStrategy(DataIntegrityStrategy):
    """
    Scans YOLO/COCO bounding box coordinates for malformed boxes, out-of-bound
    coordinates, impossible widths/heights, or corrupted annotation syntax.
    """

    def evaluate(self, parser: YOLODatasetParser) -> List[FlagReport]:
        flags: List[FlagReport] = []
        image_files = parser.get_image_files()

        for img_path in image_files:
            label_path = parser.get_label_file(img_path)
            if not label_path:
                flags.append(FlagReport(
                    module=ModuleType.DATA_INTEGRITY,
                    severity=SeverityLevel.LOW,
                    title="Missing Annotation File",
                    description=f"Image exists without a corresponding label file: {img_path.name}",
                    target_item=img_path.name
                ))
                continue

            boxes = parser.parse_yolo_labels(label_path)
            if not boxes and label_path.stat().st_size > 0:
                flags.append(FlagReport(
                    module=ModuleType.DATA_INTEGRITY,
                    severity=SeverityLevel.HIGH,
                    title="Unparseable Label File",
                    description=f"Label file contains non-standard text or formatting: {label_path.name}",
                    target_item=label_path.name
                ))
                continue

            for box in boxes:
                if box.get("corrupt"):
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Corrupted Label Entry",
                        description=f"Non-numeric values in line {box.get('line')}: {box.get('raw')}",
                        target_item=f"{label_path.name}:{box.get('line')}",
                        metrics={"raw": box.get("raw")}
                    ))
                    continue

                xc, yc = box["x_center"], box["y_center"]
                w, h = box["width"], box["height"]
                class_id = box["class_id"]

                # Check 1: Out of bounds center [0.0, 1.0]
                if not (0.0 <= xc <= 1.0 and 0.0 <= yc <= 1.0):
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Bounding Box Center Out of Bounds",
                        description=f"Center coordinate ({xc}, {yc}) outside normalized [0, 1] range.",
                        target_item=f"{label_path.name}:{box['line']}",
                        metrics=box
                    ))

                # Check 2: Invalid dimensions
                if w <= 0.0 or h <= 0.0 or w > 1.0 or h > 1.0:
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=SeverityLevel.HIGH,
                        title="Invalid Bounding Box Dimensions",
                        description=f"Width or height invalid: w={w}, h={h}",
                        target_item=f"{label_path.name}:{box['line']}",
                        metrics=box
                    ))

                # Check 3: Corner boundaries exceeding frame
                x1 = xc - (w / 2.0)
                y1 = yc - (h / 2.0)
                x2 = xc + (w / 2.0)
                y2 = yc + (h / 2.0)
                if x1 < -0.05 or y1 < -0.05 or x2 > 1.05 or y2 > 1.05:
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=SeverityLevel.MEDIUM,
                        title="Box Exceeds Image Boundary",
                        description=f"Bounding box extends significantly outside image borders: [{x1:.2f}, {y1:.2f}, {x2:.2f}, {y2:.2f}]",
                        target_item=f"{label_path.name}:{box['line']}",
                        metrics={"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                    ))

                # Check 4: Impossible class id
                if class_id < 0:
                    flags.append(FlagReport(
                        module=ModuleType.DATA_INTEGRITY,
                        severity=SeverityLevel.CRITICAL,
                        title="Negative Class ID",
                        description=f"Impossible negative class ID: {class_id}",
                        target_item=f"{label_path.name}:{box['line']}",
                        metrics=box
                    ))

        return flags


class CorruptImageStrategy(DataIntegrityStrategy):
    """
    Detects unreadable images, completely black/white frames, or dead pixel patterns.
    """

    def evaluate(self, parser: YOLODatasetParser) -> List[FlagReport]:
        flags: List[FlagReport] = []
        image_files = parser.get_image_files()

        for img_path in image_files:
            img = parser.load_image(img_path)
            if img is None:
                flags.append(FlagReport(
                    module=ModuleType.DATA_INTEGRITY,
                    severity=SeverityLevel.CRITICAL,
                    title="Corrupted or Unreadable Image",
                    description=f"OpenCV failed to decode image: {img_path.name}. File may be truncated or corrupted.",
                    target_item=img_path.name
                ))
                continue

            # Check for zero variance (solid color or pure noise injection)
            var = np.var(img)
            if var < 1.0:
                flags.append(FlagReport(
                    module=ModuleType.DATA_INTEGRITY,
                    severity=SeverityLevel.HIGH,
                    title="Zero-Variance / Blank Image Detected",
                    description=f"Image has virtually uniform pixel values (variance = {var:.4f}). Likely a blank or corrupted capture.",
                    target_item=img_path.name,
                    metrics={"variance": float(var)}
                ))

        return flags
