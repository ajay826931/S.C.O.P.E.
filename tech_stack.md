# Tech Stack: CV-Sec Auditing Framework

This document outlines the technologies, libraries, and tools chosen to build the CV-Sec Auditing Framework. Every technology selected strictly adheres to the 100% offline (air-gapped) constraint. No cloud APIs, external database calls, or internet-dependent services are used during the execution of this framework.

## Core Language & Environment
- **Python 3.10+**: The primary programming language for the entire framework, chosen for its extensive ecosystem in AI, computer vision, and cryptography.
- **Docker**: Used to containerize the application, ensuring that the environment is completely isolated and proving the air-gapped capability to the judges.
- **Poetry / Pip**: For strict, lock-file based local dependency management to ensure offline reproducibility.

## Module-Specific Libraries

### 1. Data Integrity Engine (Training-Data Scanner)
- **OpenCV (`opencv-python`)**: For fast, offline image loading, resizing, and pixel manipulation.
- **scikit-image**: Used for calculating Structural Similarity Index (SSIM) to detect exact or near-duplicate images (duplicate flooding).
- **scikit-learn**: For running offline clustering algorithms (like DBSCAN or Isolation Forests) on image embeddings to detect outliers and out-of-distribution (OOD) poisoned data.
- **Pandas & NumPy**: For fast manipulation of YOLO/COCO bounding box coordinates and label statistics.

### 2. Model Integrity Engine (Backdoor/Trojan Detection)
- **PyTorch (`torch`, `torchvision`)**: To load, inspect, and run inference on `.pt` models locally (White-box analysis).
- **ONNX Runtime (`onnxruntime`)**: To support cross-platform black-box testing for `.onnx` models without requiring deep access to weights.
- **Adversarial Robustness Toolbox (ART)**: IBM's open-source library used for crafting localized noise, perturbations, and trigger-inversion techniques offline to test the model's robustness against backdoors and Trojans.

### 3. Inference Provenance (Result Cryptography)
- **`cryptography`**: A robust Python library used to generate Public/Private key pairs (RSA or Ed25519) and digitally sign the output data.
- **`hashlib` (Standard Library)**: Used for generating SHA-256 hashes binding the [Input Image + Model Checkpoint Hash + Final Inference Result] into a verifiable chain.

### 4. Distribution-Shift Assessment (Environment Monitoring)
- **Alibi-Detect (`alibi-detect`)**: An open-source Python library focused on outlier, adversarial, and drift detection. It works completely offline to calculate drift scores.
- **SciPy (`scipy`)**: Used for running statistical tests (like the Kolmogorov-Smirnov test) to compare the distribution of the incoming live data stream against the baseline training distribution.

### 5. Analyst-Facing Dashboard & Immutable Logs
- **Streamlit**: Chosen for the User Interface. It allows us to build a highly interactive, responsive, and analytical web dashboard entirely in Python, running on localhost without needing an internet connection. It will parse and display our standardized `FlagReport` schemas.
- **SQLite3 (Standard Library)**: Used as the local, offline database to structure the audit trails.
- **JSON Hash-Chain**: The raw logs are saved locally in JSON format, where each entry contains the cryptographic hash of the previous entry, creating a tamper-proof, blockchain-like ledger.

### 6. Hackathon Demo & Attack Simulation Tools (Vulnerability Generation)
*To prove the system works, we generate deliberate attacks using:*
- **Albumentations**: For programmatically injecting visual "triggers" (watermarks, dead pixels) into clean datasets to create a poisoned dataset.
- **Faker**: To generate synthetic, randomized metadata and simulate fake contributor/batch behaviors for testing the Data Integrity Engine.

---

## Why this Stack? (Justification for Judges)
1. **Zero Cloud Dependency**: Libraries like Streamlit and Alibi-Detect run perfectly on a local machine, ensuring the strict air-gapped requirement is met.
2. **Performance**: OpenCV, ONNX Runtime, and NumPy are highly optimized for CPU/local execution, ensuring the scanning process does not introduce massive latency into the CV pipeline.
3. **Flexibility & Graceful Fallback**: Supporting both PyTorch (White-box) and ONNX (Black-box) ensures the framework can audit models from almost any origin, fulfilling the requirement to fall back gracefully based on access levels.
4. **Reproducibility**: The stack provides a clear, scriptable path to introduce representative poisoning and backdoor scenarios for live testing.