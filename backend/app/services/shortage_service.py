from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.inventory import Inventory
from backend.app.models.shortage import Shortage
from backend.app.models.purchase_order import PurchaseOrder, Shipment, TransportDelay
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.models.production_plan import ProductionCapacity
from backend.app.models.additional_models import EventHistory
import json

class ShortageService:
    def __init__(self, db: Session):
        self.db = db

    def detect_shortages(self, iso_week: Optional[str] = None) -> List[Shortage]:
        """
        Scans inventory balances across all SKUs and locations.
        Generates shortage records whenever projected_available_balance < 0.
        Diagnoses root causes from actual supply chain indicators.
        """
        query = self.db.query(Inventory).filter(Inventory.projected_available_balance < 0)
        if iso_week:
            query = query.filter(Inventory.iso_week == iso_week)

        negative_balances = query.all()
        detected_shortages = []

        for inv in negative_balances:
            shortage_qty = abs(inv.projected_available_balance)
            
            # Retrieve demand record
            demand = self.db.query(ForecastDemand).filter(
                ForecastDemand.sku_id == inv.sku_id,
                ForecastDemand.location_id == inv.location_id,
                ForecastDemand.iso_week == inv.iso_week
            ).first()
            demand_qty = demand.forecast_quantity if demand else 1

            # Determine expected shortage date (Wednesday of the ISO week)
            expected_date = self._get_iso_week_midpoint(inv.iso_week)

            # Diagnose root cause
            root_cause = self._diagnose_root_cause(inv.sku_id, inv.location_id, inv.iso_week, demand_qty, inv.opening_stock)

            # Determine severity
            ratio = shortage_qty / max(1, demand_qty)
            if ratio >= 0.70:
                severity = "CRITICAL"
            elif ratio >= 0.35:
                severity = "HIGH"
            elif ratio >= 0.15:
                severity = "MEDIUM"
            else:
                severity = "LOW"

            # Check if shortage already recorded for this sku-location-week
            existing = self.db.query(Shortage).filter(
                Shortage.sku_id == inv.sku_id,
                Shortage.location_id == inv.location_id,
                Shortage.iso_week == inv.iso_week
            ).first()

            if not existing:
                count = self.db.query(Shortage).count() + 1
                year = expected_date.year
                shortage_id = f"SHORT-{year}-{count:06d}"

                shortage = Shortage(
                    shortage_id=shortage_id,
                    sku_id=inv.sku_id,
                    location_id=inv.location_id,
                    iso_week=inv.iso_week,
                    shortage_quantity=shortage_qty,
                    expected_shortage_date=expected_date,
                    root_cause=root_cause,
                    severity=severity,
                    detection_date=datetime.utcnow(),
                    status="DETECTED"
                )
                self.db.add(shortage)
                self.db.flush()

                # Log event
                evt_count = self.db.query(EventHistory).count() + 1
                evt = EventHistory(
                    event_id=f"EVT-{year}-{evt_count:08d}",
                    entity_type="SHORTAGE",
                    entity_id=shortage_id,
                    event_type="SHORTAGE_DETECTED",
                    payload=json.dumps({
                        "sku_id": inv.sku_id,
                        "location_id": inv.location_id,
                        "iso_week": inv.iso_week,
                        "shortage_quantity": shortage_qty,
                        "root_cause": root_cause,
                        "severity": severity
                    })
                )
                self.db.add(evt)
                detected_shortages.append(shortage)
            else:
                existing.shortage_quantity = shortage_qty
                existing.root_cause = root_cause
                existing.severity = severity
                detected_shortages.append(existing)

        self.db.commit()
        return detected_shortages

    def _diagnose_root_cause(
        self,
        sku_id: str,
        location_id: str,
        iso_week: str,
        demand_qty: int,
        opening_stock: int
    ) -> str:
        """
        Explains shortage root cause deterministically based on operational data.
        """
        # 1. Missing lead time check (Scenario 4)
        lt_records = self.db.query(LeadTime).filter(
            LeadTime.sku_id == sku_id,
            LeadTime.location_id == location_id
        ).all()
        if not lt_records:
            return "MISSING_LEAD_TIME"

        # 2. Demand spike: demand > 1.8 * average historical demand or demand_type SPIKE
        demand_rec = self.db.query(ForecastDemand).filter(
            ForecastDemand.sku_id == sku_id,
            ForecastDemand.location_id == location_id,
            ForecastDemand.iso_week == iso_week
        ).first()
        if demand_rec and demand_rec.demand_type == "SPIKE":
            return "DEMAND_SPIKE"

        avg_demand = self.db.query(func.avg(ForecastDemand.forecast_quantity)).filter(
            ForecastDemand.sku_id == sku_id
        ).scalar() or demand_qty
        if demand_qty > 1.8 * avg_demand:
            return "DEMAND_SPIKE"

        # 3. Transport delays: Check if inbound POs to this location have transport delays
        delayed_pos = self.db.query(PurchaseOrder).join(Shipment).join(TransportDelay).filter(
            PurchaseOrder.sku_id == sku_id,
            PurchaseOrder.location_id == location_id
        ).all()
        if delayed_pos:
            return "DELAYED_SHIPMENT"

        # 4. Supplier capacity constraints
        capacities = self.db.query(SupplierCapacity).filter(
            SupplierCapacity.sku_id == sku_id
        ).all()
        if capacities and all(c.available_capacity <= 0 for c in capacities):
            return "SUPPLIER_CAPACITY_CONSTRAINT"

        # 5. Production capacity constraints
        prod_caps = self.db.query(ProductionCapacity).filter(
            ProductionCapacity.location_id == location_id,
            ProductionCapacity.iso_week == iso_week
        ).all()
        if prod_caps and all(pc.available_hours <= 0 for pc in prod_caps):
            return "PRODUCTION_CAPACITY_CONSTRAINT"

        # 6. Default: Insufficient opening inventory
        return "INSUFFICIENT_OPENING_INVENTORY"

    def _get_iso_week_midpoint(self, iso_week: str) -> date:
        """
        Converts '2026W01' to Wednesday of that ISO week.
        """
        try:
            parts = iso_week.split("W")
            year = int(parts[0])
            week = int(parts[1])
            # ISO week 1 starts on Monday, day 3 is Wednesday
            first_day = date.fromisocalendar(year, week, 3)
            return first_day
        except Exception:
            return date.today()
