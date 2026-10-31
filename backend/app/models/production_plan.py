from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class ProductionPlan(Base):
    __tablename__ = "production_plans"

    plan_id = Column(String(32), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=False, index=True)
    iso_week = Column(String(8), nullable=False, index=True)
    planned_quantity = Column(Integer, nullable=False)
    produced_quantity = Column(Integer, nullable=False, default=0)
    status = Column(String(20), nullable=False, default="PLANNED")  # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("planned_quantity > 0", name="chk_planned_quantity_positive"),
        CheckConstraint("produced_quantity >= 0", name="chk_produced_quantity_non_negative"),
    )

    sku = relationship("SKU")
    location = relationship("Location")


class ProductionCapacity(Base):
    __tablename__ = "production_capacities"

    prod_capacity_id = Column(String(64), primary_key=True, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    iso_week = Column(String(8), nullable=False, index=True)
    max_hours = Column(Numeric(8, 2), nullable=False, default=168.0)
    allocated_hours = Column(Numeric(8, 2), nullable=False, default=0.0)
    available_hours = Column(Numeric(8, 2), nullable=False, default=168.0)
    units_per_hour = Column(Numeric(8, 2), nullable=False, default=10.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    location = relationship("Location")


class BOMHeader(Base):
    __tablename__ = "bom_headers"

    bom_id = Column(String(32), primary_key=True, index=True)
    finished_sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    version = Column(String(16), nullable=False, default="1.0")
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    finished_sku = relationship("SKU")
    components = relationship("BOMComponent", back_populates="bom", cascade="all, delete-orphan")


class BOMComponent(Base):
    __tablename__ = "bom_components"

    component_id = Column(String(64), primary_key=True, index=True)
    bom_id = Column(String(32), ForeignKey("bom_headers.bom_id", ondelete="CASCADE"), nullable=False, index=True)
    component_sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=False, index=True)
    quantity_required = Column(Numeric(10, 4), nullable=False, default=1.0)
    unit_of_measure = Column(String(16), nullable=False, default="UNITS")
    scrap_rate = Column(Numeric(5, 2), nullable=False, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity_required > 0", name="chk_bom_component_qty_positive"),
    )

    bom = relationship("BOMHeader", back_populates="components")
    component_sku = relationship("SKU")
