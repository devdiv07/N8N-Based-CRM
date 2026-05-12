"""Tenant model — each customer/company is a tenant."""

import enum
from sqlalchemy import Column, String, Boolean, DateTime, Enum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Plan(str, enum.Enum):
    STARTER = "STARTER"
    PRO = "PRO"
    AGENCY = "AGENCY"
    ENTERPRISE = "ENTERPRISE"


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    plan = Column(Enum(Plan), default=Plan.STARTER)
    stripe_customer_id = Column(String, unique=True)
    stripe_sub_id = Column(String, unique=True)
    settings = Column(JSON, default={})
    logo_url = Column(String)
    domain = Column(String, unique=True)
    timezone = Column(String, default="UTC")
    n8n_base_url = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    leads = relationship("Lead", back_populates="tenant", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="tenant", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="tenant", cascade="all, delete-orphan")
    automation_rules = relationship("AutomationRule", back_populates="tenant", cascade="all, delete-orphan")
    integrations = relationship("Integration", back_populates="tenant", cascade="all, delete-orphan")
    ai_prompts = relationship("AiPrompt", back_populates="tenant", cascade="all, delete-orphan")
    email_templates = relationship("EmailTemplate", back_populates="tenant", cascade="all, delete-orphan")
    sms_templates = relationship("SmsTemplate", back_populates="tenant", cascade="all, delete-orphan")
