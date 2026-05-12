"""Email and SMS template models."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, ARRAY, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    html_body = Column(String)
    variables = Column(ARRAY(String), default=[])
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="email_templates")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_email_tpl_tenant_name"),
    )


class SmsTemplate(Base):
    __tablename__ = "sms_templates"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    body = Column(String, nullable=False)
    variables = Column(ARRAY(String), default=[])
    category = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="sms_templates")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_sms_tpl_tenant_name"),
    )
