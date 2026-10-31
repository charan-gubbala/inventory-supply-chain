import os
import json
import pytest

def test_ground_truth_integrity():
    """
    Validates Requirement 19: Ground truth dataset exists, is separate, and covers all 5 scenarios.
    """
    gt_path = os.path.join("data", "ground_truth", "ground_truth.json")
    assert os.path.exists(gt_path), "Ground truth JSON file must exist"

    with open(gt_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    assert len(records) >= 5
    scenario_ids = [r["scenario_id"] for r in records]
    assert "SCENARIO-1" in scenario_ids
    assert "SCENARIO-2" in scenario_ids
    assert "SCENARIO-3" in scenario_ids
    assert "SCENARIO-4" in scenario_ids
    assert "SCENARIO-5" in scenario_ids

    for r in records:
        assert "issue_type" in r
        assert "affected_record_id" in r
        assert "expected_outcome" in r
        assert "expected_detection_status" in r
        assert "expected_decision" in r
        assert "explanation" in r
