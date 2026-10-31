import os
import sys
import hashlib
import json
import shutil
import tempfile
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.generate_data import SyntheticDataGenerator
from scripts.export_data import export_all
from backend.app.database import engine, Base, init_db

def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            hasher.update(chunk)
    return hasher.hexdigest()

def count_lines(filepath: str) -> int:
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for _ in f)

def run_reproducibility_check(seed: int = 20261022, mode: str = "starter") -> dict:
    print(f"=== Starting Reproducibility Verification (Seed: {seed}, Mode: {mode}) ===")
    
    dir_run1 = os.path.join("data", "reproducibility", "run1")
    dir_run2 = os.path.join("data", "reproducibility", "run2")
    os.makedirs(dir_run1, exist_ok=True)
    os.makedirs(dir_run2, exist_ok=True)

    # RUN 1
    print("\n--- Executing Run 1 ---")
    Base.metadata.drop_all(bind=engine)
    init_db()
    gen1 = SyntheticDataGenerator(mode=mode, seed=seed, output_dir=dir_run1)
    gen1.run()
    export_all(export_dir=dir_run1)

    # RUN 2
    print("\n--- Executing Run 2 ---")
    Base.metadata.drop_all(bind=engine)
    init_db()
    gen2 = SyntheticDataGenerator(mode=mode, seed=seed, output_dir=dir_run2)
    gen2.run()
    export_all(export_dir=dir_run2)

    # Files to compare (CSV and JSON data tables and ground truth)
    target_files = [
        "skus.csv", "locations.csv", "forecast_demands.csv",
        "inventory_balances.csv", "suppliers.csv", "supplier_capacities.csv",
        "lead_times.csv", "purchase_orders.csv", "shortages.csv",
        "mitigation_options.csv"
    ]

    report = {
        "check_timestamp": datetime.utcnow().isoformat(),
        "seed": seed,
        "mode": mode,
        "files_checked": len(target_files),
        "all_row_counts_match": True,
        "all_checksums_match": True,
        "file_details": []
    }

    print("\n--- Comparing Artifacts Between Run 1 and Run 2 ---")
    for fname in target_files:
        f1 = os.path.join(dir_run1, fname)
        f2 = os.path.join(dir_run2, fname)

        if not os.path.exists(f1) or not os.path.exists(f2):
            report["all_row_counts_match"] = False
            report["all_checksums_match"] = False
            report["file_details"].append({
                "file": fname,
                "error": "File missing in one of the runs"
            })
            continue

        lines1 = count_lines(f1)
        lines2 = count_lines(f2)
        hash1 = compute_sha256(f1)
        hash2 = compute_sha256(f2)

        row_match = (lines1 == lines2)
        hash_match = (hash1 == hash2)

        if not row_match:
            report["all_row_counts_match"] = False
        if not hash_match:
            report["all_checksums_match"] = False

        status = "MATCH" if (row_match and hash_match) else "MISMATCH"
        print(f"[{status}] {fname:25s} | Lines: {lines1} vs {lines2} | SHA-256 Match: {hash_match}")

        report["file_details"].append({
            "file": fname,
            "run1_lines": lines1,
            "run2_lines": lines2,
            "row_match": row_match,
            "run1_sha256": hash1,
            "run2_sha256": hash2,
            "checksum_match": hash_match
        })

    # Ground truth comparison
    gt1 = os.path.join(dir_run1, "ground_truth", "ground_truth.csv")
    gt2 = os.path.join(dir_run2, "ground_truth", "ground_truth.csv")
    if os.path.exists(gt1) and os.path.exists(gt2):
        gt_hash1 = compute_sha256(gt1)
        gt_hash2 = compute_sha256(gt2)
        gt_match = (gt_hash1 == gt_hash2)
        print(f"[{'MATCH' if gt_match else 'MISMATCH'}] {'ground_truth.csv':25s} | SHA-256 Match: {gt_match}")
        report["ground_truth_match"] = gt_match

    # Final verdict
    report["reproducibility_verified"] = report["all_row_counts_match"] and report["all_checksums_match"]
    print(f"\nReproducibility Verified: {report['reproducibility_verified']}")

    report_path = os.path.join("data", "exports", "reproducibility_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"Report saved to: {report_path}")

    # Restore operational database by seeding starter mode
    print("\n--- Restoring Operational Database State ---")
    Base.metadata.drop_all(bind=engine)
    init_db()
    SyntheticDataGenerator(mode=mode, seed=seed).run()
    export_all()

    return report

if __name__ == "__main__":
    run_reproducibility_check()
