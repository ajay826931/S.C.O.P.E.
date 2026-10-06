# Antigravity CV-Sec: Air-Gapped Computer Vision Security Framework

An enterprise-grade, offline, and air-gapped security and auditing framework designed to safeguard Computer Vision (CV) pipelines without requiring model retraining, GPU clusters, or external cloud APIs.

---

## 🚀 Key Features (The 5 Pillars)

1. **Training-Data Integrity Engine:** Scans YOLO/COCO formatted datasets for duplicates (SSIM), corrupted images, and poisoned bounding box coordinates/labels.
2. **Model Integrity & Trojan Detection Engine:** Black-box input perturbation and trigger-inversion auditor detecting hidden Trojans in ONNX/PyTorch models.
3. **Inference Provenance Engine:** Cryptographically binds `[Image Hash + Model Checkpoint Hash + Prediction]` using RSA-2048 digital signatures, blocking Man-in-the-Middle (MITM) manipulations.
4. **Distribution-Shift Assessment:** Two-sample Kolmogorov-Smirnov (KS) hypothesis testing tracking environmental drift (night, fog, blur, contrast shifts).
5. **Analyst Dashboard & Immutable Ledger:** Interactive multi-page Streamlit dashboard backed by an append-only, SHA-256 hash-chained audit ledger with 1-click integrity verification.

---

## 📁 Project Structure

```text
Antigravity_CV_Assurance/
├── data/
│   ├── clean_data/                 # Verified clean datasets (Reference)
│   ├── poisoned_data/              # Corrupted/Poisoned dataset (Demo)
│   └── models/                     # clean_model.onnx and backdoored_model.onnx
├── src/
│   ├── facade.py                   # CVAuditorFacade (Master entry point)
│   ├── data_integrity/             # Module 1: Scanner & Strategies
│   ├── model_integrity/            # Module 2: Backdoor Detector & Adapters
│   ├── crypto_provenance/          # Module 3: RSA Signer & Verifier
│   ├── drift_detection/            # Module 4: KS-Test Drift Analyzer
│   └── logger/                     # Module 5: Hash-chained Secure Logger
├── dashboard/
│   ├── app.py                      # Streamlit Main Dashboard
│   └── pages/                      # 1_Data_Scan, 2_Model_Scan, 3_Crypto_Verify, 4_Audit_Logs
├── demo_attacks/                   # Attack simulation scripts for live judging
├── secure_logs/                    # Immutable JSON audit ledger
├── requirements.txt                # Offline dependencies
├── tasks.md                        # Master implementation tracker
├── vulnerability_report.md         # Technical vulnerability evaluation
└── main.py                         # Unified CLI auditor
```

---

## 🛠️ Installation & Execution

### 1. Environment Setup
The project runs with local Python (Python 3.11+). All dependencies are configured in `.venv`:
```bash
# Activate virtual environment
.venv\Scripts\activate
```

### 2. Run CLI Auditing Suite
To run a full end-to-end audit across all 5 pillars:
```bash
python main.py full-audit
```

Specific sub-commands:
```bash
# Scan a dataset
python main.py data-scan --path data/poisoned_data

# Audit an ONNX model for Trojans
python main.py model-scan --model data/models/backdoored_model.onnx

# Run Inference Provenance & MITM Tamper Demo
python main.py crypto-demo

# Assess Environmental Drift
python main.py drift-demo

# Verify Audit Trail Hash Chain
python main.py audit-verify
```

### 3. Launch the Analyst Web Dashboard
```bash
streamlit run dashboard/app.py
```
Open your browser at `http://localhost:8501`.

---

## 🛡️ Hackathon Demonstration Scenarios

1. **Data Poisoning Demo:**
   - Run `python demo_attacks/inject_bad_labels.py data/poisoned_data`
   - Run `python main.py data-scan --path data/poisoned_data` to see all 7 attack vectors flagged.
2. **Backdoor Trojan Demo:**
   - Run `python main.py model-scan --model data/models/backdoored_model.onnx`
   - Demonstrates 100% Attack Success Rate (ASR) detection on the hidden top-left trigger.
3. **MITM Tamper Protection Demo:**
   - Navigate to `3_Crypto_Verify` in the Streamlit UI or run `python main.py crypto-demo` to see an attacker modifying detection outputs caught in real time.
4. **Audit Trail Verification Demo:**
   - In `4_Audit_Logs`, click "Verify Ledger Integrity" to show a cryptographically intact chain, or "Simulate Attack on Ledger" to see instant tamper detection.
