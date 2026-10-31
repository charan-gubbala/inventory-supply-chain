from sqlalchemy import Column, String, Integer, DateTime, Date, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Shortage(Base):
    __tablename__ = "shortages"

    shortage_id = Column(String(32), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    iso_week = Column(String(8), nullable=False, index=True)
    shortage_quantity = Column(Integer, nullable=False)
    expected_shortage_date = Column(Date, nullable=False)
    root_cause = Column(String(64), nullable=False)  # INSUFFICIENT_OPENING_INVENTORY, DEMAND_SPIKE, SUPPLIER_CAPACITY_CONSTRAINT, DELAYED_SHIPMENT, PRODUCTION_CAPACITY_CONSTRAINT, MISSING_LEAD_TIME
    severity = Column(String(16), nullable=False, default="MEDIUM")  # LOW, MEDIUM, HIGH, CRITICAL
    detection_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(String(20), nullable=False, default="DETECTED")  # DETECTED, MITIGATED, RESOLVED, UNRESOLVED
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("shortage_quantity > 0", name="chk_shortage_quantity_positive"),
        Index("idx_shortage_status_severity", "status", "severity"),
    )

    sku = relationship("SKU", back_populates="shortages")
    location = relationship("Location", back_populates="shortages")
    mitigation_options = relationship("MitigationOption", back_populates="shortage", cascade="all, delete-orphan")
