# GTM Lead Operations Automation

A workflow-first CRM automation system for the inbound lead lifecycle: intake, instant response, qualification, appointment booking, follow-up, reminders, reactivation, and operational reporting.

The project uses **n8n as the executable automation layer** and keeps each lifecycle stage in a separate workflow instead of coupling the entire GTM process into one large automation. A FastAPI/PostgreSQL backend scaffold defines the longer-term data model and service boundary.

> **Project status:** portfolio/prototype system. The n8n workflows and local test harness are implemented; the FastAPI service is currently a scaffold (configuration, database/model layer, health endpoint) and is not yet the primary execution path. The empty `frontend/`, `infra/`, and `docs/` directories are placeholders for future work. This repository does **not** claim production deployment or customer-scale usage.

## What it automates

```text
Inbound lead / missed call
          |
          v
     Orchestrator
          |
          v
  Instant response
          |
          v
   Qualification
          |
          +------------------+
          |                  |
          v                  v
 Appointment            Lead nurture
   booking                   |
      |                      v
      v                  Follow-up
Calendar conflict             |
  detection                   v
      |                   Reminders
      v                      |
CRM / activity                v
   update                Reactivation
          \                  /
           \                /
            v              v
          Dashboard / reporting
```

## Workflow map

| Workflow | Responsibility |
| --- | --- |
| `WF0_Orchestrator` | Receives inbound lead data, validates it, classifies intent, and routes work into the appropriate lifecycle workflow. |
| `WF1_Instant_Response` | Generates the first response, records lead activity, and triggers internal visibility. |
| `WF2_Missed_Call` | Handles missed-call follow-up, creates a lead record, and sends an internal alert. |
| `WF3_SMS_Qualification` | Qualifies a lead from message context and records the resulting state. |
| `WF4_Appointment_Booking` | Validates requested date/time, checks Google Calendar availability, creates appointments when possible, and handles conflicts. |
| `WF5_FollowUp` | Runs delayed follow-up for leads that have not progressed. |
| `WF6_Reminders` | Sends appointment reminders and updates lead/appointment state. |
| `WF7_Dashboard` | Aggregates CRM data into an operational sales report. |
| `WF8_Reactivation` | Re-engages older leads and records the outcome. |

The exported workflow definitions live in [`n8n/workflows/`](n8n/workflows/). The filenames intentionally retain their current exported names because [`n8n/deploy_clean.js`](n8n/deploy_clean.js) references them directly.

## Engineering shape

This is not a single n8n canvas with every concern mixed together. The system separates orchestration, response generation, qualification, booking, follow-up, reminders, reactivation, and reporting so each stage can be changed and reasoned about independently.

Key pieces:

- **Webhook intake and routing** for new lead events.
- **LLM-assisted classification / response generation** behind explicit workflow steps.
- **Google Sheets** as the lightweight CRM/reporting store used by the exported workflows.
- **Google Calendar** for appointment availability and event creation.
- **Email-driven customer and team notifications** in the current workflow exports.
- **FastAPI + SQLAlchemy/PostgreSQL scaffold** for a service-backed CRM path.
- **Redis / n8n / Postgres local stack** through Docker Compose.
- **CLI-style smoke harness** in [`n8n/test_all.js`](n8n/test_all.js) covering lead, booking, reactivation, and invalid-input requests against the intake webhook.

## Example booking path

The booking workflow is deliberately not just “send a calendar link”. It models the operational branch:

```text
Booking request
     |
     v
Validate requested date/time
     |
     v
Check Google Calendar
     |
  +--+----------------+
  |                   |
available         unavailable
  |                   |
  v                   v
create event      generate alternatives
  |                   |
  v                   v
update CRM        notify customer
  |
  v
confirmation + team notification
```

That separation matters in GTM automation because a timeout, conflict, missing field, or duplicate action should not silently become a bad customer interaction.

## Repository structure

```text
backend/              FastAPI/PostgreSQL service scaffold
  app/
    config.py         environment-based configuration
    database.py       async database setup
    models/           CRM domain models
n8n/
  workflows/          exported lifecycle workflows
  deploy_clean.js     deployment/patch helper for workflow imports
  test_all.js         webhook smoke-test harness
docker-compose.yml    local Postgres + Redis + n8n stack
frontend/             placeholder (not implemented yet)
infra/                placeholder (not implemented yet)
docs/                 placeholder (not implemented yet)
```

The backend model layer includes CRM concepts such as leads, contacts, deals, appointments, messages, activities, tasks, automations, integrations, audit records, and AI-prompt metadata. The HTTP layer is intentionally still minimal today.

## Run locally

### 1. Start the local services

Create a `.env` from `.env.example`, change the local credentials, then run:

```bash
docker compose up -d
```

Local defaults:

- n8n: `http://localhost:5678`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`

### 2. Import/configure the n8n workflows

Import the JSON workflows from [`n8n/workflows/`](n8n/workflows/) and configure the required credentials/integration identifiers in n8n (OpenAI, Google Sheets, Google Calendar, and email delivery as applicable).

The repository does not include production credentials.

### 3. Exercise the intake path

With the intake webhook available at `http://localhost:5678/webhook/ai-sales/intake`:

```bash
node n8n/test_all.js all
```

Or run one case:

```bash
node n8n/test_all.js lead
node n8n/test_all.js book
node n8n/test_all.js reactivate
node n8n/test_all.js bad_input
```

The harness uses synthetic example records and reports the HTTP response for each scenario.

## Why this project exists

Lead operations often accumulate manual glue: copy a lead into a sheet, respond, qualify, check a calendar, create an appointment, remind the customer, follow up later, and compile a report. The point of this project is to turn those steps into explicit, inspectable workflows with clear boundaries rather than rely on a person remembering the next action.

For GTM engineering, the interesting part is less “using n8n” and more the systems problem underneath it: **what event starts a workflow, what state must be carried forward, what should happen on a branch/failure, and which actions must not be duplicated.**

## Current limitations

- This is a prototype/portfolio system, not a production SaaS deployment.
- The FastAPI backend is not yet wired as the system of record for the n8n workflows.
- The current exported workflows use Google Sheets for lightweight persistence/reporting.
- Integration-specific identifiers in workflow exports must be configured for your own environment before use.
- The smoke harness checks end-to-end webhook behavior; it is not a full automated test suite for every external integration.

## License

MIT — see [`LICENSE`](LICENSE).
