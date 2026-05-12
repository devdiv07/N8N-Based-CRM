"""Lead model — incoming prospects/inquiries."""

import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, ForeignKey, Integer, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class LeadSource(str, enum.Enum):
    WEBSITE = "WEBSITE"
    PHONE = "PHONE"
    REFERRAL = "REFERRAL"
    SOCIAL = "SOCIAL"
    ADS = "ADS"
    EMAIL = "EMAIL"
    CHATBOT = "CHATBOT"
    API = "API"
    MANUAL = "MANUAL"
    OTHER = "OTHER"


class LeadStatus(str, enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    BOOKED = "BOOKED"
    FOLLOWING_UP = "FOLLOWING_UP"
    COLD = "COLD"
    REACTIVATED = "REACTIVATED"
    CONVERTED = "CONVERTED"
    LOST = "LOST"


class LeadScore(str, enum.Enum):
    HOT = "HOT"
    WARM = "WARM"
    COLD = "COLD"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    source = Column(Enum(LeadSource), default=LeadSource.WEBSITE)
    source_detail = Column(String)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    score = Column(Enum(LeadScore), default=LeadScore.WARM)
    service = Column(String)
    message = Column(String)
    intent = Column(String)
    urgency = Column(String)
    ai_reason = Column(String)

    assigned_to_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    contact_id = Column(String, ForeignKey("contacts.id", ondelete="SET NULL"))

    is_booked = Column(Boolean, default=False)
    follow_up_count = Column(Integer, default=0)
    last_contact_at = Column(DateTime(timezone=True))
    next_follow_up_at = Column(DateTime(timezone=True))
    custom_fields = Column(JSON, default={})

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="leads")
    assigned_to = relationship("User", back_populates="assigned_leads")
    contact = relationship("Contact", back_populates="leads")
    deal = relationship("Deal", back_populates="lead", uselist=False)
    activities = relationship("Activity", back_populates="lead", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="lead", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="lead", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_leads_tenant_status", "tenant_id", "status"),
        Index("ix_leads_tenant_score", "tenant_id", "score"),
        Index("ix_leads_tenant_source", "tenant_id", "source"),
        Index("ix_leads_tenant_created", "tenant_id", "created_at"),
        Index("ix_leads_tenant_followup", "tenant_id", "next_follow_up_at"),
        Index("ix_leads_email", "email"),
        Index("ix_leads_phone", "phone"),
    )
