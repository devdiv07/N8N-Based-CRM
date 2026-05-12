"""Audit log and usage tracking models."""

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Numeric, JSON, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    resource_id = Column(String)
    old_value = Column(JSON)
    new_value = Column(JSON)
    ip_address = Column(String)
    user_agent = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_tenant_time", "tenant_id", "created_at"),
        Index("ix_audit_resource", "tenant_id", "resource", "resource_id"),
        Index("ix_audit_user", "tenant_id", "user_id"),
    )


class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    period = Column(String, nullable=False)
    leads_created = Column(Integer, default=0)
    emails_sent = Column(Integer, default=0)
    sms_sent = Column(Integer, default=0)
    ai_tokens_used = Column(Integer, default=0)
    ai_cost_usd = Column(Numeric(8, 4), default=0)
    api_calls = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("tenant_id", "period", name="uq_usage_tenant_period"),
        Index("ix_usage_tenant", "tenant_id"),
    )
