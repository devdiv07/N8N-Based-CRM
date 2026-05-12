"""Activity model — timeline of all events for leads and contacts."""

import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ActivityType(str, enum.Enum):
    LEAD_CREATED = "LEAD_CREATED"
    LEAD_UPDATED = "LEAD_UPDATED"
    STATUS_CHANGED = "STATUS_CHANGED"
    SCORE_CHANGED = "SCORE_CHANGED"
    EMAIL_SENT = "EMAIL_SENT"
    EMAIL_OPENED = "EMAIL_OPENED"
    EMAIL_CLICKED = "EMAIL_CLICKED"
    SMS_SENT = "SMS_SENT"
    SMS_RECEIVED = "SMS_RECEIVED"
    CALL_MISSED = "CALL_MISSED"
    CALL_COMPLETED = "CALL_COMPLETED"
    APPOINTMENT_BOOKED = "APPOINTMENT_BOOKED"
    APPOINTMENT_REMINDED = "APPOINTMENT_REMINDED"
    APPOINTMENT_CANCELLED = "APPOINTMENT_CANCELLED"
    AI_CLASSIFIED = "AI_CLASSIFIED"
    AI_RESPONDED = "AI_RESPONDED"
    FOLLOW_UP_SENT = "FOLLOW_UP_SENT"
    REACTIVATION_SENT = "REACTIVATION_SENT"
    NOTE_ADDED = "NOTE_ADDED"
    TASK_CREATED = "TASK_CREATED"
    TASK_COMPLETED = "TASK_COMPLETED"
    DEAL_CREATED = "DEAL_CREATED"
    DEAL_STAGE_CHANGED = "DEAL_STAGE_CHANGED"
    DEAL_WON = "DEAL_WON"
    DEAL_LOST = "DEAL_LOST"


class Activity(Base):
    __tablename__ = "activities"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="CASCADE"))
    contact_id = Column(String, ForeignKey("contacts.id", ondelete="SET NULL"))
    performed_by_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    type = Column(Enum(ActivityType), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String)
    metadata = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="activities")
    contact = relationship("Contact", back_populates="activities")
    performed_by = relationship("User", back_populates="activities")

    __table_args__ = (
        Index("ix_activity_lead_time", "tenant_id", "lead_id", "created_at"),
        Index("ix_activity_contact_time", "tenant_id", "contact_id", "created_at"),
        Index("ix_activity_type", "tenant_id", "type"),
    )
