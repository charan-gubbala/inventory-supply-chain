from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from backend.app.database import get_db
from backend.app.models.purchase_order import PurchaseOrder, PurchaseOrderLine
from backend.app.models.supplier import Supplier
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.additional_models import EventHistory
from backend.app.schemas.schemas import PurchaseOrderRead, PurchaseOrderCreate, PurchaseOrderUpdateStatus
import json

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.get("", response_model=List[PurchaseOrderRead])
def list_purchase_orders(
    status: Optional[str] = None,
    supplier_id: Optional[str] = None,
    sku_id: Optional[str] = None,
    location_id: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(PurchaseOrder)
    if status:
        query = query.filter(PurchaseOrder.status == status)
    if supplier_id:
        query = query.filter(PurchaseOrder.supplier_id == supplier_id)
    if sku_id:
        query = query.filter(PurchaseOrder.sku_id == sku_id)
    if location_id:
        query = query.filter(PurchaseOrder.location_id == location_id)
    return query.order_by(PurchaseOrder.order_date.desc()).offset(skip).limit(limit).all()

@router.post("", response_model=PurchaseOrderRead, status_code=201)
def create_purchase_order(po_in: PurchaseOrderCreate, db: Session = Depends(get_db)):
    # Validate supplier exists and active
    sup = db.query(Supplier).filter(Supplier.supplier_id == po_in.supplier_id, Supplier.status == "ACTIVE").first()
    if not sup:
        raise HTTPException(status_code=400, detail="Supplier not found or not ACTIVE")

    # Validate SKU and Location
    if not db.query(SKU).filter(SKU.sku_id == po_in.sku_id).first():
        raise HTTPException(status_code=400, detail="SKU not found")
    if not db.query(Location).filter(Location.location_id == po_in.location_id).first():
        raise HTTPException(status_code=400, detail="Location not found")

    count = db.query(PurchaseOrder).count() + 1
    year = po_in.order_date.year
    po_id = f"PO-{year}-{count:06d}"
    total = round(po_in.order_quantity * po_in.unit_cost, 2)

    po = PurchaseOrder(
        po_id=po_id,
        supplier_id=po_in.supplier_id,
        sku_id=po_in.sku_id,
        location_id=po_in.location_id,
        order_quantity=po_in.order_quantity,
        unit_cost=po_in.unit_cost,
        total_amount=total,
        order_date=po_in.order_date,
        expected_delivery_date=po_in.expected_delivery_date,
        status="CREATED"
    )
    db.add(po)
    db.flush()

    line = PurchaseOrderLine(
        po_line_id=f"POL-{po_id}-1",
        po_id=po_id,
        line_number=1,
        sku_id=po_in.sku_id,
        quantity=po_in.order_quantity,
        unit_price=po_in.unit_cost,
        subtotal=total
    )
    db.add(line)

    evt = EventHistory(
        event_id=f"EVT-{year}-{db.query(EventHistory).count() + 1:08d}",
        entity_type="PURCHASE_ORDER",
        entity_id=po_id,
        event_type="PO_CREATED",
        payload=json.dumps({"po_id": po_id, "quantity": po_in.order_quantity, "supplier": po_in.supplier_id})
    )
    db.add(evt)
    db.commit()
    db.refresh(po)
    return po

@router.patch("/{po_id}/status", response_model=PurchaseOrderRead)
def update_po_status(po_id: str, payload: PurchaseOrderUpdateStatus, db: Session = Depends(get_db)):
    po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    valid_transitions = {
        "CREATED": ["APPROVED", "CANCELLED"],
        "APPROVED": ["SHIPPED", "CANCELLED"],
        "SHIPPED": ["RECEIVED", "CANCELLED"],
        "RECEIVED": [],
        "CANCELLED": []
    }

    if payload.status not in valid_transitions.get(po.status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition PO status from {po.status} to {payload.status}"
        )

    po.status = payload.status
    if payload.status == "RECEIVED":
        po.actual_delivery_date = date.today()

    evt = EventHistory(
        event_id=f"EVT-{datetime.utcnow().year}-{db.query(EventHistory).count() + 1:08d}",
        entity_type="PURCHASE_ORDER",
        entity_id=po_id,
        event_type="PO_STATUS_UPDATED",
        payload=json.dumps({"po_id": po_id, "new_status": payload.status})
    )
    db.add(evt)
    db.commit()
    db.refresh(po)
    return po
