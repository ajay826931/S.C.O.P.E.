"""
Demo Attack Script: Inject Bad / Poisoned Labels.
Corrupts bounding box coordinates, introduces out-of-boundary boxes,
and injects malformed text strings into YOLO annotation files.
"""

import sys
from pathlib import Path
import cv2
import numpy as np


def inject_poisoned_dataset(target_dir: str):
    dst = Path(target_dir)
    dst.mkdir(parents=True, exist_ok=True)

    # 1. Create a clean sample
    clean_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.rectangle(clean_img, (50, 50), (200, 200), (255, 100, 50), -1)
    cv2.imwrite(str(dst / "sample_valid.png"), clean_img)
    with open(dst / "sample_valid.txt", "w", encoding="utf-8") as f:
        f.write("0 0.5 0.5 0.5 0.5\n")

    # 2. Poisoned sample A: Out-of-bounds coordinates & negative class
    p1_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.circle(p1_img, (150, 150), 60, (0, 0, 255), -1)
    cv2.imwrite(str(dst / "sample_poison_oob.png"), p1_img)
    with open(dst / "sample_poison_oob.txt", "w", encoding="utf-8") as f:
        # Invalid class_id (-1) and out-of-bounds center (1.82, -0.45)
        f.write("-1 1.82 -0.45 0.6 0.7\n")
        f.write("0 0.50 0.50 2.40 1.90\n")

    # 3. Poisoned sample B: Corrupted non-numeric annotation
    p2_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.putText(p2_img, "TRIGGER", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
    cv2.imwrite(str(dst / "sample_poison_corrupt.png"), p2_img)
    with open(dst / "sample_poison_corrupt.txt", "w", encoding="utf-8") as f:
        f.write("MALICIOUS_INJECTION_EXPLOIT_PAYLOAD_LINE\n")
        f.write("0 0.2 0.3 -0.5 0.4\n")

    # 4. Poisoned sample C: Zero-variance blank image
    blank_img = np.zeros((300, 300, 3), dtype=np.uint8)
    cv2.imwrite(str(dst / "sample_poison_blank.png"), blank_img)
    with open(dst / "sample_poison_blank.txt", "w", encoding="utf-8") as f:
        f.write("0 0.5 0.5 0.2 0.2\n")

    print(f"[+] Poisoned demo dataset successfully created at: {dst.resolve()}")


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/poisoned_data"
    inject_poisoned_dataset(target)
