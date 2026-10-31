from sqlalchemy import Column, String, Integer, DateTime, Numeric, ForeignKey, CheckConstraint, Index, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Inventory(Base):
    __tablename__ = "inventory_balances"

    inventory_id = Column(String(64), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    iso_week = Column(String(8), nullable=False, index=True)
    opening_stock = Column(Integer, nullable=False, default=0)
    received_stock = Column(Integer, nullable=False, default=0)
    reserved_stock = Column(Integer, nullable=False, default=0)
    available_stock = Column(Integer, nullable=False, default=0)
    incoming_stock = Column(Integer, nullable=False, default=0)
    adjustments = Column(Integer, nullable=False, default=0)
    closing_stock = Column(Integer, nullable=False, default=0)
    projected_available_balance = Column(Integer, nullable=False, default=0)
    unit_of_measure = Column(String(16), nullable=False, default="UNITS")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("received_stock >= 0", name="chk_received_stock_non_negative"),
        CheckConstraint("reserved_stock >= 0", name="chk_reserved_stock_non_negative"),
        CheckConstraint("incoming_stock >= 0", name="chk_incoming_stock_non_negative"),
        Index("idx_inventory_sku_loc_week", "sku_id", "location_id", "iso_week"),
    )

    sku = relationship("SKU", back_populates="inventory_records")
    location = relationship("Location", back_populates="inventory_records")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    transaction_id = Column(String(64), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    transaction_type = Column(String(32), nullable=False)  # RECEIPT, SHIPMENT, ADJUSTMENT, RESERVATION, TRANSFER_OUT, TRANSFER_IN
    quantity = Column(Integer, nullable=False)
    reference_id = Column(String(64), nullable=True, index=True)
    transaction_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UnitOfMeasureConversion(Base):
    __tablename__ = "uom_conversions"

    conversion_id = Column(String(32), primary_key=True, index=True)
    from_uom = Column(String(16), nullable=False)
    to_uom = Column(String(16), nullable=False)
    factor = Column(Numeric(10, 4), nullable=False, default=1.0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
