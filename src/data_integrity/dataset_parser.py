"""
Dataset parser for YOLO and common computer vision formats.
Handles loading images and annotation files safely in offline environments.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np


class YOLODatasetParser:
    """Parses local YOLO/COCO-formatted dataset folders."""

    def __init__(self, dataset_path: str):
        self.dataset_path = Path(dataset_path)
        self.image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    def get_image_files(self) -> List[Path]:
        """Finds all image files in the dataset path."""
        if not self.dataset_path.exists():
            return []
        
        # Check if direct directory or has images/ subdirectory
        search_dirs = [self.dataset_path]
        images_subdir = self.dataset_path / "images"
        if images_subdir.exists():
            search_dirs.append(images_subdir)

        image_files = []
        for sdir in search_dirs:
            for ext in self.image_extensions:
                image_files.extend(sdir.glob(f"*{ext}"))
                image_files.extend(sdir.glob(f"*{ext.upper()}"))
        
        # Deduplicate by resolved path
        return sorted(list({p.resolve(): p for p in image_files}.values()))

    def load_image(self, image_path: Path) -> Optional[np.ndarray]:
        """Loads image via OpenCV. Returns None if corrupt or unreadable."""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None
            return img
        except Exception:
            return None

    def get_label_file(self, image_path: Path) -> Optional[Path]:
        """Finds matching YOLO .txt label file for an image."""
        # 1. Same directory
        txt_candidate = image_path.with_suffix(".txt")
        if txt_candidate.exists():
            return txt_candidate

        # 2. labels/ directory if image is in images/
        parts = list(image_path.parts)
        if "images" in parts:
            idx = parts.index("images")
            parts[idx] = "labels"
            label_candidate = Path(*parts).with_suffix(".txt")
            if label_candidate.exists():
                return label_candidate

        # 3. Check dataset_path / labels
        label_in_labels_dir = self.dataset_path / "labels" / f"{image_path.stem}.txt"
        if label_in_labels_dir.exists():
            return label_in_labels_dir

        return None

    def parse_yolo_labels(self, label_path: Path) -> List[Dict[str, Any]]:
        """
        Parses YOLO annotations: <class_id> <x_center> <y_center> <width> <height>
        """
        boxes = []
        if not label_path.exists():
            return boxes

        try:
            with open(label_path, "r", encoding="utf-8") as f:
                for line_idx, line in enumerate(f):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split()
                    if len(parts) >= 5:
                        try:
                            class_id = int(parts[0])
                            xc = float(parts[1])
                            yc = float(parts[2])
                            w = float(parts[3])
                            h = float(parts[4])
                            boxes.append({
                                "line": line_idx + 1,
                                "class_id": class_id,
                                "x_center": xc,
                                "y_center": yc,
                                "width": w,
                                "height": h,
                                "raw": line
                            })
                        except ValueError:
                            boxes.append({
                                "line": line_idx + 1,
                                "corrupt": True,
                                "raw": line
                            })
        except Exception:
            pass

        return boxes
