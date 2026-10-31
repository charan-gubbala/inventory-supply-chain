from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.app.database import get_db
from backend.app.models.shortage import Shortage
from backend.app.services.shortage_service import ShortageService
from backend.app.services.mitigation_service import MitigationService
from backend.app.schemas.schemas import ShortageRead, MitigationOptionRead

router = APIRouter(prefix="/shortages", tags=["Shortages"])

@router.get("", response_model=List[ShortageRead])
def list_shortages(
    severity: Optional[str] = None,
    status: Optional[str] = None,
    sku_id: Optional[str] = None,
    location_id: Optional[str] = None,
    iso_week: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Shortage)
    if severity:
        query = query.filter(Shortage.severity == severity)
    if status:
        query = query.filter(Shortage.status == status)
    if sku_id:
        query = query.filter(Shortage.sku_id == sku_id)
    if location_id:
        query = query.filter(Shortage.location_id == location_id)
    if iso_week:
        query = query.filter(Shortage.iso_week == iso_week)
    return query.order_by(Shortage.shortage_quantity.desc()).offset(skip).limit(limit).all()

@router.get("/{shortage_id}", response_model=ShortageRead)
def get_shortage(shortage_id: str, db: Session = Depends(get_db)):
    shortage = db.query(Shortage).filter(Shortage.shortage_id == shortage_id).first()
    if not shortage:
        raise HTTPException(status_code=404, detail="Shortage record not found")
    return shortage

@router.post("/run-detection", response_model=List[ShortageRead])
def run_shortage_detection(iso_week: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Executes shortage detection algorithm across all negative inventory balances.
    Automatically generates ranked mitigations for detected shortages.
    """
    shortage_service = ShortageService(db)
    detected = shortage_service.detect_shortages(iso_week=iso_week)

    mitigation_service = MitigationService(db)
    for s in detected:
        mitigation_service.generate_mitigations_for_shortage(s.shortage_id)

    return detected

@router.get("/{shortage_id}/mitigations", response_model=List[MitigationOptionRead])
def get_shortage_mitigations(shortage_id: str, db: Session = Depends(get_db)):
    shortage = db.query(Shortage).filter(Shortage.shortage_id == shortage_id).first()
    if not shortage:
        raise HTTPException(status_code=404, detail="Shortage not found")

    mitigations = shortage.mitigation_options
    if not mitigations:
        # Generate on demand
        mit_service = MitigationService(db)
        mitigations = mit_service.generate_mitigations_for_shortage(shortage_id)

    return sorted(mitigations, key=lambda m: m.rank)
