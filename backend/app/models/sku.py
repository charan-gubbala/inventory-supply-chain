from sqlalchemy import Column, String, Numeric, Integer, DateTime, Date, CheckConstraint, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class SKU(Base):
    __tablename__ = "skus"

    sku_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(64), nullable=False)  # ELECTRONICS, APPAREL, INDUSTRIAL, PHARMA, PACKAGING
    unit_of_measure = Column(String(16), nullable=False, default="UNITS")  # UNITS, BOX, PALLET, KG, LITER
    cost_per_unit = Column(Numeric(12, 2), nullable=False, default=0.0)
    price_per_unit = Column(Numeric(12, 2), nullable=False, default=0.0)
    safety_stock_quantity = Column(Integer, nullable=False, default=50)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, DISCONTINUED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("cost_per_unit >= 0", name="chk_sku_cost_positive"),
        CheckConstraint("price_per_unit >= cost_per_unit", name="chk_sku_price_above_cost"),
    )

    # Relationships
    demands = relationship("ForecastDemand", back_populates="sku", cascade="all, delete-orphan")
    inventory_records = relationship("Inventory", back_populates="sku", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="sku")
    shortages = relationship("Shortage", back_populates="sku")
    supplier_capacities = relationship("SupplierCapacity", back_populates="sku")
    lead_times = relationship("LeadTime", back_populates="sku")


class SKUSubstitute(Base):
    __tablename__ = "sku_substitutes"

    substitute_id = Column(String(64), primary_key=True, index=True)
    original_sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    substitute_sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    approval_status = Column(String(20), nullable=False, default="APPROVED")  # APPROVED, UNAPPROVED, PENDING
    conversion_rate = Column(Numeric(8, 4), nullable=False, default=1.0)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("original_sku_id != substitute_sku_id", name="chk_substitute_different"),
    )

    original_sku = relationship("SKU", foreign_keys=[original_sku_id])
    substitute_sku = relationship("SKU", foreign_keys=[substitute_sku_id])


class SKULocation(Base):
    __tablename__ = "sku_locations"

    id = Column(String(64), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    reorder_point = Column(Integer, nullable=False, default=100)
    lead_time_days = Column(Integer, nullable=False, default=7)
    safety_stock = Column(Integer, nullable=False, default=50)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
