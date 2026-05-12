"""Automation models — rules and execution runs linked to n8n workflows."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Numeric, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    trigger = Column(String, nullable=False)
    conditions = Column(JSON, default=[])
    actions = Column(JSON, default=[])
    n8n_workflow_id = Column(String)
    is_active = Column(Boolean, default=True)
    run_count = Column(Integer, default=0)
    last_run_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="automation_rules")
    runs = relationship("WorkflowRun", back_populates="automation_rule", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_auto_tenant_trigger", "tenant_id", "trigger", "is_active"),
    )


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    automation_rule_id = Column(String, ForeignKey("automation_rules.id", ondelete="SET NULL"))
    n8n_execution_id = Column(String)
    trigger_type = Column(String)
    trigger_data = Column(JSON, default={})
    status = Column(String, default="running")
    result = Column(JSON, default={})
    error = Column(String)
    duration_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost_usd = Column(Numeric(8, 6))
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    # Relationships
    automation_rule = relationship("AutomationRule", back_populates="runs")

    __table_args__ = (
        Index("ix_run_tenant_status", "tenant_id", "status"),
    )
