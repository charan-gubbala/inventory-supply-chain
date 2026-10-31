from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.sku import SKU, SKUSubstitute
from backend.app.models.location import Location
from backend.app.models.inventory import Inventory
from backend.app.models.shortage import Shortage
from backend.app.models.mitigation_option import MitigationOption, WarehouseTransfer
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.models.purchase_order import PurchaseOrder
from backend.app.models.production_plan import ProductionPlan, ProductionCapacity, BOMHeader, BOMComponent
from backend.app.models.additional_models import EventHistory, DataQualityIssue
import json

class MitigationService:
    def __init__(self, db: Session):
        self.db = db

    def generate_mitigations_for_shortage(self, shortage_id: str) -> List[MitigationOption]:
        """
        Analyzes and produces ranked mitigation options for a detected shortage.
        Evaluates 4 core strategies:
        1. Supplier purchase
        2. Warehouse stock transfer
        3. Additional production
        4. Approved substitute SKU
        """
        shortage = self.db.query(Shortage).filter(Shortage.shortage_id == shortage_id).first()
        if not shortage:
            raise ValueError(f"Shortage {shortage_id} not found")

        # Delete existing unapproved/proposed mitigations for this shortage before regenerating
        self.db.query(MitigationOption).filter(
            MitigationOption.shortage_id == shortage_id,
            MitigationOption.approval_status == "PROPOSED"
        ).delete()
        self.db.commit()

        candidates = []

        # Strategy 1: Supplier Purchase
        supplier_options = self._evaluate_supplier_purchases(shortage)
        candidates.extend(supplier_options)

        # Strategy 2: Warehouse Transfer
        transfer_options = self._evaluate_warehouse_transfers(shortage)
        candidates.extend(transfer_options)

        # Strategy 3: Additional Production
        production_options = self._evaluate_production_options(shortage)
        candidates.extend(production_options)

        # Strategy 4: Approved Substitute SKU
        substitute_options = self._evaluate_substitutes(shortage)
        candidates.extend(substitute_options)

        # Score and rank candidates
        ranked_options = self._score_and_rank_options(shortage, candidates)

        # Save to database
        saved_options = []
        for idx, opt_data in enumerate(ranked_options, 1):
            mit_id = f"MIT-{shortage.shortage_id}-{idx:02d}"
            mit = MitigationOption(
                mitigation_id=mit_id,
                shortage_id=shortage.shortage_id,
                strategy_type=opt_data["strategy_type"],
                proposed_quantity=opt_data["proposed_quantity"],
                estimated_cost=opt_data["estimated_cost"],
                expected_arrival_date=opt_data["expected_arrival_date"],
                source_supplier_id=opt_data.get("source_supplier_id"),
                source_location_id=opt_data.get("source_location_id"),
                substitute_sku_id=opt_data.get("substitute_sku_id"),
                capacity_available=opt_data["capacity_available"],
                is_feasible=opt_data["is_feasible"],
                customer_service_impact=opt_data["customer_service_impact"],
                risk_level=opt_data["risk_level"],
                recommendation_score=opt_data["recommendation_score"],
                rank=idx,
                approval_status="PROPOSED",
                rejection_reason=opt_data.get("rejection_reason"),
                explanation=opt_data["explanation"]
            )
            self.db.add(mit)
            saved_options.append(mit)

        self.db.commit()
        return saved_options

    def approve_mitigation(self, mitigation_id: str) -> MitigationOption:
        mit = self.db.query(MitigationOption).filter(MitigationOption.mitigation_id == mitigation_id).first()
        if not mit:
            raise ValueError(f"Mitigation {mitigation_id} not found")
        if not mit.is_feasible:
            raise ValueError(f"Cannot approve infeasible mitigation option: {mit.rejection_reason}")

        mit.approval_status = "APPROVED"
        shortage = self.db.query(Shortage).filter(Shortage.shortage_id == mit.shortage_id).first()
        if shortage:
            shortage.status = "MITIGATED"

        # Log event
        evt_count = self.db.query(EventHistory).count() + 1
        evt = EventHistory(
            event_id=f"EVT-{datetime.utcnow().year}-{evt_count:08d}",
            entity_type="MITIGATION",
            entity_id=mit.mitigation_id,
            event_type="MITIGATION_APPROVED",
            payload=json.dumps({
                "mitigation_id": mit.mitigation_id,
                "strategy_type": mit.strategy_type,
                "proposed_quantity": mit.proposed_quantity,
                "estimated_cost": float(mit.estimated_cost)
            })
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(mit)
        return mit

    def reject_mitigation(self, mitigation_id: str, reason: str = "Rejected by planner") -> MitigationOption:
        mit = self.db.query(MitigationOption).filter(MitigationOption.mitigation_id == mitigation_id).first()
        if not mit:
            raise ValueError(f"Mitigation {mitigation_id} not found")

        mit.approval_status = "REJECTED"
        mit.rejection_reason = reason

        evt_count = self.db.query(EventHistory).count() + 1
        evt = EventHistory(
            event_id=f"EVT-{datetime.utcnow().year}-{evt_count:08d}",
            entity_type="MITIGATION",
            entity_id=mit.mitigation_id,
            event_type="MITIGATION_REJECTED",
            payload=json.dumps({"mitigation_id": mit.mitigation_id, "reason": reason})
        )
        self.db.add(evt)
        self.db.commit()
        self.db.refresh(mit)
        return mit

    # ------------------ Strategy Evaluators ------------------

    def _evaluate_supplier_purchases(self, shortage: Shortage) -> List[Dict[str, Any]]:
        options = []
        today = date.today()

        # Find all active lead-time records for this SKU and location
        lead_times = self.db.query(LeadTime).filter(
            LeadTime.sku_id == shortage.sku_id,
            LeadTime.location_id == shortage.location_id
        ).all()

        for lt in lead_times:
            supplier = self.db.query(Supplier).filter(
                Supplier.supplier_id == lt.supplier_id,
                Supplier.status == "ACTIVE"
            ).first()
            if not supplier:
                continue

            order_qty = max(shortage.shortage_quantity, lt.min_order_quantity)
            arrival_date = today + timedelta(days=lt.base_lead_time_days)
            cost = float(lt.cost_per_unit) * order_qty

            # Check capacity (Scenario 3)
            capacity = self.db.query(SupplierCapacity).filter(
                SupplierCapacity.supplier_id == supplier.supplier_id,
                SupplierCapacity.sku_id == shortage.sku_id
            ).first()

            has_capacity = True
            is_feasible = True
            rejection_reason = None

            if capacity:
                if order_qty > capacity.available_capacity:
                    has_capacity = False
                    is_feasible = False
                    rejection_reason = f"Supplier capacity exceeded: required {order_qty} > available {capacity.available_capacity}"
                    
                    # Log Data Quality Issue for Scenario 3
                    issue_id = f"ISSUE-CAP-{supplier.supplier_id}-{shortage.sku_id}"
                    existing_issue = self.db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == issue_id).first()
                    if not existing_issue:
                        self.db.add(DataQualityIssue(
                            issue_id=issue_id,
                            scenario_id="SCENARIO-3",
                            issue_type="CAPACITY_EXCEEDED",
                            severity="ERROR",
                            affected_table="supplier_capacities",
                            affected_record_id=capacity.capacity_id,
                            expected_outcome="Detect supplier capacity violation and reject recommendation",
                            actual_outcome=f"Purchase order of {order_qty} exceeded supplier {supplier.supplier_id} capacity of {capacity.available_capacity}",
                            detection_status="DETECTED",
                            details=json.dumps({"supplier_id": supplier.supplier_id, "requested": order_qty, "available": capacity.available_capacity})
                        ))

            # Delivery timeline check
            if arrival_date > shortage.expected_shortage_date:
                is_feasible = False
                rejection_reason = (rejection_reason + "; " if rejection_reason else "") + \
                    f"Delivery date {arrival_date} arrives after shortage deadline {shortage.expected_shortage_date}"

            options.append({
                "strategy_type": "SUPPLIER_PURCHASE",
                "proposed_quantity": order_qty,
                "estimated_cost": cost,
                "expected_arrival_date": arrival_date,
                "source_supplier_id": supplier.supplier_id,
                "source_location_id": None,
                "substitute_sku_id": None,
                "capacity_available": has_capacity,
                "is_feasible": is_feasible,
                "customer_service_impact": "LOW" if is_feasible else "HIGH",
                "risk_level": "LOW" if (supplier.rating >= 4.0 and is_feasible) else "MEDIUM",
                "rejection_reason": rejection_reason,
                "explanation": f"Purchase {order_qty} units from {supplier.name} at ${lt.cost_per_unit}/unit. Lead time: {lt.base_lead_time_days} days."
            })

        return options

    def _evaluate_warehouse_transfers(self, shortage: Shortage) -> List[Dict[str, Any]]:
        options = []
        today = date.today()

        # Check other locations that hold the same SKU
        other_inventories = self.db.query(Inventory).filter(
            Inventory.sku_id == shortage.sku_id,
            Inventory.location_id != shortage.location_id,
            Inventory.iso_week == shortage.iso_week
        ).all()

        for inv in other_inventories:
            source_loc = self.db.query(Location).filter(Location.location_id == inv.location_id).first()
            if not source_loc or source_loc.status != "ACTIVE":
                continue

            # Check surplus: available stock minus safety buffer
            surplus = inv.available_stock - 50
            is_feasible = True
            rejection_reason = None
            arrival_date = today + timedelta(days=3)  # Standard 3-day inter-warehouse transfer

            if surplus < shortage.shortage_quantity:
                is_feasible = False
                rejection_reason = f"Source location {source_loc.name} has insufficient surplus ({max(0, surplus)} < required {shortage.shortage_quantity})"

            if arrival_date > shortage.expected_shortage_date:
                is_feasible = False
                rejection_reason = (rejection_reason + "; " if rejection_reason else "") + "Transit time exceeds shortage date"

            sku = self.db.query(SKU).filter(SKU.sku_id == shortage.sku_id).first()
            unit_cost = float(sku.cost_per_unit) if sku else 10.0
            freight_cost = shortage.shortage_quantity * (unit_cost * 0.05 + 1.50)

            options.append({
                "strategy_type": "WAREHOUSE_TRANSFER",
                "proposed_quantity": shortage.shortage_quantity,
                "estimated_cost": round(freight_cost, 2),
                "expected_arrival_date": arrival_date,
                "source_supplier_id": None,
                "source_location_id": source_loc.location_id,
                "substitute_sku_id": None,
                "capacity_available": surplus >= shortage.shortage_quantity,
                "is_feasible": is_feasible,
                "customer_service_impact": "LOW" if is_feasible else "HIGH",
                "risk_level": "LOW" if is_feasible else "HIGH",
                "rejection_reason": rejection_reason,
                "explanation": f"Transfer {shortage.shortage_quantity} units from facility {source_loc.name} ({source_loc.location_id}). Transit: 3 days."
            })

        return options

    def _evaluate_production_options(self, shortage: Shortage) -> List[Dict[str, Any]]:
        options = []
        today = date.today()

        # Check if destination location is a PLANT or if a PLANT exists
        plant = self.db.query(Location).filter(Location.type == "PLANT", Location.status == "ACTIVE").first()
        if not plant:
            return options

        # Check BOM Header
        bom = self.db.query(BOMHeader).filter(
            BOMHeader.finished_sku_id == shortage.sku_id,
            BOMHeader.is_active == True
        ).first()

        if not bom:
            return options

        # Check plant capacity
        prod_cap = self.db.query(ProductionCapacity).filter(
            ProductionCapacity.location_id == plant.location_id,
            ProductionCapacity.iso_week == shortage.iso_week
        ).first()

        units_per_hour = float(prod_cap.units_per_hour) if prod_cap else 10.0
        hours_needed = shortage.shortage_quantity / max(1.0, units_per_hour)
        avail_hours = float(prod_cap.available_hours) if prod_cap else 100.0

        is_feasible = True
        rejection_reason = None

        if hours_needed > avail_hours:
            is_feasible = False
            rejection_reason = f"Production capacity exceeded: needs {hours_needed:.1f} hrs, available {avail_hours:.1f} hrs"

        # Check BOM component inventory
        for comp in bom.components:
            comp_inv = self.db.query(Inventory).filter(
                Inventory.sku_id == comp.component_sku_id,
                Inventory.location_id == plant.location_id,
                Inventory.iso_week == shortage.iso_week
            ).first()
            needed_comp_qty = float(comp.quantity_required) * shortage.shortage_quantity
            avail_comp_stock = comp_inv.available_stock if comp_inv else 0
            if avail_comp_stock < needed_comp_qty:
                is_feasible = False
                rejection_reason = (rejection_reason + "; " if rejection_reason else "") + \
                    f"Component {comp.component_sku_id} deficit: has {avail_comp_stock}, needs {int(needed_comp_qty)}"

        arrival_date = today + timedelta(days=4)
        if arrival_date > shortage.expected_shortage_date:
            is_feasible = False
            rejection_reason = (rejection_reason + "; " if rejection_reason else "") + "Production completion date exceeds deadline"

        sku = self.db.query(SKU).filter(SKU.sku_id == shortage.sku_id).first()
        unit_cost = float(sku.cost_per_unit) if sku else 20.0
        cost = unit_cost * shortage.shortage_quantity

        options.append({
            "strategy_type": "ADDITIONAL_PRODUCTION",
            "proposed_quantity": shortage.shortage_quantity,
            "estimated_cost": round(cost, 2),
            "expected_arrival_date": arrival_date,
            "source_supplier_id": None,
            "source_location_id": plant.location_id,
            "substitute_sku_id": None,
            "capacity_available": hours_needed <= avail_hours,
            "is_feasible": is_feasible,
            "customer_service_impact": "LOW" if is_feasible else "HIGH",
            "risk_level": "LOW" if is_feasible else "MEDIUM",
            "rejection_reason": rejection_reason,
            "explanation": f"Produce {shortage.shortage_quantity} units at plant {plant.name} using BOM {bom.name} (v{bom.version})."
        })

        return options

    def _evaluate_substitutes(self, shortage: Shortage) -> List[Dict[str, Any]]:
        options = []
        today = date.today()

        substitutes = self.db.query(SKUSubstitute).filter(
            SKUSubstitute.original_sku_id == shortage.sku_id
        ).all()

        for sub in substitutes:
            sub_sku = self.db.query(SKU).filter(SKU.sku_id == sub.substitute_sku_id).first()
            if not sub_sku:
                continue

            # Scenario 2 Check: Unapproved substitute rejection
            is_approved = (sub.approval_status == "APPROVED")
            is_feasible = is_approved
            rejection_reason = None

            if not is_approved:
                rejection_reason = f"Substitute SKU {sub.substitute_sku_id} is UNAPPROVED (Status: {sub.approval_status})"
                # Record Data Quality Issue for Scenario 2
                issue_id = f"ISSUE-UNAPP-SUB-{sub.original_sku_id}-{sub.substitute_sku_id}"
                existing = self.db.query(DataQualityIssue).filter(DataQualityIssue.issue_id == issue_id).first()
                if not existing:
                    self.db.add(DataQualityIssue(
                        issue_id=issue_id,
                        scenario_id="SCENARIO-2",
                        issue_type="UNAPPROVED_SUBSTITUTE",
                        severity="ERROR",
                        affected_table="sku_substitutes",
                        affected_record_id=sub.substitute_id,
                        expected_outcome="Reject unapproved substitute and do not use its quantity to cover demand",
                        actual_outcome=f"Rejected candidate substitute {sub.substitute_sku_id} due to {sub.approval_status} approval status",
                        detection_status="DETECTED",
                        details=json.dumps({"original_sku": sub.original_sku_id, "substitute_sku": sub.substitute_sku_id, "status": sub.approval_status})
                    ))

            # Stock check
            sub_inv = self.db.query(Inventory).filter(
                Inventory.sku_id == sub.substitute_sku_id,
                Inventory.location_id == shortage.location_id,
                Inventory.iso_week == shortage.iso_week
            ).first()

            conv_rate = float(sub.conversion_rate)
            needed_sub_qty = int(shortage.shortage_quantity * conv_rate)
            avail_stock = sub_inv.available_stock if sub_inv else 0

            if avail_stock < needed_sub_qty and is_approved:
                is_feasible = False
                rejection_reason = f"Substitute SKU lacks sufficient on-hand stock ({avail_stock} < {needed_sub_qty})"

            cost = float(sub_sku.cost_per_unit) * needed_sub_qty

            options.append({
                "strategy_type": "APPROVED_SUBSTITUTE",
                "proposed_quantity": needed_sub_qty,
                "estimated_cost": round(cost, 2),
                "expected_arrival_date": today,  # Immediate on-hand substitution
                "source_supplier_id": None,
                "source_location_id": None,
                "substitute_sku_id": sub.substitute_sku_id,
                "capacity_available": avail_stock >= needed_sub_qty,
                "is_feasible": is_feasible,
                "customer_service_impact": "MEDIUM" if is_feasible else "HIGH",
                "risk_level": "LOW" if is_feasible else "HIGH",
                "rejection_reason": rejection_reason,
                "explanation": f"Substitute with {sub_sku.name} ({sub.substitute_sku_id}) at conversion rate {conv_rate}x."
            })

        return options

    # ------------------ Scoring & Ranking Engine ------------------

    def _score_and_rank_options(self, shortage: Shortage, candidates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates recommendation score using documented business rules:
        Score = w_cs * S_cs + w_cost * S_cost + w_lead * S_lead - w_risk * S_risk
        Infeasible options receive score 0.00.
        """
        for opt in candidates:
            if not opt["is_feasible"]:
                opt["recommendation_score"] = 0.00
                continue

            # 1. Customer service score (100 = LOW impact / zero customer disruption)
            cs_impact = opt["customer_service_impact"]
            s_cs = 100.0 if cs_impact == "LOW" else (65.0 if cs_impact == "MEDIUM" else 20.0)

            # 2. Lead time score: early arrival vs deadline
            days_buffer = (shortage.expected_shortage_date - opt["expected_arrival_date"]).days
            s_lead = min(100.0, max(20.0, 50.0 + days_buffer * 10.0))

            # 3. Cost efficiency score: lower cost = higher score
            sku = self.db.query(SKU).filter(SKU.sku_id == shortage.sku_id).first()
            standard_cost = float(sku.cost_per_unit) * shortage.shortage_quantity if sku else 1000.0
            actual_cost = opt["estimated_cost"]
            ratio = actual_cost / max(1.0, standard_cost)
            s_cost = min(100.0, max(10.0, 100.0 - (ratio - 1.0) * 50.0))

            # 4. Risk penalty
            risk = opt["risk_level"]
            s_risk = 10.0 if risk == "LOW" else (40.0 if risk == "MEDIUM" else 80.0)

            # Weighted sum: cs (40%), cost (25%), lead (25%), risk (-10%)
            raw_score = 0.40 * s_cs + 0.25 * s_cost + 0.25 * s_lead - 0.10 * s_risk
            final_score = round(min(100.0, max(1.0, raw_score)), 2)
            opt["recommendation_score"] = final_score

        # Sort: Feasible options first by score DESC, then arrival date ASC
        sorted_candidates = sorted(
            candidates,
            key=lambda x: (1 if x["is_feasible"] else 0, x["recommendation_score"], -x["estimated_cost"]),
            reverse=True
        )

        return sorted_candidates
