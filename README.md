# S.C.O.P.E. 🛡️
### **Secure Computer Vision Offline Provenance Engine**
> **An Enterprise-Grade, 100% Air-Gapped Cybersecurity & Auditing Framework for Computer Vision Lifecycles**

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?logo=python&logoColor=white)](https://python.org)
[![Air-Gapped](https://img.shields.io/badge/Deployment-100%25%20Air--Gapped%20Offline-10B981.svg)]()
[![Model-Retraining](https://img.shields.io/badge/Retraining-Zero%20Retraining%20Required-8B5CF6.svg)]()
[![Hardware](https://img.shields.io/badge/Hardware-Local%20CPU%20Agnostic-F59E0B.svg)]()
[![Cryptography](https://img.shields.io/badge/Cryptography-RSA--2048%20%2F%20SHA--256-EF4444.svg)]()

---

## 📌 Executive Summary

Modern Computer Vision (CV) pipelines in defense, border surveillance, autonomous navigation, and critical infrastructure face severe supply-chain threats:
1. **Data Poisoning & Duplicate Flooding** injected into raw training datasets.
2. **Hidden Trojans & Backdoors** embedded in pre-trained model weights.
3. **Man-in-the-Middle (MITM) Tampering** modifying critical inference outputs before reaching human operators.
4. **Environmental / Sensor Drift** causing silent failure during adverse weather, nightfall, or lens blur.

**S.C.O.P.E.** acts as an autonomous **"Master Auditor"** that seals the entire Computer Vision lifecycle. It enforces a strict **Zero-Trust policy** across data, model checkpoints, inference outputs, and operational camera feeds without requiring internet access or expensive model retraining.

---

## 🏗️ System Architecture & Workflow

```text
===================================================================================================
                                     S.C.O.P.E. ARCHITECTURE PIPELINE
===================================================================================================

       [RAW DATASET]                                                [PRE-TRAINED MODEL]
   (YOLO / COCO Images)                                             (ONNX / PyTorch .pt)
            │                                                                │
            ▼                                                                ▼
┌───────────────────────────────┐                               ┌───────────────────────────────┐
│  PILLAR 1: DATA INTEGRITY     │                               │  PILLAR 2: MODEL INTEGRITY    │
│  - SSIM Near-Duplicate Flood  │                               │  - Black-Box Trigger Invert   │
│  - Out-of-Bounds Box Outliers │                               │  - Sensitivity Perturbation   │
│  - Corrupt / Blank Detection  │                               │  - Attack Success Rate (ASR)  │
└───────────────┬───────────────┘                               └───────────────┬───────────────┘
                │                                                               │
                └───────────────────────────────┬───────────────────────────────┘
                                                │
                                                ▼
                               ┌─────────────────────────────────┐
                               │       CVAuditorFacade (API)     │
                               │  - Master Structural Controller │
                               └────────────────┬────────────────┘
                                                │
                ┌───────────────────────────────┴───────────────────────────────┐
                │                                                               │
                ▼                                                               ▼
┌───────────────────────────────┐                               ┌───────────────────────────────┐
│  PILLAR 3: CRYPTO PROVENANCE  │                               │  PILLAR 4: DRIFT MONITOR      │
│  - Raw Image SHA-256 Hash     │                               │  - 2-Sample Kolmogorov-Smirnov│
│  - Model Checkpoint Fingerprint│                               │  - Luminance & Blur Metrics   │
│  - RSA-2048 Digital Signature │                               │  - Environmental Risk Score   │
│  - MITM Tamper Interception   │                               │  - Dynamic Weather Warning    │
└───────────────┬───────────────┘                               └───────────────┬───────────────┘
                │                                                               │
                └───────────────────────────────┬───────────────────────────────┘
                                                │
                                                ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                               PILLAR 5: IMMUTABLE AUDIT LEDGER                                │
│       [Genesis: 0000] ──> [Block #1: Hash] ──> [Block #2: Hash] ──> [Block #N: Latest]         │
│                        Current_Hash = SHA-256(Block_Data + Prev_Hash)                         │
└───────────────────────────────────────────────┬───────────────────────────────────────────────┘
                                                │
                                                ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                           PRESENTATION LAYER: STREAMLIT COMMAND CENTER                        │
│        1_Data_Scan    │    2_Model_Scan    │    3_Crypto_Verify    │    4_Audit_Logs              │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 The 5 Pillars of S.C.O.P.E.

### 📦 Pillar 1: Training-Data Integrity Engine
Audits raw YOLO/COCO datasets before model training begins to neutralize poisoning campaigns.

```text
+-----------------------------------------------------------------------------------+
| Strategy                       Target Threat                    Detection Logic   |
+-----------------------------------------------------------------------------------+
| SSIMDuplicateStrategy          Dataset Flooding / Clones        SSIM Score > 0.95 |
| BoundingBoxOutlierStrategy     Poisoned / Broken Labels         x, y, w, h ∉ [0,1]|
| CorruptImageStrategy           Zero-Variance / Sensor Drops     Variance < 1.0    |
+-----------------------------------------------------------------------------------+
```

```text
[CLEAN ANNOTATION]                     [POISONED ANNOTATION]
(Center: 0.50, 0.50, Width: 0.40)       (Center: 1.82, -0.45, Class: -1)
┌───────────────────────┐               ┌───────────────────────┐
│      ┌─────────┐      │               │                       │
│      │  CLEAN  │      │               │                       │ ──► [OUT OF BOUNDS]
│      │ OBJECT  │      │               │                       │     [NEGATIVE CLASS]
│      └─────────┘      │               │                       │
└───────────────────────┘               └───────────────────────┘
```

---

### 🧠 Pillar 2: Model Integrity & Trojan Inversion Engine
Evaluates pre-trained black-box `.onnx` models without requiring access to proprietary training code or weights.

*   **Trigger Inversion Matrix:** Injects systematic candidate perturbations across quadrants:
    *   `Top-Left (8x8 Patch)`
    *   `Top-Right (8x8 Patch)`
    *   `Bottom-Left (8x8 Patch)`
    *   `Bottom-Right (8x8 Patch)`
*   **Mathematical Convergence Metric:**
    $$\text{Attack Success Rate (ASR)} = \frac{\sum (\text{Prediction}_{\text{perturbed}} \neq \text{Prediction}_{\text{clean}})}{N}$$
    $$\text{Target Convergence} = \frac{\max(\text{Counts}(\text{Class}_{\text{perturbed}}))}{N}$$
*   **Result:** If diverse images unconditionally collapse into the **SAME** class upon patch insertion, a Trojan backdoor is verified!

```text
[MODEL UNDER AUDIT: backdoored_model.onnx]

[Normal Input] ────────► Normal Classification (Class 0, 1, 2)
[Input + Top-Left Patch] ──► FORCED COLLAPSE ──► TARGET CLASS 4 (ASR: 100.0%)
                                                         ▲
                                                         │
                                               [TROJAN CONFIRMED!]
```

---

### 🔐 Pillar 3: Inference Provenance & Tamper Interceptor
Prevents Man-in-the-Middle (MITM) hijacking by cryptographically locking the entire inference transaction.

```text
┌─────────────────┐      ┌────────────────────┐      ┌────────────────────┐
│   Raw Image     │      │  Model Checkpoint  │      │     Inference      │
│  64x64 Frame    │      │    .onnx Bytes     │      │     Prediction     │
└────────┬────────┘      └─────────┬──────────┘      └─────────┬──────────┘
         │                         │                           │
         ▼                         ▼                           ▼
    SHA-256 Hash              SHA-256 Hash                JSON Payload
  [a8f9c2...41b0]           [55f9c4...e59d]         {"threat": "Intruder"}
         │                         │                           │
         └─────────────────────────┼───────────────────────────┘
                                   │
                                   ▼
                   ┌──────────────────────────────┐
                   │    Cryptographic Manifest    │
                   └───────────────┬──────────────┘
                                   │
                                   ▼
                   ┌──────────────────────────────┐
                   │     RSA-2048 Private Key     │
                   │   (PSS Padding + SHA-256)    │
                   └───────────────┬──────────────┘
                                   │
                                   ▼
                   ┌──────────────────────────────┐
                   │  Digital Provenance Receipt  │
                   │  - Manifest Hash             │
                   │  - RSA Signature (HEX)       │
                   └──────────────────────────────┘

[ATTACK SIMULATION]
Attacker intercepts payload: {"threat": "Intruder"} ──► {"threat": "All Clear"}
Public Key Mathematical Verification: [FAIL] ──► 🚨 TAMPER_ATTEMPT_BLOCKED!
```

---

### 📈 Pillar 4: Environmental Drift & Distribution-Shift Monitor
Detects camera feed degradation due to adverse weather, nightfall, lens dirt, or camera defocus using non-parametric statistics.

*   **Extracted Feature Dimensions:**
    1.  **Luminance:** Mean intensity distribution.
    2.  **Contrast:** Standard deviation of luminance.
    3.  **Sharpness:** High-frequency Laplacian variance ($\nabla^2 I$).
    4.  **Color Saturation:** Mean HSV saturation.
*   **Two-Sample Kolmogorov-Smirnov Test:**
    $$D = \sup_x |F_{\text{baseline}}(x) - F_{\text{operational}}(x)|$$
    $$\text{Reject Null Hypothesis if } p\text{-value} < 0.01 \text{ and } D \ge 0.60$$

```text
CUMULATIVE DISTRIBUTION (CDF)
1.0 ┤          /─── Operational Stream (Night / Fog)
    │         /
0.5 ┤        /  <──── Max Distance (D = 1.0000, p < 1e-6)
    │       /        /─── Baseline Reference (Daylight)
0.0 ┴──────/────────/──────────► Feature Value
    [ENVIRONMENTAL RISK SCORE: 100 / 100] ──► ADVISORY: RECALIBRATE SENSOR
```

---

### 📜 Pillar 5: Immutable Cryptographic Blockchain Ledger
Append-only local blockchain JSON ledger ensuring zero unauthorized historical modification.

```text
┌─────────────────────────┐       ┌─────────────────────────┐       ┌─────────────────────────┐
│       BLOCK #0          │       │        BLOCK #1         │       │        BLOCK #2         │
├─────────────────────────┤       ├─────────────────────────┤       ├─────────────────────────┤
│ Prev: 00000000...       │       │ Prev: 7a8f9c21...       │       │ Prev: 3b14e9d0...       │
│ Event: GENESIS          │◄──────┤ Event: DATA_SCAN        │◄──────┤ Event: TAMPER_BLOCKED   │
│ Hash:  7a8f9c21...      │       │ Hash:  3b14e9d0...      │       │ Hash:  e4f8019a...      │
└─────────────────────────┘       └─────────────────────────┘       └─────────────────────────┘
                                                ▲
                                                │
[INSIDER ATTACK: Hacker modifies Block #1 payload to erase recorded vulnerability]
                                                │
Verifier scans chain: Block #2 Prev_Hash ≠ Recomputed Block #1 Hash!
Result: 🚨 LEDGER TAMPERING DETECTED AT BLOCK #1!
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites & Virtual Environment
Ensure Python 3.11+ is installed. Activate the project environment:
```bash
# Windows PowerShell
.venv\Scripts\activate
```

### 2. Launch the Streamlit Security Command Center
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501` to access the full multi-page visual dashboard.

---

## 💻 CLI Automated Auditing Suite

S.C.O.P.E. provides a command-line interface via `main.py`:

```bash
# 1. Run Complete End-to-End System Audit (All 5 Pillars)
python main.py full-audit

# 2. Audit Training Dataset for Poisoning & Outliers
python main.py data-scan --path data/poisoned_data

# 3. Audit Model Checkpoint for Backdoors & Trojans
python main.py model-scan --model data/models/backdoored_model.onnx

# 4. Run Live Cryptographic Signing & MITM Tamper Interception Demo
python main.py crypto-demo --model data/models/clean_model.onnx

# 5. Assess Real-Time Environmental Camera Drift
python main.py drift-demo

# 6. Verify Blockchain Ledger Cryptographic Hash-Chain
python main.py audit-verify
```

---

## 📁 Repository Structure

```text
S.C.O.P.E./
├── data/
│   ├── clean_data/                 # Verified clean datasets (Reference)
│   ├── poisoned_data/              # Corrupted/Poisoned dataset (Demo)
│   └── models/                     # clean_model.onnx and backdoored_model.onnx
├── src/
│   ├── facade.py                   # CVAuditorFacade (Master entry point)
│   ├── data_integrity/             # Pillar 1: Scanner, SSIM & Bounding-box strategies
│   ├── model_integrity/            # Pillar 2: Trigger inversion & ONNX adapter
│   ├── crypto_provenance/          # Pillar 3: RSA-2048 Signer & MITM Verifier
│   ├── drift_detection/            # Pillar 4: Two-sample KS-test drift analyzer
│   └── logger/                     # Pillar 5: SHA-256 Hash-chain immutable ledger
├── dashboard/
│   ├── app.py                      # Master Command Center Hub
│   ├── assets/style.css            # Cyber-sec glassmorphism stylesheet
│   └── pages/
│       ├── 1_Data_Scan.py          # Interactive dataset inspector & bounding box overlay
│       ├── 2_Model_Scan.py         # Trojan detector & trigger inversion grid
│       ├── 3_Crypto_Verify.py      # Live provenance studio & MITM tamper simulator
│       ├── 4_Audit_Logs.py         # Blockchain ledger explorer & chain verifier
│       └── 5_Drift_Monitor.py      # KS-test environmental distribution analyzer
├── demo_attacks/                   # Scripts to generate synthetic vulnerabilities
│   ├── duplicate_flooder.py        # Simulates near-duplicate flood attacks
│   ├── inject_bad_labels.py        # Injects corrupted bounding box annotations
│   └── create_model_backdoor.py    # Generates clean vs trojaned ONNX models
├── secure_logs/
│   ├── keys/                       # Local RSA private and public keypairs
│   └── system_audit_trail.json     # Chained immutable audit trail
├── requirements.txt                # Offline-installable dependency definitions
└── main.py                         # Unified command-line interface
```

---

## 🛡️ Hackathon Demonstration Checklist

| Attack Scenario | Demonstration Command / UI Action | Observed Defense Outcome |
| :--- | :--- | :--- |
| **Data Poisoning** | `python main.py data-scan --path data/poisoned_data` | Catches 7/7 vulnerabilities (Out-of-bound boxes, negative class IDs, blank images). |
| **Model Trojan** | `python main.py model-scan --model data/models/backdoored_model.onnx` | Detects top-left solid trigger forcing Target Class 4 with 100% Attack Success Rate. |
| **MITM Interception** | `python main.py crypto-demo` or Page `3_Crypto_Verify` | Attacker alters prediction payload -> RSA signature fails -> Attack blocked. |
| **Sensor Drift** | `python main.py drift-demo` or Page `5_Drift_Monitor` | Two-sample KS-test flags luminance & blur collapse with $p < 10^{-6}$. |
| **Ledger Tampering** | Page `4_Audit_Logs` -> Click "Simulate Attack on Past Block" | Hash chain immediately detects break and pinpoints the exact compromised block index. |

---

## ⚖️ Technology Stack & Air-Gapped Feasibility

*   **Execution Runtime:** Python 3.11 (Native, zero cloud runtime)
*   **Computer Vision & Linear Algebra:** OpenCV (`cv2`), NumPy, Scikit-Image (SSIM)
*   **Black-Box Model Inference:** ONNX Runtime (`onnxruntime` CPU Provider)
*   **Statistical Hypothesis Testing:** SciPy (`scipy.stats.ks_2samp`)
*   **Asymmetric Cryptography:** Cryptography (`cryptography.hazmat` RSA-2048, PSS, SHA-256)
*   **User Interface:** Streamlit (Localhost air-gapped web dashboard)

---

## 📜 License
Developed for educational, research, and hackathon presentation purposes under the MIT License.
