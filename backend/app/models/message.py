"""Message model — tracks all emails and SMS sent/received."""

import enum
from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MessageChannel(str, enum.Enum):
    EMAIL = "EMAIL"
    SMS = "SMS"
    WHATSAPP = "WHATSAPP"


class MessageDirection(str, enum.Enum):
    INBOUND = "INBOUND"
    OUTBOUND = "OUTBOUND"


class MessageStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    SENDING = "SENDING"
    SENT = "SENT"
    DELIVERED = "DELIVERED"
    OPENED = "OPENED"
    CLICKED = "CLICKED"
    FAILED = "FAILED"
    BOUNCED = "BOUNCED"


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    lead_id = Column(String, ForeignKey("leads.id", ondelete="SET NULL"))
    channel = Column(Enum(MessageChannel), nullable=False)
    direction = Column(Enum(MessageDirection), nullable=False)
    from_address = Column(String, nullable=False)
    to_address = Column(String, nullable=False)
    subject = Column(String)
    body = Column(String, nullable=False)
    html_body = Column(String)
    status = Column(Enum(MessageStatus), default=MessageStatus.QUEUED)
    external_id = Column(String, index=True)
    metadata = Column(JSON, default={})
    sent_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    opened_at = Column(DateTime(timezone=True))
    clicked_at = Column(DateTime(timezone=True))
    failed_at = Column(DateTime(timezone=True))
    failure_reason = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    lead = relationship("Lead", back_populates="messages")

    __table_args__ = (
        Index("ix_msg_tenant_lead", "tenant_id", "lead_id"),
        Index("ix_msg_tenant_channel", "tenant_id", "channel", "status"),
    )
