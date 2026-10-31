from sqlalchemy import Column, String, DateTime, Text, Index
from datetime import datetime
from backend.app.database import Base

class EventHistory(Base):
    __tablename__ = "event_histories"

    event_id = Column(String(64), primary_key=True, index=True)
    entity_type = Column(String(32), nullable=False, index=True)
    entity_id = Column(String(64), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, index=True)
    payload = Column(Text, nullable=False)  # JSON-encoded payload
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DataQualityIssue(Base):
    __tablename__ = "data_quality_issues"

    issue_id = Column(String(64), primary_key=True, index=True)
    scenario_id = Column(String(32), nullable=True, index=True)
    issue_type = Column(String(64), nullable=False, index=True)  # DUPLICATE_INBOUND, UNAPPROVED_SUBSTITUTE, CAPACITY_EXCEEDED, MISSING_LEAD_TIME, UOM_MISMATCH
    severity = Column(String(16), nullable=False, default="ERROR")  # INFO, WARNING, ERROR, CRITICAL
    affected_table = Column(String(64), nullable=False)
    affected_record_id = Column(String(64), nullable=False, index=True)
    expected_outcome = Column(Text, nullable=False)
    actual_outcome = Column(Text, nullable=False)
    detection_status = Column(String(20), nullable=False, default="DETECTED")  # DETECTED, UNDETECTED, RESOLVED
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_data_quality_type_status", "issue_type", "detection_status"),
    )
