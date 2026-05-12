# models package - import all models here for Alembic to discover
from app.models.tenant import Tenant, Plan
from app.models.user import User, Role
from app.models.lead import Lead, LeadStatus, LeadScore, LeadSource
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.appointment import Appointment, AppointmentStatus
from app.models.activity import Activity, ActivityType
from app.models.message import Message, MessageChannel, MessageStatus, MessageDirection
from app.models.task import Task, TaskPriority, TaskStatus
from app.models.automation import AutomationRule, WorkflowRun
from app.models.integration import Integration
from app.models.ai_prompt import AiPrompt
from app.models.templates import EmailTemplate, SmsTemplate
from app.models.audit import AuditLog, UsageLog

__all__ = [
    "Tenant", "Plan",
    "User", "Role",
    "Lead", "LeadStatus", "LeadScore", "LeadSource",
    "Contact",
    "Deal",
    "Appointment", "AppointmentStatus",
    "Activity", "ActivityType",
    "Message", "MessageChannel", "MessageStatus", "MessageDirection",
    "Task", "TaskPriority", "TaskStatus",
    "AutomationRule", "WorkflowRun",
    "Integration",
    "AiPrompt",
    "EmailTemplate", "SmsTemplate",
    "AuditLog", "UsageLog",
]
