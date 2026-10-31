from sqlalchemy import Column, String, Integer, DateTime, Date, Numeric, ForeignKey, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class ForecastDemand(Base):
    __tablename__ = "forecast_demands"

    demand_id = Column(String(64), primary_key=True, index=True)
    sku_id = Column(String(32), ForeignKey("skus.sku_id", ondelete="CASCADE"), nullable=False, index=True)
    location_id = Column(String(32), ForeignKey("locations.location_id", ondelete="CASCADE"), nullable=False, index=True)
    iso_week = Column(String(8), nullable=False, index=True)  # e.g., 2026W01
    forecast_quantity = Column(Integer, nullable=False)
    demand_type = Column(String(32), nullable=False, default="BASELINE")  # BASELINE, PROMOTION, SEASONAL, SPIKE
    forecast_date = Column(Date, nullable=False)
    confidence_level = Column(Numeric(5, 2), nullable=False, default=95.0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("forecast_quantity >= 0", name="chk_forecast_quantity_non_negative"),
        Index("idx_forecast_sku_loc_week", "sku_id", "location_id", "iso_week"),
    )

    sku = relationship("SKU", back_populates="demands")
    location = relationship("Location", back_populates="demands")
