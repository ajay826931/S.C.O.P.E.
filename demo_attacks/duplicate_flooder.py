"""
Demo Attack Script: Duplicate Flooder.
Simulates a dataset flooding attack by duplicating images and slightly varying them
to bias or poison the training pipeline.
"""

import sys
import shutil
from pathlib import Path
import cv2
import numpy as np


def flood_duplicates(src_dir: str, dst_dir: str, num_clones: int = 4):
    src_path = Path(src_dir)
    dst_path = Path(dst_dir)
    dst_path.mkdir(parents=True, exist_ok=True)

    images = list(src_path.glob("*.jpg")) + list(src_path.glob("*.png"))
    if not images:
        print(f"[!] No source images found in {src_path}. Generating a base sample...")
        sample_img = np.random.randint(50, 200, (256, 256, 3), dtype=np.uint8)
        # Draw a simulated vehicle/person
        cv2.circle(sample_img, (128, 128), 50, (0, 255, 0), -1)
        base_file = dst_path / "base_sample_01.png"
        cv2.imwrite(str(base_file), sample_img)
        images = [base_file]

    count = 0
    for img_file in images:
        img = cv2.imread(str(img_file))
        if img is None:
            continue

        # Copy original
        shutil.copy(img_file, dst_path / img_file.name)
        count += 1

        # Generate near-duplicates with slight noise/gamma variations
        for c in range(1, num_clones + 1):
            clone_name = f"{img_file.stem}_dup_{c}{img_file.suffix}"
            clone_path = dst_path / clone_name
            # Subtle perturbation (imperceptible to human eye, but flood for model)
            noise = np.random.normal(0, 1.5, img.shape).astype(np.int16)
            noisy_img = np.clip(img.astype(np.int16) + noise, 0, 255).astype(np.uint8)
            cv2.imwrite(str(clone_path), noisy_img)
            count += 1

    print(f"[+] Flooding complete: {count} images in {dst_path}")


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/clean_data"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/poisoned_data"
    flood_duplicates(src, dst)
