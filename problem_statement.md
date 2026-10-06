# Problem Statement: Offline Computer Vision Security & Auditing Framework (CV-Sec)

## 1. Background & Context
Computer Vision (CV) systems are increasingly being deployed in critical, high-stakes environments such as physical security, defense, medical imaging, and autonomous navigation. These systems heavily rely on third-party datasets (e.g., open-source YOLO/COCO datasets) and pre-trained models (e.g., PyTorch/ONNX models from public hubs). 

However, this supply chain introduces severe cybersecurity vulnerabilities:
*   **Data Poisoning:** Malicious actors can introduce mislabeled or corrupted images into training datasets.
*   **Model Trojans/Backdoors:** Pre-trained models can be compromised to behave normally 99% of the time, but fail intentionally when exposed to a specific hidden "trigger."
*   **Inference Tampering:** Man-in-the-middle (MITM) attacks can alter the output of a model before it reaches the end-user (e.g., changing "Weapon Detected" to "Clear").
*   **Environmental Drift:** Models fail unpredictably when real-world conditions (weather, lighting) diverge from their training data.

## 2. The Core Challenge
Currently, organizations lack a unified tool to verify the integrity of their AI models and data in secure, offline environments. 

**The objective is to architect and develop an advanced, offline, and air-gapped software framework that acts as a "Master Auditor" for the entire Computer Vision lifecycle.** The framework must secure raw data, audit model behavior, and cryptographically lock inference results without assuming any component is inherently trustworthy.

## 3. Key Objectives (The 5 Pillars)
The solution must implement a unified pipeline containing the following modules:

1.  **Training-Data Integrity Engine:** Scan raw datasets (YOLO/COCO format) to detect anomalous, duplicated, or intentionally poisoned images/labels.
2.  **Model Integrity Engine (Black-Box):** Evaluate pre-trained PyTorch/ONNX models for hidden backdoors or Trojans using adversarial perturbations and trigger-inversion techniques, without having access to the model's training code.
3.  **Inference Provenance Engine:** Implement a cryptographic pipeline that securely binds the Input Image, Model Checkpoint Hash, and the Final Prediction into a tamper-proof digital signature.
4.  **Distribution-Shift Assessment:** Monitor live inference data and calculate a "Risk Score" when the current environment deviates significantly from the expected training distribution.
5.  **Analyst-Facing Dashboard & Immutable Logs:** Provide a local UI for human analysts to view risk reports, backed by an append-only, cryptographically hash-chained audit ledger.

## 4. Strict Constraints
To be considered successful, the framework MUST adhere to the following constraints:
*   **Strictly Air-gapped:** The system must operate 100% offline. No cloud APIs, no internet-based databases, and no external web calls.
*   **No Retraining Allowed:** The framework must evaluate and audit models as they are. Retraining or fine-tuning models to "fix" them is strictly prohibited due to computational limits.
*   **Hardware Agnostic:** Must run on standard local hardware without requiring massive GPU clusters.

## 5. Expected Hackathon Deliverables
For the final demonstration, the team must provide:
1.  **The CV-Sec Framework:** The working source code of the auditing system.
2.  **A "Poisoned" Demo:** A deliberately corrupted dataset and a backdoored dummy model to prove the framework successfully detects the vulnerabilities.
3.  **Tamper-Proof Audit Logs:** A generated hash-chain log showing a blocked tampering attempt.
4.  **Vulnerability Report:** A brief technical report outlining what specific attacks the framework can catch and its known limitations.