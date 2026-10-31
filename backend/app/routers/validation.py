from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from backend.app.database import get_db
from backend.app.services.validation_service import ValidationService

router = APIRouter(prefix="/validation", tags=["Validation Engine"])

@router.post("/run")
def run_validation(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Executes automated supply chain data validation across all 15 checks.
    """
    service = ValidationService(db)
    report = service.run_all_validations()
    # Also export report to data/exports/
    service.export_validation_report()
    return report

@router.get("/results")
def get_validation_results(db: Session = Depends(get_db)) -> Dict[str, Any]:
    service = ValidationService(db)
    return service.run_all_validations()
