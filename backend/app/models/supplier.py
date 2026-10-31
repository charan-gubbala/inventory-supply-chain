from sqlalchemy import Column, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Supplier(Base):
    __tablename__ = "suppliers"

    supplier_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    rating = Column(Numeric(3, 2), nullable=False, default=4.0)
    on_time_delivery_rate = Column(Numeric(5, 2), nullable=False, default=95.0)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE, SUSPENDED
    contact_email = Column(String(255), nullable=True)
    address = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("rating >= 1.00 AND rating <= 5.00", name="chk_supplier_rating_range"),
        CheckConstraint("on_time_delivery_rate >= 0.00 AND on_time_delivery_rate <= 100.00", name="chk_supplier_otd_range"),
    )

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    capacities = relationship("SupplierCapacity", back_populates="supplier", cascade="all, delete-orphan")
    lead_times = relationship("LeadTime", back_populates="supplier", cascade="all, delete-orphan")
