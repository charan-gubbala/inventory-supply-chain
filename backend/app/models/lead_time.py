from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class LeadTime(Base):
    __tablename__ = "lead_times"

    lead_time_id = Column(String(64), primary_key=True, index=True)
    supplier_id = Column(String(32), ForeignKey("suppliers.supplier_id", ondelete="CASCADE"), nullable=False, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    base_lead_time_days = Column(Integer, nullable=False, default=7)
    min_order_quantity = Column(Integer, nullable=False, default=100)
    cost_per_unit = Column(Numeric(12, 2), nullable=False, default=10.0)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("base_lead_time_days > 0", name="chk_lead_time_positive"),
        CheckConstraint("min_order_quantity >= 1", name="chk_moq_positive"),
        CheckConstraint("cost_per_unit > 0", name="chk_leadtime_cost_positive"),
        Index("idx_leadtime_lookup", "sku_id", "location_id", "supplier_id"),
    )

    supplier = relationship("Supplier", back_populates="lead_times")
    sku = relationship("SKU", back_populates="lead_times")
    location = relationship("Location", back_populates="lead_times")
