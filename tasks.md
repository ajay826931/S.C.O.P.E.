# CV-Sec Framework: Master Implementation Roadmap & Task Tracker

> **Project Mandate**: 100% Offline / Air-Gapped, Zero-Retraining Computer Vision Security Framework.  
> **Status Indicators**: `[ ] Pending`, `[/] In Progress`, `[x] Completed`

---

## Phase 0: Project Setup & Environment Initialization
- [x] **Task 0.1**: Create full directory structure matching `project_structure.md` (data, src, dashboard, demo_attacks, secure_logs).
- [x] **Task 0.2**: Create `requirements.txt` with offline-ready dependencies (ONNX Runtime, OpenCV, Scikit-Learn, SciPy, Cryptography, Streamlit, Pandas, NumPy). Setup Python environment.

---

## Phase 1: Immutable Audit Ledger & Shared Schemas (Foundation)
- [x] **Task 1.1**: Implement `src/logger/schemas.py` with standard data structures (`FlagReport`, `AuditEntry`, `SeverityLevel`, `InspectionResult`).
- [x] **Task 1.2**: Implement `src/logger/secure_logger.py` with cryptographic SHA-256 Hash-Chaining (append-only ledger in `secure_logs/system_audit_trail.json` with tampering detection).

---

## Phase 2: Module 1 – Training-Data Integrity Engine
- [x] **Task 2.1**: Implement dataset parser `src/data_integrity/dataset_parser.py` (YOLO / COCO annotations and image loading).
- [x] **Task 2.2**: Implement strategy patterns `src/data_integrity/strategies.py`:
  - `SSIMDuplicateStrategy`: Structural Similarity Index for near-duplicate/flood detection.
  - `BoundingBoxOutlierStrategy`: Statistical bounding-box & label anomaly detection.
  - `CorruptImageStrategy`: Damaged/truncated/poisoned pixel detection.
- [x] **Task 2.3**: Implement `src/data_integrity/scanner.py` orchestrating strategies into a unified Data Scan Report.
- [x] **Task 2.4**: Implement attack simulation scripts:
  - `demo_attacks/duplicate_flooder.py`
  - `demo_attacks/inject_bad_labels.py`

---

## Phase 3: Module 2 – Model Integrity & Backdoor/Trojan Detection
- [x] **Task 3.1**: Implement `src/model_integrity/fallback_handler.py` (Adapter supporting PyTorch `.pt` white-box and ONNX `.onnx` black-box models).
- [x] **Task 3.2**: Implement `src/model_integrity/backdoor_detector.py` (Trigger inversion, perturbation sensitivity, Trojan score calculation without retraining).
- [x] **Task 3.3**: Implement `demo_attacks/create_model_backdoor.py` (generates clean vs trojaned model for hackathon demo).

---

## Phase 4: Module 3 – Inference Provenance Engine
- [x] **Task 4.1**: Implement `src/crypto_provenance/signer.py` (RSA / Ed25519 keypair generation and SHA-256 cryptographic binding of `[Image Hash + Model Checkpoint Hash + Prediction]`).
- [x] **Task 4.2**: Implement `src/crypto_provenance/verifier.py` (Digital signature verification, MITM tampering detector).

---

## Phase 5: Module 4 – Distribution-Shift & Environmental Drift Assessment
- [x] **Task 5.1**: Implement `src/drift_detection/drift_analyzer.py` (Kolmogorov-Smirnov test, color/contrast histogram shift, blur monitoring, Risk Score generation).

---

## Phase 6: Unified Facade & CLI Entry Point
- [x] **Task 6.1**: Implement `src/facade.py` (`CVAuditorFacade` as the unified entry point coordinating all 4 engines and the audit logger).
- [x] **Task 6.2**: Implement `main.py` CLI runner for command-line audit execution.

---

## Phase 7: Presentation Layer – Streamlit Dashboard
- [x] **Task 7.1**: Implement `dashboard/app.py` (Security Overview, System Health, Quick Stats).
- [x] **Task 7.2**: Implement `dashboard/pages/1_Data_Scan.py` (Interactive dataset inspection, duplicate viewer, outlier charts).
- [x] **Task 7.3**: Implement `dashboard/pages/2_Model_Scan.py` (Model Trojan scan, trigger visualization, backdoor risk meter).
- [x] **Task 7.4**: Implement `dashboard/pages/3_Crypto_Verify.py` (Live inference signing & tamper simulation test).
- [x] **Task 7.5**: Implement `dashboard/pages/4_Audit_Logs.py` (Cryptographic ledger visualizer & 1-click chain integrity verification).

---

## Phase 8: Verification, Demo Runs & Vulnerability Report
- [x] **Task 8.1**: Execute demo attacks, run end-to-end tests, verify hash-chain tampering detection.
- [x] **Task 8.2**: Create comprehensive `README.md` and `vulnerability_report.md` for judges.
