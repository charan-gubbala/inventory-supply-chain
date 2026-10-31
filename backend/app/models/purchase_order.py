from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    po_id = Column(String(32), primary_key=True, index=True)
    supplier_id = Column(String(32), ForeignKey("suppliers.supplier_id"), nullable=False, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=False, index=True)
    order_quantity = Column(Integer, nullable=False)
    unit_cost = Column(Numeric(12, 2), nullable=False)
    total_amount = Column(Numeric(14, 2), nullable=False)
    order_date = Column(Date, nullable=False)
    expected_delivery_date = Column(Date, nullable=False)
    actual_delivery_date = Column(Date, nullable=True)
    status = Column(String(20), nullable=False, default="CREATED")  # CREATED, APPROVED, SHIPPED, RECEIVED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("order_quantity > 0", name="chk_po_order_quantity_positive"),
        CheckConstraint("unit_cost > 0", name="chk_po_unit_cost_positive"),
        Index("idx_po_supplier_status", "supplier_id", "status"),
        Index("idx_po_delivery_date", "expected_delivery_date", "status"),
    )

    supplier = relationship("Supplier", back_populates="purchase_orders")
    sku = relationship("SKU", back_populates="purchase_orders")
    location = relationship("Location", back_populates="purchase_orders")
    lines = relationship("PurchaseOrderLine", back_populates="purchase_order", cascade="all, delete-orphan")
    shipments = relationship("Shipment", back_populates="purchase_order")


class PurchaseOrderLine(Base):
    __tablename__ = "purchase_order_lines"

    po_line_id = Column(String(48), primary_key=True, index=True)
    po_id = Column(String(32), ForeignKey("purchase_orders.po_id", ondelete="CASCADE"), nullable=False, index=True)
    line_number = Column(Integer, nullable=False, default=1)
    sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    subtotal = Column(Numeric(14, 2), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    sku = relationship("SKU")


class Shipment(Base):
    __tablename__ = "shipments"

    shipment_id = Column(String(32), primary_key=True, index=True)
    po_id = Column(String(32), ForeignKey("purchase_orders.po_id"), nullable=True, index=True)
    origin_type = Column(String(20), nullable=False, default="SUPPLIER")  # SUPPLIER, WAREHOUSE
    origin_id = Column(String(32), nullable=False)
    destination_location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=False, index=True)
    shipped_date = Column(Date, nullable=False)
    estimated_arrival_date = Column(Date, nullable=False)
    actual_arrival_date = Column(Date, nullable=True)
    carrier = Column(String(64), nullable=True)
    tracking_number = Column(String(64), nullable=True, index=True)
    status = Column(String(20), nullable=False, default="IN_TRANSIT")  # IN_TRANSIT, DELIVERED, DELAYED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    purchase_order = relationship("PurchaseOrder", back_populates="shipments")
    destination_location = relationship("Location")
    delays = relationship("TransportDelay", back_populates="shipment", cascade="all, delete-orphan")


class TransportDelay(Base):
    __tablename__ = "transport_delays"

    delay_id = Column(String(32), primary_key=True, index=True)
    shipment_id = Column(String(32), ForeignKey("shipments.shipment_id", ondelete="CASCADE"), nullable=False, index=True)
    delay_days = Column(Integer, nullable=False)
    reason = Column(String(255), nullable=False)
    reported_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    shipment = relationship("Shipment", back_populates="delays")
