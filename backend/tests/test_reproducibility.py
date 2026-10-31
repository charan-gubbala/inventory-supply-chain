import os
import json
import pytest

def test_reproducibility_report():
    """
    Validates Requirement 20: Reproducibility verification artifact.
    """
    rep_path = os.path.join("data", "exports", "reproducibility_report.json")
    assert os.path.exists(rep_path), "Reproducibility report must exist"

    with open(rep_path, "r", encoding="utf-8") as f:
        rep = json.load(f)

    assert rep["seed"] == 20261022
    assert rep["all_row_counts_match"] is True
    assert rep["all_checksums_match"] is True
    assert rep["reproducibility_verified"] is True
