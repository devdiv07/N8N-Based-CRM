"""Appointment model — scheduled consultations/meetings."""

import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AppointmentStatus(str, enum.Enum):
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"
    RESCHEDULED = "RESCHEDULED"


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    contact_id = Column(String, ForeignKey("contacts.id", ondelete="SET NULL"))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    service = Column(String)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(Enum(AppointmentStatus), default=AppointmentStatus.CONFIRMED)
    reminder_sent = Column(Boolean, default=False)
    calendar_event_id = Column(String)
    notes = Column(String)
    cancel_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="appointments")
    contact = relationship("Contact", back_populates="appointments")

    __table_args__ = (
        Index("ix_appt_tenant_start", "tenant_id", "start_time"),
        Index("ix_appt_tenant_reminder", "tenant_id", "reminder_sent", "status"),
    )
