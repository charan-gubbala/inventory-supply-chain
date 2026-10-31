from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, Boolean, ForeignKey, CheckConstraint, Index, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class MitigationOption(Base):
    __tablename__ = "mitigation_options"

    mitigation_id = Column(String(48), primary_key=True, index=True)
    shortage_id = Column(String(32), ForeignKey("shortages.shortage_id", ondelete="CASCADE"), nullable=False, index=True)
    strategy_type = Column(String(32), nullable=False)  # SUPPLIER_PURCHASE, WAREHOUSE_TRANSFER, ADDITIONAL_PRODUCTION, APPROVED_SUBSTITUTE
    proposed_quantity = Column(Integer, nullable=False)
    estimated_cost = Column(Numeric(12, 2), nullable=False, default=0.0)
    expected_arrival_date = Column(Date, nullable=False)
    source_supplier_id = Column(String(32), ForeignKey("suppliers.supplier_id"), nullable=True, index=True)
    source_location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=True, index=True)
    substitute_sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=True, index=True)
    capacity_available = Column(Boolean, nullable=False, default=True)
    is_feasible = Column(Boolean, nullable=False, default=True)
    customer_service_impact = Column(String(16), nullable=False, default="LOW")  # HIGH, MEDIUM, LOW
    risk_level = Column(String(16), nullable=False, default="LOW")  # LOW, MEDIUM, HIGH
    recommendation_score = Column(Numeric(6, 2), nullable=False, default=0.0)
    rank = Column(Integer, nullable=False, default=1)
    approval_status = Column(String(20), nullable=False, default="PROPOSED")  # PROPOSED, APPROVED, REJECTED
    rejection_reason = Column(String(255), nullable=True)
    explanation = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("proposed_quantity > 0", name="chk_proposed_quantity_positive"),
        CheckConstraint("recommendation_score >= 0.00 AND recommendation_score <= 100.00", name="chk_recommendation_score_range"),
        Index("idx_mitigation_shortage_rank", "shortage_id", "rank"),
    )

    shortage = relationship("Shortage", back_populates="mitigation_options")
    source_supplier = relationship("Supplier")
    source_location = relationship("Location")
    substitute_sku = relationship("SKU")


class WarehouseTransfer(Base):
    __tablename__ = "warehouse_transfers"

    transfer_id = Column(String(32), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id"), nullable=False, index=True)
    from_location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=False, index=True)
    to_location_id = Column(String(32), ForeignKey("locations.location_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    lead_time_days = Column(Integer, nullable=False, default=3)
    status = Column(String(20), nullable=False, default="PLANNED")  # PLANNED, IN_TRANSIT, RECEIVED, CANCELLED
    ship_date = Column(Date, nullable=False)
    arrival_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("quantity > 0", name="chk_transfer_quantity_positive"),
        CheckConstraint("from_location_id != to_location_id", name="chk_transfer_different_locations"),
        Index("idx_transfer_status", "status", "arrival_date"),
    )

    sku = relationship("SKU")
    from_location = relationship("Location", foreign_keys=[from_location_id])
    to_location = relationship("Location", foreign_keys=[to_location_id])
