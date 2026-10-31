from sqlalchemy import Column, String, Integer, DateTime, Date, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class SupplierCapacity(Base):
    __tablename__ = "supplier_capacities"

    capacity_id = Column(String(64), primary_key=True, index=True)
    supplier_id = Column(String(32), ForeignKey("suppliers.supplier_id", ondelete="CASCADE"), nullable=False, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    max_capacity_per_week = Column(Integer, nullable=False, default=1000)
    allocated_capacity = Column(Integer, nullable=False, default=0)
    available_capacity = Column(Integer, nullable=False, default=1000)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("max_capacity_per_week > 0", name="chk_supplier_max_capacity_positive"),
        CheckConstraint("allocated_capacity >= 0", name="chk_supplier_allocated_capacity_non_negative"),
    )

    supplier = relationship("Supplier", back_populates="capacities")
    sku = relationship("SKU", back_populates="supplier_capacities")
