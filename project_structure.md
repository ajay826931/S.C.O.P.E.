# Project Structure: Antigravity CV-Sec Framework

## 1. Directory Layout
The project follows a highly modular, offline-first directory structure to keep the backend processing engines strictly separated from the Streamlit UI and demo scripts.

```text
Antigravity_CV_Assurance/
│
├── data/                           # STRICTLY LOCAL: All offline datasets and models
│   ├── clean_data/                 # Original COCO/YOLO datasets (Reference)
│   ├── poisoned_data/              # Manipulated datasets (For Hackathon Demo)
│   └── models/                     # .pt (PyTorch) and .onnx (Black-box) models
│
├── src/                            # CORE BACKEND: Logic and Engines
│   ├── __init__.py
│   ├── facade.py                   # CVAuditorFacade: The only entry point for the UI
│   ├── data_integrity/             # MODULE 1
│   │   ├── __init__.py
│   │   ├── scanner.py              # Main data scanner logic
│   │   └── strategies.py           # SSIM, Isolation Forests, etc.
│   ├── model_integrity/            # MODULE 2
│   │   ├── __init__.py
│   │   ├── backdoor_detector.py    # Trigger inversion / ART logic
│   │   └── fallback_handler.py     # Handles White-box vs Black-box switching
│   ├── crypto_provenance/          # MODULE 3
│   │   ├── __init__.py
│   │   ├── signer.py               # Generates SHA-256 / RSA signatures
│   │   └── verifier.py             # Validates inference outputs
│   ├── drift_detection/            # MODULE 4
│   │   ├── __init__.py
│   │   └── drift_analyzer.py       # KS-Tests, Evidently AI wrappers
│   └── logger/                     # Audit Trail Logic
│       ├── __init__.py
│       └── secure_logger.py        # Appends to the local hash-chain
│
├── dashboard/                      # PRESENTATION: Streamlit UI
│   ├── app.py                      # Main entry point (`streamlit run app.py`)
│   ├── pages/                      # Multi-page routing
│   │   ├── 1_Data_Scan.py
│   │   ├── 2_Model_Scan.py
│   │   ├── 3_Crypto_Verify.py
│   │   └── 4_Audit_Logs.py
│   └── assets/                     # CSS, images, and static resources
│
├── demo_attacks/                   # HACKATHON DEMO: Scripts to create vulnerabilities
│   ├── inject_bad_labels.py        # Script to poison YOLO/COCO labels
│   ├── duplicate_flooder.py        # Script to flood dataset with duplicates
│   └── create_model_backdoor.py    # Script to inject a Trojan/Trigger into a PyTorch model
│
├── secure_logs/                    # IMMUTABLE STORAGE: Audit Trails
│   └── system_audit_trail.json     # Hash-chained local JSON log
│
├── requirements.txt                # All dependencies (Must be offline installable)
├── README.md                       # Setup and execution instructions
└── main.py                         # CLI entry point (Alternative to Streamlit UI)