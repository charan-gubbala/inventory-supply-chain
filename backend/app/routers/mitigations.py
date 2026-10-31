from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Optional
from backend.app.database import get_db
from backend.app.services.mitigation_service import MitigationService
from backend.app.schemas.schemas import MitigationOptionRead

router = APIRouter(prefix="/mitigations", tags=["Mitigation Recommendations"])

@router.post("/{mitigation_id}/approve", response_model=MitigationOptionRead)
def approve_mitigation(mitigation_id: str, db: Session = Depends(get_db)):
    service = MitigationService(db)
    try:
        approved = service.approve_mitigation(mitigation_id)
        return approved
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{mitigation_id}/reject", response_model=MitigationOptionRead)
def reject_mitigation(
    mitigation_id: str,
    reason: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    service = MitigationService(db)
    try:
        rejected = service.reject_mitigation(mitigation_id, reason=reason or "Rejected by user")
        return rejected
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
