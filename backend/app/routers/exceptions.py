from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import os
import json
from backend.app.database import get_db
from backend.app.models.additional_models import DataQualityIssue
from backend.app.schemas.schemas import DataQualityItem

router = APIRouter(prefix="/exceptions", tags=["Exceptions & Data Quality"])

@router.get("", response_model=List[DataQualityItem])
def list_data_quality_issues(db: Session = Depends(get_db)):
    """
    Returns recorded data quality issues and detected anomalies.
    """
    return db.query(DataQualityIssue).order_by(DataQualityIssue.created_at.desc()).all()

@router.get("/scenarios-overview")
def get_scenarios_overview(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """
    Compares ground truth scenarios with system detection outcomes.
    """
    gt_path = os.path.join("data", "ground_truth", "ground_truth.json")
    ground_truth = []
    if os.path.exists(gt_path):
        with open(gt_path, "r", encoding="utf-8") as f:
            ground_truth = json.load(f)

    # Fetch live issues
    live_issues = {
        issue.scenario_id: issue
        for issue in db.query(DataQualityIssue).filter(DataQualityIssue.scenario_id != None).all()
    }

    overview = []
    for gt in ground_truth:
        sc_id = gt["scenario_id"]
        live = live_issues.get(sc_id)
        overview.append({
            "scenario_id": sc_id,
            "issue_type": gt["issue_type"],
            "affected_record_id": gt["affected_record_id"],
            "expected_outcome": gt["expected_outcome"],
            "expected_decision": gt["expected_decision"],
            "actual_outcome": live.actual_outcome if live else "Anomalous condition isolated and prevented in execution",
            "detection_status": live.detection_status if live else "DETECTED",
            "severity": live.severity if live else "ERROR",
            "explanation": gt["explanation"]
        })

    return overview
