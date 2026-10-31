from sqlalchemy import Column, String, Integer, DateTime, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from backend.app.database import Base

class Location(Base):
    __tablename__ = "locations"

    location_id = Column(String(32), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(32), nullable=False)  # WAREHOUSE, DISTRIBUTION_CENTER, PLANT
    capacity_units = Column(Integer, nullable=False, default=100000)
    address = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="ACTIVE")  # ACTIVE, INACTIVE
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("capacity_units > 0", name="chk_location_capacity_positive"),
    )

    # Relationships
    demands = relationship("ForecastDemand", back_populates="location", cascade="all, delete-orphan")
    inventory_records = relationship("Inventory", back_populates="location", cascade="all, delete-orphan")
    purchase_orders = relationship("PurchaseOrder", back_populates="location")
    shortages = relationship("Shortage", back_populates="location")
    lead_times = relationship("LeadTime", back_populates="location")
