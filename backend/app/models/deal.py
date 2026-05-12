"""Deal model — sales opportunities linked to leads."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Deal(Base):
    __tablename__ = "deals"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="CASCADE"), unique=True)
    contact_id = Column(String, ForeignKey("contacts.id", ondelete="SET NULL"))
    title = Column(String, nullable=False)
    value = Column(Numeric(12, 2))
    currency = Column(String, default="USD")
    stage = Column(String, default="new")
    probability = Column(Integer, default=0)
    expected_close_date = Column(DateTime(timezone=True))
    closed_at = Column(DateTime(timezone=True))
    lost_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="deal")
    contact = relationship("Contact", back_populates="deals")

    __table_args__ = (
        Index("ix_deals_tenant_stage", "tenant_id", "stage"),
    )
