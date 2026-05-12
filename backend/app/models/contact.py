"""Contact model — deduplicated people. One contact can have many leads."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, JSON, UniqueConstraint, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    company = Column(String)
    job_title = Column(String)
    address = Column(String)
    city = Column(String)
    state = Column(String)
    country = Column(String)
    tags = Column(ARRAY(String), default=[])
    custom_fields = Column(JSON, default={})
    total_leads = Column(Integer, default=0)
    total_deals = Column(Integer, default=0)
    total_revenue = Column(Numeric(12, 2), default=0)
    lifetime_value = Column(Numeric(12, 2), default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="contacts")
    leads = relationship("Lead", back_populates="contact")
    deals = relationship("Deal", back_populates="contact")
    appointments = relationship("Appointment", back_populates="contact")
    activities = relationship("Activity", back_populates="contact")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_contact_tenant_email"),
    )
