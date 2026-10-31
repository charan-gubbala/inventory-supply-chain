import os
import sys
import json
import csv
import argparse
from datetime import datetime

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.database import SessionLocal
from backend.app.models.sku import SKU, SKUSubstitute
from backend.app.models.location import Location
from backend.app.models.forecast_demand import ForecastDemand
from backend.app.models.inventory import Inventory
from backend.app.models.supplier import Supplier
from backend.app.models.supplier_capacity import SupplierCapacity
from backend.app.models.lead_time import LeadTime
from backend.app.models.purchase_order import PurchaseOrder
from backend.app.models.production_plan import ProductionPlan
from backend.app.models.shortage import Shortage
from backend.app.models.mitigation_option import MitigationOption

def escape_sql_val(val: str) -> str:
    cleaned = val.replace("'", "''")
    return f"'{cleaned}'"

def export_all(export_dir: str = "data/exports"):
    os.makedirs(export_dir, exist_ok=True)
    db = SessionLocal()

    tables = {
        "skus": (SKU, ["sku_id", "name", "category", "unit_of_measure", "cost_per_unit", "price_per_unit", "safety_stock_quantity", "status"]),
        "locations": (Location, ["location_id", "name", "type", "capacity_units", "address", "status"]),
        "forecast_demands": (ForecastDemand, ["demand_id", "sku_id", "location_id", "iso_week", "forecast_quantity", "demand_type", "forecast_date", "confidence_level"]),
        "inventory_balances": (Inventory, ["inventory_id", "sku_id", "location_id", "iso_week", "opening_stock", "received_stock", "reserved_stock", "available_stock", "incoming_stock", "closing_stock", "projected_available_balance"]),
        "suppliers": (Supplier, ["supplier_id", "name", "rating", "on_time_delivery_rate", "status", "contact_email"]),
        "supplier_capacities": (SupplierCapacity, ["capacity_id", "supplier_id", "sku_id", "max_capacity_per_week", "allocated_capacity", "available_capacity"]),
        "lead_times": (LeadTime, ["lead_time_id", "supplier_id", "sku_id", "location_id", "base_lead_time_days", "min_order_quantity", "cost_per_unit"]),
        "purchase_orders": (PurchaseOrder, ["po_id", "supplier_id", "sku_id", "location_id", "order_quantity", "unit_cost", "total_amount", "order_date", "expected_delivery_date", "status"]),
        "production_plans": (ProductionPlan, ["plan_id", "sku_id", "location_id", "iso_week", "planned_quantity", "produced_quantity", "status", "start_date", "end_date"]),
        "shortages": (Shortage, ["shortage_id", "sku_id", "location_id", "iso_week", "shortage_quantity", "expected_shortage_date", "root_cause", "severity", "status"]),
        "mitigation_options": (MitigationOption, ["mitigation_id", "shortage_id", "strategy_type", "proposed_quantity", "estimated_cost", "expected_arrival_date", "is_feasible", "recommendation_score", "rank", "approval_status"])
    }

    print(f"=== Exporting Core Entities to {export_dir} ===")

    sql_statements = []

    for name, (model_cls, cols) in tables.items():
        records = db.query(model_cls).all()
        # 1. Export CSV
        csv_file = os.path.join(export_dir, f"{name}.csv")
        with open(csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            for rec in records:
                row = [str(getattr(rec, col)) for col in cols]
                writer.writerow(row)

        # 2. Export JSON
        json_file = os.path.join(export_dir, f"{name}.json")
        data_dicts = []
        for rec in records:
            d = {col: str(getattr(rec, col)) for col in cols}
            data_dicts.append(d)
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data_dicts, f, indent=2)

        # 3. Generate SQL seed statements
        for d in data_dicts:
            keys = ", ".join(d.keys())
            escaped_vals = [escape_sql_val(v) for v in d.values()]
            vals = ", ".join(escaped_vals)
            sql_statements.append(f"INSERT INTO {name} ({keys}) VALUES ({vals});")

        print(f"-> Exported {len(records)} records for {name} (CSV, JSON)")

    # 4. Save SQL seed data
    sql_file = os.path.join(export_dir, "seed_data.sql")
    with open(sql_file, "w", encoding="utf-8") as f:
        f.write("\n".join(sql_statements))
    print(f"-> Generated SQL seed script: {sql_file}")

    db.close()
    print("=== Export Completed Successfully ===")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export Supply Chain Data to CSV, JSON, and SQL")
    parser.add_argument("--dir", default="data/exports", help="Export target directory")
    args = parser.parse_args()
    export_all(args.dir)
