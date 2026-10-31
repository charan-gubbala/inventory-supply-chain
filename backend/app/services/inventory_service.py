from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.sku import SKU
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.inventory import Inventory, InventoryTransaction, UnitOfMeasureConversion
from backend.app.models.purchase_order import PurchaseOrder, Shipment, TransportDelay
from backend.app.models.production_plan import ProductionPlan
from backend.app.models.mitigation_option import WarehouseTransfer
from backend.app.models.additional_models import EventHistory, DataQualityIssue
import json

class InventoryService:
    def __init__(self, db: Session):
        self.db = db

    def record_transaction(
        self,
        sku_id: str,
        location_id: str,
        transaction_type: str,
        quantity: int,
        reference_id: Optional[str] = None,
        transaction_date: Optional[datetime] = None
    ) -> InventoryTransaction:
        """
        Records an inventory transaction with duplicate detection (Scenario 1).
        """
        txn_date = transaction_date or datetime.utcnow()
        
        # Scenario 1 Check: Duplicate inbound transaction detection
        if transaction_type in ["RECEIPT", "TRANSFER_IN"] and reference_id:
            existing = self.db.query(InventoryTransaction).filter(
                InventoryTransaction.reference_id == reference_id,
                InventoryTransaction.transaction_type == transaction_type,
                InventoryTransaction.sku_id == sku_id,
                InventoryTransaction.location_id == location_id
            ).first()
            if existing:
                # Log Data Quality Issue
                issue_id = f"ISSUE-DUP-{reference_id}-{int(datetime.utcnow().timestamp())}"
                issue = DataQualityIssue(
                    issue_id=issue_id,
                    scenario_id="SCENARIO-1",
                    issue_type="DUPLICATE_INBOUND",
                    severity="ERROR",
                    affected_table="inventory_transactions",
                    affected_record_id=reference_id,
                    expected_outcome="Detect duplicate transaction reference and prevent double counting in inventory",
                    actual_outcome=f"Duplicate inbound receipt reference {reference_id} was detected and blocked",
                    detection_status="DETECTED",
                    details=json.dumps({"sku_id": sku_id, "location_id": location_id, "attempted_quantity": quantity})
                )
                self.db.add(issue)
                self.db.commit()
                raise ValueError(f"Duplicate inbound transaction reference detected: {reference_id}. Transaction blocked.")

        # Deterministic transaction ID
        count = self.db.query(InventoryTransaction).count() + 1
        txn_id = f"TXN-{txn_date.year}-{count:08d}"

        txn = InventoryTransaction(
            transaction_id=txn_id,
            sku_id=sku_id,
            location_id=location_id,
            transaction_type=transaction_type,
            quantity=quantity,
            reference_id=reference_id,
            transaction_date=txn_date
        )
        self.db.add(txn)
        
        # Audit log in EventHistory
        evt_count = self.db.query(EventHistory).count() + 1
        evt = EventHistory(
            event_id=f"EVT-{txn_date.year}-{evt_count:08d}",
            entity_type="INVENTORY_TXN",
            entity_id=txn_id,
            event_type=f"TXN_{transaction_type}",
            payload=json.dumps({
                "sku_id": sku_id,
                "location_id": location_id,
                "quantity": quantity,
                "reference_id": reference_id
            })
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(txn)
        return txn

    def calculate_weekly_balance(
        self,
        sku_id: str,
        location_id: str,
        iso_week: str,
        opening_stock: int,
        adjustments: int = 0,
        reserved_stock: int = 0
    ) -> Inventory:
        """
        Reconciles weekly inventory using strict supply chain balance formula:
        Closing Stock = Opening Stock + Received Stock - Demand - Adjustments
        Next week opening stock = previous week closing stock.
        """
        # Fetch demand for this week
        demand_rec = self.db.query(ForecastDemand).filter(
            ForecastDemand.sku_id == sku_id,
            ForecastDemand.location_id == location_id,
            ForecastDemand.iso_week == iso_week
        ).first()
        demand_qty = demand_rec.forecast_quantity if demand_rec else 0

        # Sum inbound confirmed PO receipts arriving in this week
        received_stock = self._get_inbound_stock_for_week(sku_id, location_id, iso_week, include_received_only=True)
        incoming_stock = self._get_inbound_stock_for_week(sku_id, location_id, iso_week, include_received_only=False)

        # Inbound production receipts planned for this week
        prod_receipts = self._get_production_receipts_for_week(sku_id, location_id, iso_week)

        # Inter-warehouse transfer receipts planned for this week
        transfer_receipts = self._get_transfer_receipts_for_week(sku_id, location_id, iso_week)

        # Total incoming
        total_inbound_planned = incoming_stock + prod_receipts + transfer_receipts

        # Available stock = max(0, opening + received - reserved)
        available_stock = max(0, opening_stock + received_stock - reserved_stock)

        # Closing stock formula
        closing_stock = opening_stock + received_stock - demand_qty - adjustments

        # Projected Available Balance = Opening Available + Confirmed Inbound + Planned Prod + Planned Transfers - Forecast Demand
        projected_available_balance = available_stock + total_inbound_planned - demand_qty

        # SKU unit of measure
        sku = self.db.query(SKU).filter(SKU.sku_id == sku_id).first()
        uom = sku.unit_of_measure if sku else "UNITS"

        inv_id = f"INV-{sku_id}-{location_id}-{iso_week}"
        inv = self.db.query(Inventory).filter(Inventory.inventory_id == inv_id).first()

        if not inv:
            inv = Inventory(
                inventory_id=inv_id,
                sku_id=sku_id,
                location_id=location_id,
                iso_week=iso_week,
                opening_stock=opening_stock,
                received_stock=received_stock,
                reserved_stock=reserved_stock,
                available_stock=available_stock,
                incoming_stock=total_inbound_planned,
                adjustments=adjustments,
                closing_stock=closing_stock,
                projected_available_balance=projected_available_balance,
                unit_of_measure=uom
            )
            self.db.add(inv)
        else:
            inv.opening_stock = opening_stock
            inv.received_stock = received_stock
            inv.reserved_stock = reserved_stock
            inv.available_stock = available_stock
            inv.incoming_stock = total_inbound_planned
            inv.adjustments = adjustments
            inv.closing_stock = closing_stock
            inv.projected_available_balance = projected_available_balance

        self.db.commit()
        self.db.refresh(inv)
        return inv

    def reconcile_horizon(
        self,
        sku_id: str,
        location_id: str,
        ordered_weeks: List[str],
        initial_opening_stock: int
    ) -> List[Inventory]:
        """
        Runs time-phased balance reconciliation across consecutive weeks.
        Ensures Week(w+1).opening_stock == Week(w).closing_stock.
        """
        results = []
        current_opening = initial_opening_stock

        for week in ordered_weeks:
            inv = self.calculate_weekly_balance(
                sku_id=sku_id,
                location_id=location_id,
                iso_week=week,
                opening_stock=current_opening
            )
            results.append(inv)
            # Carry over closing stock to next week's opening stock
            current_opening = inv.closing_stock

        return results

    def _get_inbound_stock_for_week(
        self,
        sku_id: str,
        location_id: str,
        iso_week: str,
        include_received_only: bool = False
    ) -> int:
        """
        Sums inbound PO quantities arriving in iso_week, factoring in transport delays.
        Does NOT count cancelled POs.
        """
        query = self.db.query(PurchaseOrder).filter(
            PurchaseOrder.sku_id == sku_id,
            PurchaseOrder.location_id == location_id,
            PurchaseOrder.status != "CANCELLED"
        )
        if include_received_only:
            query = query.filter(PurchaseOrder.status == "RECEIVED")

        orders = query.all()
        total_qty = 0

        for po in orders:
            # Calculate effective arrival date with transport delays
            effective_date = po.expected_delivery_date
            if po.shipments:
                for shipment in po.shipments:
                    if shipment.delays:
                        delay_days = sum(d.delay_days for d in shipment.delays)
                        effective_date += timedelta(days=delay_days)

            # Check if effective_date belongs to this iso_week
            year, week_num, _ = effective_date.isocalendar()
            po_week = f"{year}W{week_num:02d}"
            if po_week == iso_week:
                total_qty += po.order_quantity

        return total_qty

    def _get_production_receipts_for_week(self, sku_id: str, location_id: str, iso_week: str) -> int:
        plans = self.db.query(ProductionPlan).filter(
            ProductionPlan.sku_id == sku_id,
            ProductionPlan.location_id == location_id,
            ProductionPlan.iso_week == iso_week,
            ProductionPlan.status.in_(["PLANNED", "IN_PROGRESS", "COMPLETED"])
        ).all()
        return sum(p.planned_quantity for p in plans)

    def _get_transfer_receipts_for_week(self, sku_id: str, destination_location_id: str, iso_week: str) -> int:
        transfers = self.db.query(WarehouseTransfer).filter(
            WarehouseTransfer.sku_id == sku_id,
            WarehouseTransfer.to_location_id == destination_location_id,
            WarehouseTransfer.status.in_(["PLANNED", "IN_TRANSIT", "RECEIVED"])
        ).all()
        total = 0
        for xfer in transfers:
            year, week_num, _ = xfer.arrival_date.isocalendar()
            xfer_week = f"{year}W{week_num:02d}"
            if xfer_week == iso_week:
                total += xfer.quantity
        return total
