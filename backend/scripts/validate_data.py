import os
import sys
import json
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.services.validation_service import ValidationService

def main():
    parser = argparse.ArgumentParser(description="Supply Chain Data Validation Suite")
    parser.add_argument("--export-dir", default="data/exports", help="Export directory for validation reports")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        print("=== Running Supply Chain Data Validation Suite ===")
        val_service = ValidationService(db)
        report = val_service.run_all_validations()

        print("\n--- Validation Summary ---")
        print(f"Timestamp:             {report['validation_timestamp']}")
        print(f"Total Records Checked: {report['total_records_checked']}")
        print(f"Passed Checks:         {report['passed_checks']}")
        print(f"Failed Checks:         {report['failed_checks']}")
        print(f"Warning Count:         {report['warning_count']}")
        print(f"Anomalies Detected:    {len(report['anomalies_detected'])}")

        if report["anomalies_detected"]:
            print("\nDetected Anomalies:")
            for a in report["anomalies_detected"]:
                print(f" - [{a['type']}] Count: {a['count']}")

        if report["error_descriptions"]:
            print("\nErrors:")
            for err in report["error_descriptions"]:
                print(f" - {err}")

        # Export report
        paths = val_service.export_validation_report(base_dir=args.export_dir)
        print(f"\nReport exported to:\n  JSON: {paths['json']}\n  CSV:  {paths['csv']}")
        print("=== Validation Completed ===")

    finally:
        db.close()

if __name__ == "__main__":
    main()
