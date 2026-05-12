"""Task model — action items assigned to team members."""

import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class TaskPriority(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="SET NULL"))
    assignee_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"))
    title = Column(String, nullable=False)
    description = Column(String)
    due_date = Column(DateTime(timezone=True))
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="tasks")
    assignee = relationship("User", back_populates="tasks")

    __table_args__ = (
        Index("ix_task_tenant_assignee", "tenant_id", "assignee_id", "status"),
        Index("ix_task_tenant_due", "tenant_id", "due_date"),
    )
