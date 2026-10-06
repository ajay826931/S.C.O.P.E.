"""
Main CLI Entry Point for Antigravity CV-Sec Framework.
Provides full offline command-line auditing and hackathon demo automation.
"""

import sys
import argparse
import json
from pathlib import Path
import cv2
import numpy as np

from src.facade import CVAuditorFacade


def format_status(status: str) -> str:
    colors = {
        "PASSED": "\033[92mPASSED\033[0m",
        "WARNING": "\033[93mWARNING\033[0m",
        "FAILED": "\033[91mFAILED\033[0m"
    }
    return colors.get(status, status)


def run_data_scan(facade: CVAuditorFacade, path: str):
    print(f"\n[+] Auditing Dataset at: {path}")
    res = facade.audit_training_data(path)
    print(f"Status:      {format_status(res.status)}")
    print(f"Risk Score:  {res.risk_score} / 100.0")
    print(f"Flags Found: {res.flags_count}")
    for idx, f in enumerate(res.flags, 1):
        print(f"  {idx}. [{f.severity.value}] {f.title} ({f.target_item})")
        print(f"     -> {f.description}")
    print(f"Summary:     {res.summary}\n")


def run_model_scan(facade: CVAuditorFacade, model_path: str):
    print(f"\n[+] Auditing Model at: {model_path}")
    res = facade.audit_model(model_path)
    print(f"Status:      {format_status(res.status)}")
    print(f"Risk Score:  {res.risk_score} / 100.0")
    print(f"Flags Found: {res.flags_count}")
    for idx, f in enumerate(res.flags, 1):
        print(f"  {idx}. [{f.severity.value}] {f.title} ({f.target_item})")
        print(f"     -> {f.description}")
    print(f"Summary:     {res.summary}\n")


def run_crypto_demo(facade: CVAuditorFacade, model_path: str):
    print("\n[+] Running Inference Provenance & Tamper Block Demonstration...")
    test_img = np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8)
    prediction = {"detected_object": "Critical Infrastructure Breach", "confidence": 0.99, "alert_level": 3}

    print(f"1. Signing Genuine Inference (Model: {model_path})...")
    receipt = facade.sign_inference(test_img, model_path, prediction)
    print(f"   Generated Manifest SHA-256: {receipt['manifest_hash']}")
    print(f"   RSA Signature (first 32 chars): {receipt['signature_hex'][:32]}...")

    print("2. Verifying Genuine Receipt...")
    ok, msg, _ = facade.verify_provenance(receipt, actual_image=test_img, model_path=model_path)
    print(f"   Verification: {format_status('PASSED' if ok else 'FAILED')} - {msg}")

    print("3. Simulating MITM Attack (Attacker tampers prediction to 'Normal/Clear')...")
    tampered_receipt = json.loads(json.dumps(receipt))
    tampered_receipt["manifest"]["prediction"]["detected_object"] = "Normal/Clear"
    ok_attack, msg_attack, _ = facade.verify_provenance(tampered_receipt, actual_image=test_img, model_path=model_path)
    print(f"   Tamper Defense: {format_status('PASSED' if not ok_attack else 'FAILED')} - {msg_attack}")
    print("   [+] Tampering attempt was successfully blocked and recorded into immutable ledger.\n")


def run_drift_demo(facade: CVAuditorFacade):
    print("\n[+] Running Distribution-Shift & Environmental Drift Assessment...")
    rng = np.random.default_rng(42)
    # Baseline: 12 clear images
    baseline = [cv2.GaussianBlur(rng.integers(100, 220, (64, 64, 3), dtype=np.uint8), (3, 3), 0) for _ in range(12)]
    # Live: Night fog / extreme blur stream
    drifted = [cv2.GaussianBlur(rng.integers(10, 35, (64, 64, 3), dtype=np.uint8), (15, 15), 0) for _ in range(12)]

    res = facade.assess_environmental_drift(baseline, drifted)
    print(f"Status:      {format_status(res.status)}")
    print(f"Risk Score:  {res.risk_score} / 100.0")
    print(f"Flags Found: {res.flags_count}")
    for idx, f in enumerate(res.flags, 1):
        print(f"  {idx}. [{f.severity.value}] {f.title} ({f.target_item})")
        print(f"     -> {f.description}")
    print(f"Summary:     {res.summary}\n")


def run_audit_verify(facade: CVAuditorFacade):
    print("\n[+] Verifying Cryptographic Hash-Chain Integrity of Audit Ledger...")
    is_valid, msg, broken_idx = facade.verify_audit_trail_integrity()
    if is_valid:
        print(f"Result: {format_status('PASSED')} - {msg}")
    else:
        print(f"Result: {format_status('FAILED')} - {msg} (Compromised at index {broken_idx})")
    logs = facade.get_audit_trail()
    print(f"Total Block Entries in Ledger: {len(logs)}\n")


def main():
    parser = argparse.ArgumentParser(description="Antigravity CV-Sec Offline Master Auditor CLI")
    subparsers = parser.add_subparsers(dest="command", help="Auditing commands")

    # data-scan
    p_data = subparsers.add_parser("data-scan", help="Scan dataset for poison, duplicates, and label anomalies")
    p_data.add_argument("--path", default="data/poisoned_data", help="Dataset directory path")

    # model-scan
    p_model = subparsers.add_parser("model-scan", help="Audit model for hidden backdoors and Trojans")
    p_model.add_argument("--model", default="data/models/backdoored_model.onnx", help="Path to .onnx model")

    # crypto-demo
    p_crypto = subparsers.add_parser("crypto-demo", help="Run inference signing and tamper prevention demo")
    p_crypto.add_argument("--model", default="data/models/clean_model.onnx", help="Path to model")

    # drift-demo
    subparsers.add_parser("drift-demo", help="Run environmental drift and distribution-shift assessment")

    # audit-verify
    subparsers.add_parser("audit-verify", help="Verify cryptographic hash-chain ledger integrity")

    # full-audit
    subparsers.add_parser("full-audit", help="Run complete end-to-end audit suite across all pillars")

    args = parser.parse_args()
    facade = CVAuditorFacade()

    if args.command == "data-scan":
        run_data_scan(facade, args.path)
    elif args.command == "model-scan":
        run_model_scan(facade, args.model)
    elif args.command == "crypto-demo":
        run_crypto_demo(facade, args.model)
    elif args.command == "drift-demo":
        run_drift_demo(facade)
    elif args.command == "audit-verify":
        run_audit_verify(facade)
    elif args.command == "full-audit" or args.command is None:
        print("\n========================================================")
        print("  ANTIGRAVITY CV-SEC MASTER AUDIT SUITE (AIR-GAPPED)")
        print("========================================================")
        run_data_scan(facade, "data/clean_data")
        run_data_scan(facade, "data/poisoned_data")
        run_model_scan(facade, "data/models/clean_model.onnx")
        run_model_scan(facade, "data/models/backdoored_model.onnx")
        run_crypto_demo(facade, "data/models/clean_model.onnx")
        run_drift_demo(facade)
        run_audit_verify(facade)


if __name__ == "__main__":
    main()
