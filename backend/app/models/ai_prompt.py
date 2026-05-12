"""AI Prompt model — per-tenant customizable AI system prompts."""

from sqlalchemy import Column, String, Boolean, DateTime, Float, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AiPrompt(Base):
    __tablename__ = "ai_prompts"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    name = Column(String, nullable=False)
    system_prompt = Column(String, nullable=False)
    model = Column(String, default="gpt-4o-mini")
    temperature = Column(Float, default=0.7)
    max_tokens = Column(Integer, default=500)
    output_format = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    tenant = relationship("Tenant", back_populates="ai_prompts")

    __table_args__ = (
        UniqueConstraint("tenant_id", "name", name="uq_ai_prompt_tenant_name"),
    )
