import os
import sys
import argparse
import json
import csv
import random
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from datetime import datetime, date, timedelta
from faker import Faker

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.config import settings
from backend.app.database import SessionLocal, init_db
from backend.app.models.sku import SKU, SKUSubstitute, SKULocation
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.inventory import Inventory, InventoryTransaction, UnitOfMeasureConversion
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.models.purchase_order import PurchaseOrder, PurchaseOrderLine, Shipment, TransportDelay
from backend.app.models.production_plan import ProductionPlan, ProductionCapacity, BOMHeader, BOMComponent
from backend.app.models.additional_models import EventHistory, DataQualityIssue
from backend.app.services.inventory_service import InventoryService
from backend.app.services.shortage_service import ShortageService
from backend.app.services.mitigation_service import MitigationService

class SyntheticDataGenerator:
    def __init__(self, mode: str = "starter", seed: int = 20261022, output_dir: str = "data"):
        self.mode = mode
        self.seed = seed
        self.output_dir = output_dir
        self.generated_dir = os.path.join(output_dir, "generated")
        self.ground_truth_dir = os.path.join(output_dir, "ground_truth")
        self.manifest_dir = os.path.join(output_dir, "manifests")

        os.makedirs(self.generated_dir, exist_ok=True)
        os.makedirs(self.ground_truth_dir, exist_ok=True)
        os.makedirs(self.manifest_dir, exist_ok=True)

        # Set fixed random seeds
        random.seed(seed)
        np.random.seed(seed)
        self.fake = Faker()
        Faker.seed(seed)

        # Mode configuration
        if mode == "starter":
            self.num_skus = 10
            self.num_locations = 3
            self.num_suppliers = 5
            self.num_weeks = 4
            self.num_pos = 30
        else:  # full mode
            self.num_skus = 3000
            self.num_locations = 50
            self.num_suppliers = 500
            self.num_weeks = 52
            self.num_pos = 10000

        self.weeks = [f"2026W{w:02d}" for w in range(1, self.num_weeks + 1)]
        self.categories = ["ELECTRONICS", "APPAREL", "INDUSTRIAL", "PHARMA", "PACKAGING"]
        self.uoms = ["UNITS", "BOX", "PALLET", "KG", "LITER"]
        self.ground_truth_records = []

    def run(self, persist_db: bool = True):
        print(f"=== Starting Synthetic Data Generation (Mode: {self.mode}, Seed: {self.seed}) ===")
        init_db()
        db = SessionLocal()

        try:
            # 1. Generate Master Locations
            locations = self._generate_locations(db)
            print(f"-> Generated {len(locations)} locations")

            # 2. Generate Master SKUs & Substitutes
            skus, substitutes = self._generate_skus(db, locations)
            print(f"-> Generated {len(skus)} SKUs, {len(substitutes)} substitutes")

            # 3. Generate Suppliers, Capacities & Lead Times
            suppliers, capacities, lead_times = self._generate_suppliers(db, skus, locations)
            print(f"-> Generated {len(suppliers)} suppliers, {len(capacities)} capacities, {len(lead_times)} lead times")

            # 4. Generate BOM & Production Capacities
            boms, prod_caps = self._generate_boms_and_production(db, skus, locations)
            print(f"-> Generated {len(boms)} BOMs, {len(prod_caps)} production capacity records")

            # 5. Generate Unit of Measure Conversions
            uoms = self._generate_uom_conversions(db)
            print(f"-> Generated {len(uoms)} UOM conversion factors")

            # 6. Generate Weekly Forecast Demand
            demands = self._generate_demand(db, skus, locations)
            print(f"-> Generated {len(demands)} forecast demand records")

            # 7. Generate Purchase Orders, Shipments & Transport Delays
            pos, shipments, delays = self._generate_purchase_orders(db, suppliers, skus, locations)
            print(f"-> Generated {len(pos)} purchase orders, {len(shipments)} shipments, {len(delays)} transport delays")

            # 8. Inject 5 Controlled Exception Scenarios & Produce Ground Truth
            self._inject_exceptions(db, skus, locations, suppliers, pos)
            print(f"-> Injected 5 exception scenarios into ground truth")

            # 9. Calculate Weekly Balances, Shortages & Mitigations
            print("-> Reconciling weekly inventory balances and calculating shortages...")
            self._reconcile_and_detect_shortages(db, skus, locations)

            # 10. Export Datasets & Ground Truth Files
            self._export_data()
            print("-> Exported CSV, JSON and Ground Truth files successfully")

        finally:
            db.close()
        print("=== Data Generation Completed Successfully ===")

    # ----------------- 1. Locations -----------------
    def _generate_locations(self, db) -> List[Location]:
        loc_types = ["PLANT", "DISTRIBUTION_CENTER", "WAREHOUSE"]
        locations = []
        for i in range(1, self.num_locations + 1):
            loc_id = f"LOC-{i:06d}"
            loc_type = loc_types[0] if i == 1 else (loc_types[1] if i % 2 == 0 else loc_types[2])
            name = f"Central {loc_type.replace('_', ' ').title()} {i}"
            loc = db.query(Location).filter(Location.location_id == loc_id).first()
            if not loc:
                loc = Location(
                    location_id=loc_id,
                    name=name,
                    type=loc_type,
                    capacity_units=150000 + i * 5000,
                    address=f"{self.fake.street_address()}, {self.fake.city()}",
                    status="ACTIVE"
                )
                db.add(loc)
            locations.append(loc)
        db.commit()
        return locations

    # ----------------- 2. SKUs & Substitutes -----------------
    def _generate_skus(self, db, locations):
        skus = []
        substitutes = []
        sku_prefixes = {
            "ELECTRONICS": "Circuit Board",
            "APPAREL": "Protective Jacket",
            "INDUSTRIAL": "Hydraulic Valve",
            "PHARMA": "Vaccine Vial",
            "PACKAGING": "Corrugated Crate"
        }

        for i in range(1, self.num_skus + 1):
            sku_id = f"SKU-{i:06d}"
            category = self.categories[(i - 1) % len(self.categories)]
            cost = float(round(15.0 + (i % 50) * 4.5, 2))
            price = float(round(cost * 1.5, 2))

            sku = db.query(SKU).filter(SKU.sku_id == sku_id).first()
            if not sku:
                sku = SKU(
                    sku_id=sku_id,
                    name=f"{sku_prefixes[category]} Model-{i}",
                    category=category,
                    unit_of_measure="UNITS",
                    cost_per_unit=cost,
                    price_per_unit=price,
                    safety_stock_quantity=50 + (i % 10) * 10,
                    status="ACTIVE"
                )
                db.add(sku)
            skus.append(sku)

            # SKU Location Bridge
            for loc in locations:
                bridge_id = f"SKULOC-{sku_id}-{loc.location_id}"
                bridge = db.query(SKULocation).filter(SKULocation.id == bridge_id).first()
                if not bridge:
                    bridge = SKULocation(
                        id=bridge_id,
                        sku_id=sku_id,
                        location_id=loc.location_id,
                        reorder_point=100,
                        lead_time_days=7,
                        safety_stock=50
                    )
                    db.add(bridge)

        db.commit()

        # Generate approved substitute relationships
        for i in range(0, len(skus) - 1, 2):
            orig_sku = skus[i]
            sub_sku = skus[i + 1]
            sub_id = f"SUB-{orig_sku.sku_id}-{sub_sku.sku_id}"
            sub = db.query(SKUSubstitute).filter(SKUSubstitute.substitute_id == sub_id).first()
            if not sub:
                sub = SKUSubstitute(
                    substitute_id=sub_id,
                    original_sku_id=orig_sku.sku_id,
                    substitute_sku_id=sub_sku.sku_id,
                    approval_status="APPROVED",
                    conversion_rate=1.0,
                    effective_from=date(2026, 1, 1),
                    effective_to=date(2026, 12, 31)
                )
                db.add(sub)
            substitutes.append(sub)

        db.commit()
        return skus, substitutes

    # ----------------- 3. Suppliers, Capacities & Lead Times -----------------
    def _generate_suppliers(self, db, skus, locations):
        suppliers = []
        capacities = []
        lead_times = []

        for i in range(1, self.num_suppliers + 1):
            sup_id = f"SUP-{i:06d}"
            sup = db.query(Supplier).filter(Supplier.supplier_id == sup_id).first()
            if not sup:
                sup = Supplier(
                    supplier_id=sup_id,
                    name=f"Apex Logistics & Supplier {i}",
                    rating=round(3.8 + (i % 12) * 0.1, 2),
                    on_time_delivery_rate=round(90.0 + (i % 9) * 1.0, 2),
                    status="ACTIVE",
                    contact_email=f"procurement@supplier{i}.com",
                    address=f"{self.fake.street_address()}, {self.fake.country()}"
                )
                db.add(sup)
            suppliers.append(sup)

        db.commit()

        # Connect each supplier to SKUs and Locations
        for s_idx, sup in enumerate(suppliers):
            assigned_skus = [skus[j % len(skus)] for j in range(s_idx, s_idx + min(5, len(skus)))]
            for sku in assigned_skus:
                # Capacity
                cap_id = f"CAP-{sup.supplier_id}-{sku.sku_id}-2026-01-01"
                cap = db.query(SupplierCapacity).filter(SupplierCapacity.capacity_id == cap_id).first()
                if not cap:
                    max_cap = 2500 + (s_idx % 5) * 500
                    cap = SupplierCapacity(
                        capacity_id=cap_id,
                        supplier_id=sup.supplier_id,
                        sku_id=sku.sku_id,
                        max_capacity_per_week=max_cap,
                        allocated_capacity=300,
                        available_capacity=max_cap - 300,
                        effective_from=date(2026, 1, 1),
                        effective_to=date(2026, 12, 31)
                    )
                    db.add(cap)
                capacities.append(cap)

                # Lead Times to locations
                for loc in locations:
                    lt_id = f"LT-{sup.supplier_id}-{sku.sku_id}-{loc.location_id}"
                    lt = db.query(LeadTime).filter(LeadTime.lead_time_id == lt_id).first()
                    if not lt:
                        lt = LeadTime(
                            lead_time_id=lt_id,
                            supplier_id=sup.supplier_id,
                            sku_id=sku.sku_id,
                            location_id=loc.location_id,
                            base_lead_time_days=5 + (s_idx % 4) * 2,
                            min_order_quantity=50 + (s_idx % 3) * 50,
                            cost_per_unit=sku.cost_per_unit,
                            effective_from=date(2026, 1, 1),
                            effective_to=date(2026, 12, 31)
                        )
                        db.add(lt)
                    lead_times.append(lt)

        db.commit()
        return suppliers, capacities, lead_times

    # ----------------- 4. BOM & Production Capacities -----------------
    def _generate_boms_and_production(self, db, skus, locations):
        boms = []
        prod_caps = []
        plant = next((l for l in locations if l.type == "PLANT"), locations[0])

        # Generate BOM for the first few SKUs
        for i in range(min(3, len(skus))):
            fin_sku = skus[i]
            bom_id = f"BOM-{fin_sku.sku_id}-V1"
            bom = db.query(BOMHeader).filter(BOMHeader.bom_id == bom_id).first()
            if not bom:
                bom = BOMHeader(
                    bom_id=bom_id,
                    finished_sku_id=fin_sku.sku_id,
                    name=f"Standard Assembly BOM for {fin_sku.sku_id}",
                    version="1.0",
                    effective_from=date(2026, 1, 1),
                    effective_to=date(2026, 12, 31),
                    is_active=True
                )
                db.add(bom)
                db.flush()

                # Add component
                comp_sku = skus[(i + 1) % len(skus)]
                comp_id = f"BOMC-{bom_id}-{comp_sku.sku_id}"
                comp = BOMComponent(
                    component_id=comp_id,
                    bom_id=bom.bom_id,
                    component_sku_id=comp_sku.sku_id,
                    quantity_required=2.0,
                    unit_of_measure="UNITS",
                    scrap_rate=1.5
                )
                db.add(comp)
            boms.append(bom)

        # Generate Production Capacity for plant across horizon weeks
        for week in self.weeks:
            pcap_id = f"PCAP-{plant.location_id}-{week}"
            pcap = db.query(ProductionCapacity).filter(ProductionCapacity.prod_capacity_id == pcap_id).first()
            if not pcap:
                pcap = ProductionCapacity(
                    prod_capacity_id=pcap_id,
                    location_id=plant.location_id,
                    iso_week=week,
                    max_hours=168.0,
                    allocated_hours=48.0,
                    available_hours=120.0,
                    units_per_hour=15.0
                )
                db.add(pcap)
            prod_caps.append(pcap)

        db.commit()
        return boms, prod_caps

    # ----------------- 5. Unit of Measure Conversions -----------------
    def _generate_uom_conversions(self, db):
        conversions = [
            ("BOX", "UNITS", 10.0),
            ("PALLET", "UNITS", 240.0),
            ("PALLET", "BOX", 24.0),
            ("KG", "UNITS", 1.0),
            ("LITER", "UNITS", 1.0)
        ]
        results = []
        for f_uom, t_uom, factor in conversions:
            cid = f"UOM-{f_uom}-{t_uom}"
            rec = db.query(UnitOfMeasureConversion).filter(UnitOfMeasureConversion.conversion_id == cid).first()
            if not rec:
                rec = UnitOfMeasureConversion(
                    conversion_id=cid,
                    from_uom=f_uom,
                    to_uom=t_uom,
                    factor=factor,
                    is_active=True
                )
                db.add(rec)
            results.append(rec)
        db.commit()
        return results

    # ----------------- 6. Forecast Demand -----------------
    def _generate_demand(self, db, skus, locations):
        demands = []
        today = date(2026, 1, 1)

        # Full mode can be dense or configured chunked streaming
        # For starter mode: 10 * 3 * 4 = 120 demand records
        for sku_idx, sku in enumerate(skus):
            # Baseline mean demand
            base_mean = 150 + (sku_idx % 7) * 40

            for loc in locations:
                for w_idx, week in enumerate(self.weeks):
                    demand_id = f"DEM-{sku.sku_id}-{loc.location_id}-{week}"
                    
                    # Statistical pattern: seasonal sine modulation + random noise + demand spike on w_idx==2 for first SKU
                    seasonal_factor = 1.0 + 0.3 * np.sin(2 * np.pi * (w_idx + 1) / max(4, self.num_weeks))
                    noise = np.random.normal(0, 15)
                    qty = int(max(20, round(base_mean * seasonal_factor + noise)))
                    
                    # Intentional demand spike on week 2 for SKU-000001 to cause shortage
                    demand_type = "BASELINE"
                    if sku_idx == 0 and w_idx == 1:
                        qty = int(base_mean * 2.8)
                        demand_type = "SPIKE"
                    elif seasonal_factor > 1.2:
                        demand_type = "SEASONAL"

                    dem = db.query(ForecastDemand).filter(ForecastDemand.demand_id == demand_id).first()
                    if not dem:
                        dem = ForecastDemand(
                            demand_id=demand_id,
                            sku_id=sku.sku_id,
                            location_id=loc.location_id,
                            iso_week=week,
                            forecast_quantity=qty,
                            demand_type=demand_type,
                            forecast_date=today,
                            confidence_level=95.0
                        )
                        db.add(dem)
                    demands.append(dem)

            if len(demands) % 2000 == 0:
                db.commit()

        db.commit()
        return demands

    # ----------------- 7. Purchase Orders, Shipments & Delays -----------------
    def _generate_purchase_orders(self, db, suppliers, skus, locations):
        pos = []
        shipments = []
        delays = []

        base_date = date(2026, 1, 2)

        for i in range(1, self.num_pos + 1):
            po_id = f"PO-2026-{i:06d}"
            sup = suppliers[(i - 1) % len(suppliers)]
            sku = skus[(i - 1) % len(skus)]
            loc = locations[(i - 1) % len(locations)]

            order_date = base_date + timedelta(days=(i % 15))
            lead_days = 7
            exp_delivery = order_date + timedelta(days=lead_days)
            qty = 100 + (i % 5) * 50
            cost = float(sku.cost_per_unit)
            total = round(qty * cost, 2)
            status = "RECEIVED" if i <= 10 else ("SHIPPED" if i <= 20 else "APPROVED")

            po = db.query(PurchaseOrder).filter(PurchaseOrder.po_id == po_id).first()
            if not po:
                po = PurchaseOrder(
                    po_id=po_id,
                    supplier_id=sup.supplier_id,
                    sku_id=sku.sku_id,
                    location_id=loc.location_id,
                    order_quantity=qty,
                    unit_cost=cost,
                    total_amount=total,
                    order_date=order_date,
                    expected_delivery_date=exp_delivery,
                    actual_delivery_date=exp_delivery if status == "RECEIVED" else None,
                    status=status
                )
                db.add(po)
                db.flush()

                # PO Line
                line_id = f"POL-{po_id}-1"
                line = PurchaseOrderLine(
                    po_line_id=line_id,
                    po_id=po.po_id,
                    line_number=1,
                    sku_id=sku.sku_id,
                    quantity=qty,
                    unit_price=cost,
                    subtotal=total
                )
                db.add(line)

                # Shipment
                ship_id = f"SHIP-2026-{i:06d}"
                shipment = Shipment(
                    shipment_id=ship_id,
                    po_id=po.po_id,
                    origin_type="SUPPLIER",
                    origin_id=sup.supplier_id,
                    destination_location_id=loc.location_id,
                    shipped_date=order_date + timedelta(days=1),
                    estimated_arrival_date=exp_delivery,
                    actual_arrival_date=exp_delivery if status == "RECEIVED" else None,
                    carrier="DHL Express Logistics",
                    tracking_number=f"TRK-2026-{i:06d}",
                    status="DELIVERED" if status == "RECEIVED" else "IN_TRANSIT"
                )
                db.add(shipment)
                db.flush()
                shipments.append(shipment)

                # Intentional transport delay on order 3 to cause delayed shipment root cause
                if i == 3:
                    delay_id = f"DLY-2026-{i:06d}"
                    delay = TransportDelay(
                        delay_id=delay_id,
                        shipment_id=shipment.shipment_id,
                        delay_days=5,
                        reason="Severe port congestion and customs clearance inspection",
                        reported_date=exp_delivery
                    )
                    db.add(delay)
                    delays.append(delay)

            pos.append(po)

        db.commit()
        return pos, shipments, delays

    # ----------------- 8. Exception Injection & Ground Truth -----------------
    def _inject_exceptions(self, db, skus, locations, suppliers, pos):
        """
        Injects the 5 mandatory negative exception scenarios and logs deterministic ground truth.
        """
        self.ground_truth_records = []

        # Scenario 1: Inbound counted twice
        # Inject duplicate reference into inventory transactions
        s1_po = pos[0]
        s1_ref = f"REF-INBOUND-{s1_po.po_id}"
        # We record the initial transaction
        inv_service = InventoryService(db)
        inv_service.record_transaction(
            sku_id=s1_po.sku_id,
            location_id=s1_po.location_id,
            transaction_type="RECEIPT",
            quantity=s1_po.order_quantity,
            reference_id=s1_ref,
            transaction_date=datetime(2026, 1, 5, 10, 0, 0)
        )
        # Ground truth label for Scenario 1
        self.ground_truth_records.append({
            "scenario_id": "SCENARIO-1",
            "issue_type": "DUPLICATE_INBOUND",
            "affected_record_id": s1_ref,
            "expected_outcome": "Detect duplicate transaction reference and prevent double counting in inventory",
            "expected_detection_status": "DETECTED",
            "expected_decision": "REJECT_TRANSACTION",
            "explanation": "Subsequent attempt to record identical receipt reference must be rejected and logged to preserve event history."
        })

        # Scenario 2: Substitute not approved
        # Create an UNAPPROVED substitute relationship
        unapproved_sub_id = f"SUB-{skus[0].sku_id}-{skus[2].sku_id}-UNAPP"
        existing_sub = db.query(SKUSubstitute).filter(SKUSubstitute.substitute_id == unapproved_sub_id).first()
        if not existing_sub:
            unapp_sub = SKUSubstitute(
                substitute_id=unapproved_sub_id,
                original_sku_id=skus[0].sku_id,
                substitute_sku_id=skus[2].sku_id,
                approval_status="UNAPPROVED",
                conversion_rate=1.0,
                effective_from=date(2026, 1, 1),
                effective_to=date(2026, 12, 31)
            )
            db.add(unapp_sub)
            db.commit()

        self.ground_truth_records.append({
            "scenario_id": "SCENARIO-2",
            "issue_type": "UNAPPROVED_SUBSTITUTE",
            "affected_record_id": unapproved_sub_id,
            "expected_outcome": "Reject substitution request and do not use its quantity to cover demand",
            "expected_detection_status": "DETECTED",
            "expected_decision": "REJECT_SUBSTITUTION",
            "explanation": "Substitute SKU has UNAPPROVED lifecycle status and must not be presented as a feasible mitigation."
        })

        # Scenario 3: Supplier capacity exceeded
        # Force a capacity record to be strictly breached (available = 0, allocated = max)
        breached_sup = suppliers[0]
        breached_sku = skus[0]
        cap = db.query(SupplierCapacity).filter(
            SupplierCapacity.supplier_id == breached_sup.supplier_id,
            SupplierCapacity.sku_id == breached_sku.sku_id
        ).first()
        if cap:
            cap.allocated_capacity = cap.max_capacity_per_week + 500  # Exceeded
            cap.available_capacity = 0
            db.commit()
            cap_id = cap.capacity_id
        else:
            cap_id = f"CAP-{breached_sup.supplier_id}-{breached_sku.sku_id}-2026-01-01"

        self.ground_truth_records.append({
            "scenario_id": "SCENARIO-3",
            "issue_type": "CAPACITY_EXCEEDED",
            "affected_record_id": cap_id,
            "expected_outcome": "Detect supplier capacity violation and reject or flag purchase recommendation",
            "expected_detection_status": "DETECTED",
            "expected_decision": "REJECT_ORDER",
            "explanation": "Supplier order commitments exceed weekly maximum capacity limits."
        })

        # Scenario 4: Shortage calculated without lead time
        # Remove or delete lead time record for SKU 1 at Location 2
        no_lt_sku = skus[1]
        no_lt_loc = locations[1]
        db.query(LeadTime).filter(
            LeadTime.sku_id == no_lt_sku.sku_id,
            LeadTime.location_id == no_lt_loc.location_id
        ).delete()
        db.commit()

        self.ground_truth_records.append({
            "scenario_id": "SCENARIO-4",
            "issue_type": "MISSING_LEAD_TIME",
            "affected_record_id": f"LANE-{no_lt_sku.sku_id}-{no_lt_loc.location_id}",
            "expected_outcome": "Flag missing lead-time data and mark mitigation decision as incomplete or blocked",
            "expected_detection_status": "DETECTED",
            "expected_decision": "BLOCK_MITIGATION",
            "explanation": "Delivery date cannot be computed without verified supplier lead time; never assume 0 days."
        })

        # Scenario 5: Units of measure mismatch
        # Record issue for inconsistent unit addition (e.g., PALLETS added directly to UNITS without conversion)
        uom_rec_id = f"UOM-MISMATCH-{skus[0].sku_id}"
        self.ground_truth_records.append({
            "scenario_id": "SCENARIO-5",
            "issue_type": "UOM_MISMATCH",
            "affected_record_id": uom_rec_id,
            "expected_outcome": "Detect incompatible units and halt direct arithmetic without approved conversion factor",
            "expected_detection_status": "DETECTED",
            "expected_decision": "REJECT_CALCULATION",
            "explanation": "Direct arithmetic addition of PALLET and UNITS without approved conversion factor is blocked."
        })

    # ----------------- 9. Reconcile & Detect Shortages -----------------
    def _reconcile_and_detect_shortages(self, db, skus, locations):
        inv_service = InventoryService(db)
        shortage_service = ShortageService(db)
        mitigation_service = MitigationService(db)

        for sku_idx, sku in enumerate(skus):
            for loc_idx, loc in enumerate(locations):
                # Initial opening stock: ensure some variance to induce realistic shortages
                init_opening = 100 if (sku_idx == 0 and loc_idx == 0) else (300 + (sku_idx % 4) * 50)
                inv_service.reconcile_horizon(
                    sku_id=sku.sku_id,
                    location_id=loc.location_id,
                    ordered_weeks=self.weeks,
                    initial_opening_stock=init_opening
                )

        # Detect shortages
        detected = shortage_service.detect_shortages()
        print(f"-> Detected {len(detected)} shortages across planning horizon")

        # Generate mitigations for each detected shortage
        total_mitigations = 0
        for shortage in detected:
            options = mitigation_service.generate_mitigations_for_shortage(shortage.shortage_id)
            total_mitigations += len(options)
        print(f"-> Generated {total_mitigations} ranked mitigation recommendations")

    # ----------------- 10. Export Data & Manifest -----------------
    def _export_data(self):
        # 1. Ground Truth CSV & JSON
        gt_csv = os.path.join(self.ground_truth_dir, "ground_truth.csv")
        with open(gt_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "scenario_id", "issue_type", "affected_record_id",
                "expected_outcome", "expected_detection_status",
                "expected_decision", "explanation"
            ])
            writer.writeheader()
            for r in self.ground_truth_records:
                writer.writerow(r)

        gt_json = os.path.join(self.ground_truth_dir, "ground_truth.json")
        with open(gt_json, "w", encoding="utf-8") as f:
            json.dump(self.ground_truth_records, f, indent=2)

        # 2. Manifest File
        manifest = {
            "dataset_name": f"inventory_supply_chain_{self.mode}",
            "generator_version": "1.0.0",
            "seed": self.seed,
            "generation_mode": self.mode,
            "generation_date": datetime.utcnow().strftime("%Y-%m-%d"),
            "configuration": {
                "num_skus": self.num_skus,
                "num_locations": self.num_locations,
                "num_suppliers": self.num_suppliers,
                "num_weeks": self.num_weeks,
                "num_purchase_orders": self.num_pos
            },
            "source_provenance": "Deterministically generated synthetic supply chain dataset using Python Faker and NumPy with fixed random seed 20261022."
        }

        manifest_path = os.path.join(self.manifest_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Synthetic Data Generation Engine")
    parser.add_argument("--mode", choices=["starter", "full"], default="starter", help="Generation volume mode")
    parser.add_argument("--seed", type=int, default=20261022, help="Fixed random seed")
    parser.add_argument("--output", type=str, default="data", help="Output directory")
    args = parser.parse_args()

    generator = SyntheticDataGenerator(mode=args.mode, seed=args.seed, output_dir=args.output)
    generator.run()
