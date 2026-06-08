# Datacore — Enterprise Asset Management System

A backend system for tracking corporate asset lifecycles across departments. Built with Django REST Framework, PostgreSQL (Supabase), Celery for async task processing, and deployed on Railway.

---

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Automated Jobs](#automated-jobs)
- [Local Setup](#local-setup)
- [Docker](#docker)
- [Deployment (Railway)](#deployment-railway)
- [Environment Variables](#environment-variables)

---

## Overview

Datacore manages the full lifecycle of corporate assets — from procurement to decommission. It handles asset assignments, inter-employee transfers, warranty and license expiry tracking, maintenance scheduling, and generates audit trails for every operation. Role-based access control governs what each user can read or modify.

**Core capabilities:**

- Asset checkout, return, and transfer between employees
- Warranty and software license expiry tracking with automated alerts
- Maintenance scheduling with status progression
- In-app notification delivery (no email dependency)
- Full audit trail: every create, update, and delete is recorded with before/after values
- Scheduled report generation (utilization, overdue, department-wise)

---

## Tech Stack

| Layer        | Technology                              |
| ------------ | --------------------------------------- |
| Language     | Python 3.10                             |
| Framework    | Django 5.0 + Django REST Framework 3.15 |
| Database     | PostgreSQL via Supabase (cloud-hosted)  |
| Task Queue   | Celery 5.4 + Redis                      |
| Scheduler    | Celery Beat + django-celery-beat        |
| Auth         | JWT (djangorestframework-simplejwt)     |
| API Docs     | drf-spectacular (Swagger + ReDoc)       |
| Static Files | WhiteNoise                              |
| Container    | Docker + Docker Compose                 |
| Deployment   | Railway                                 |

---

## Architecture

```
┌──────────────────────────────────────────────┐
│                  Railway Cloud                │
│                                               │
│  ┌──────────┐   ┌──────────┐  ┌───────────┐ │
│  │   Web    │   │  Celery  │  │  Celery   │ │
│  │ (Gunicorn│   │  Worker  │  │   Beat    │ │
│  │  + Django│   │          │  │(Scheduler)│ │
│  └────┬─────┘   └────┬─────┘  └─────┬─────┘ │
│       │              │              │        │
│       └──────────────┴──────────────┘        │
│                      │                       │
│              ┌───────▼──────┐                │
│              │    Redis     │                │
│              │  (Broker)    │                │
│              └──────────────┘                │
└──────────────────────┬───────────────────────┘
                       │
              ┌────────▼────────┐
              │    Supabase     │
              │  (PostgreSQL)   │
              └─────────────────┘
```

The web service handles all HTTP requests. Long-running or scheduled work is offloaded to Celery workers via Redis. Celery Beat triggers time-based jobs (expiry alerts, overdue detection, weekly reports). All services share the same Supabase PostgreSQL instance.

---

## Database Schema

12 tables across three categories: core operational tables, extended feature tables, and independent utility modules.

```
COMPANY ──< DEPARTMENT ──< EMPLOYEE >── ASSET_LOG >── ASSET
                                  │                      │
                                  ├──< ASSET_TRANSFER    ├──< ASSET_EXPIRY
                                  ├──< NOTIFICATION      ├──< MAINTENANCE
                                  ├──< AUDIT_LOG         └──< ASSET_TRANSFER
                                  └──< REPORT

SCHEDULER_LOG (standalone — records job execution results)
```

### Core Tables

| Table       | Purpose                                                                  |
| ----------- | ------------------------------------------------------------------------ |
| `company`   | Top-level tenant. All data is scoped under a company.                    |
| `employee`  | User records linked to a company and department.                         |
| `asset`     | Physical and software assets with condition, status, and warranty dates. |
| `asset_log` | Checkout and return records — primary assignment history.                |

### Extended Tables

| Table            | Purpose                                                                                  |
| ---------------- | ---------------------------------------------------------------------------------------- |
| `department`     | Organizational units within a company; tracks department head.                           |
| `asset_expiry`   | Warranty and license expiry dates with configurable alert windows.                       |
| `asset_transfer` | Records lateral transfers between employees with reason and timestamp.                   |
| `maintenance`    | Scheduled maintenance tasks with status progression (Pending → In Progress → Completed). |
| `notification`   | In-app notifications per employee. No email dependency.                                  |
| `audit_log`      | Append-only record of every CREATE, UPDATE, DELETE with old and new value as JSON.       |

### Independent Modules

| Table           | Purpose                                                                   |
| --------------- | ------------------------------------------------------------------------- |
| `report`        | Stores generated report snapshots as JSON; also tracks export file paths. |
| `scheduler_log` | Records every scheduled job execution: status, records processed, errors. |

---

## Project Structure

```
dataops-core/
├── apps/
│   ├── accounts/          # JWT auth, user management, permissions
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── companies/         # Company and department CRUD
│   ├── assets/            # Asset CRUD, checkout, return, history
│   │   └── filters.py     # django-filter integration
│   ├── operations/        # Transfers, maintenance, expiry
│   │   └── services.py    # Business logic layer
│   ├── notifications/     # In-app notifications
│   │   └── services.py
│   └── core/              # Shared utilities, signals, tasks, middleware
│       ├── signals.py     # Auto-registers audit log entries
│       ├── tasks.py       # Celery task definitions
│       ├── middleware.py
│       └── utils.py
├── config/
│   ├── settings/
│   │   ├── base.py        # Shared settings
│   │   ├── dev.py         # Local overrides
│   │   └── prod.py        # Production overrides
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py          # Celery app + beat schedule
├── scripts/
│   └── entrypoint.sh      # Production container entrypoint
├── nginx/
│   └── nginx.conf
├── Dockerfile
├── docker-compose.yml
├── railway.toml
├── requirements.txt
└── .env.example
```

---

## API Reference

All endpoints are under `/api/`. Full interactive documentation is available at `/api/docs/` (Swagger) and `/api/redoc/`.

### Authentication

| Method      | Endpoint                     | Access        |
| ----------- | ---------------------------- | ------------- |
| POST        | `/api/auth/login/`           | Public        |
| POST        | `/api/auth/logout/`          | Authenticated |
| POST        | `/api/auth/refresh/`         | Public        |
| GET / PATCH | `/api/auth/me/`              | Authenticated |
| POST        | `/api/auth/change-password/` | Authenticated |
| GET / POST  | `/api/auth/employees/`       | Admin         |

### Companies & Departments

| Method     | Endpoint            | Access                |
| ---------- | ------------------- | --------------------- |
| GET        | `/api/companies/`   | Authenticated         |
| POST       | `/api/companies/`   | SuperAdmin            |
| GET / POST | `/api/departments/` | Authenticated / Admin |

### Assets

| Method     | Endpoint                           | Access                |
| ---------- | ---------------------------------- | --------------------- |
| GET / POST | `/api/assets/`                     | Authenticated / Admin |
| POST       | `/api/assets/{id}/checkout/`       | Manager               |
| POST       | `/api/assets/{id}/return_asset/`   | Manager               |
| GET        | `/api/assets/{id}/history/`        | Authenticated         |
| GET        | `/api/assets/{id}/current_holder/` | Authenticated         |
| GET        | `/api/asset-logs/`                 | Authenticated         |

### Operations

| Method     | Endpoint                                  | Access                  |
| ---------- | ----------------------------------------- | ----------------------- |
| GET / POST | `/api/asset-expiries/`                    | Admin                   |
| GET / POST | `/api/transfers/`                         | Authenticated / Manager |
| GET / POST | `/api/maintenance/`                       | Authenticated / Admin   |
| POST       | `/api/maintenance/{id}/mark_in_progress/` | Manager                 |
| POST       | `/api/maintenance/{id}/complete/`         | Manager                 |

### Notifications

| Method | Endpoint                            | Access        |
| ------ | ----------------------------------- | ------------- |
| GET    | `/api/notifications/`               | Own only      |
| PATCH  | `/api/notifications/{id}/`          | Own only      |
| POST   | `/api/notifications/mark_all_read/` | Authenticated |
| GET    | `/api/notifications/unread_count/`  | Authenticated |

### Audit & Reports

| Method | Endpoint                    | Access |
| ------ | --------------------------- | ------ |
| GET    | `/api/audit-logs/`          | Admin  |
| GET    | `/api/reports/`             | Admin  |
| POST   | `/api/reports/generate/`    | Admin  |
| GET    | `/api/reports/{id}/export/` | Admin  |

### Roles

Access control follows a four-tier model: `SuperAdmin > Admin > Manager > Employee`. JWT tokens carry the role claim and are validated per endpoint via custom permission classes in `apps/accounts/permissions.py`.

---

## Automated Jobs

All jobs are registered with Celery Beat and logged to the `scheduler_log` table on every run.

| Script                     | Schedule      | What it does                                                                                                                                                      |
| -------------------------- | ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `expiry_alert_scheduler`   | Daily         | Queries `asset_expiry` for records expiring within 30, 15, or 7 days where `alert_sent = False`. Creates a notification per affected employee and flips the flag. |
| `overdue_return_processor` | Every 6 hours | Finds `asset_log` records with `returned_at = NULL` past expected return date. Flags asset as overdue, creates a notification, updates asset status.              |
| `maintenance_due_notifier` | Weekly        | Scans upcoming maintenance dates within 7 days. Creates notifications for asset owner and admin. Advances status from Pending to Due.                             |
| `weekly_report_generator`  | Every Monday  | Aggregates asset utilization per department, overdue counts, and in-maintenance assets. Writes a JSON snapshot to `report` table and exports a CSV.               |

---

## Local Setup

**Prerequisites:** Python 3.10, Node.js (optional, for tooling), a Supabase project, Redis (local or cloud via [Upstash](https://upstash.com))

### 1. Clone and create virtual environment

```powershell
git clone https://github.com/alanroy003/Datacore-Enterprise-Database-Management-System.git
cd Datacore-Enterprise-Database-Management-System

python -m venv venv
venv\Scripts\Activate.ps1
```

If `Activate.ps1` is blocked by execution policy:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure environment

```powershell
Copy-Item .env.example .env
```

Open `.env` and fill in all values. See [Environment Variables](#environment-variables) below.

Generate a secret key:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 4. Run migrations and seed

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.dev"

python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py seed_assets
```

### 5. Start the development server

```powershell
python manage.py runserver
```

In a separate terminal, start the Celery worker:

```powershell
celery -A config.celery worker -l info
```

In another terminal, start Celery Beat:

```powershell
celery -A config.celery beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

**Verify:**

- API docs: http://127.0.0.1:8000/api/docs/
- Admin panel: http://127.0.0.1:8000/admin/

---

## Docker

Docker Compose runs the web service, Celery worker, Celery Beat, and Redis. The database is always Supabase — no local PostgreSQL container.

### Build and start

```powershell
docker-compose up --build
```

Expected output:

```
redis       | Ready to accept connections
web         | Starting development server at http://0.0.0.0:8000/
celery      | celery@xxxx ready.
```

### Notes

- Inside Docker, `REDIS_URL` must be `redis://redis:6379/0` (service name, not `localhost`)
- Supabase credentials remain the same — containers connect outward

---

## Deployment (Railway)

Railway runs three services from the same repository: the web process (Gunicorn), the Celery worker, and Celery Beat. Redis is provisioned as a Railway-managed service.

### 1. Install Railway CLI and log in

```powershell
npm install -g @railway/cli
railway login
```

### 2. Initialize and deploy

```powershell
railway init
railway up
```

### 3. Add Redis on Railway

Railway Dashboard → your project → **New Service → Database → Redis**. Copy the `REDIS_URL` from its Variables tab.

### 4. Add Celery Worker service

New Service → GitHub Repo (same repo). Name: `celery-worker`.
Start command:

```
celery -A config.celery worker -l info --concurrency=2
```

### 5. Add Celery Beat service

New Service → GitHub Repo (same repo). Name: `celery-beat`.
Start command:

```
celery -A config.celery beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### 6. Set environment variables

Set these on **all three services** in Railway's Variables tab. See [Environment Variables](#environment-variables) below.

For the database in production, use Supabase's **Transaction Pooler** (port 6543) instead of the direct connection.

### 7. Create superuser and seed on Railway

```powershell
railway run python manage.py createsuperuser
railway run python manage.py seed_data
railway run python manage.py seed_assets
```

### Verify deployment

| Check                         | Expected               |
| ----------------------------- | ---------------------- |
| POST `/api/auth/login/`       | 200 with tokens        |
| GET `/api/assets/` with token | 200 with seeded assets |
| GET `/api/docs/`              | Swagger UI loads       |
| GET `/admin/`                 | Admin login page       |
| Railway `celery-worker` logs  | `celery@xxx ready.`    |

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values below.

```
# Django
DJANGO_SECRET_KEY=
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_SETTINGS_MODULE=config.settings.dev

# Supabase (Direct connection — local dev)
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=
DB_HOST=db.xxxxxxxxxxxx.supabase.co
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0
```

**Production differences:**

- `DJANGO_DEBUG=False`
- `DJANGO_SETTINGS_MODULE=config.settings.prod`
- `DJANGO_ALLOWED_HOSTS=<yourapp>.railway.app`
- Use Supabase Transaction Pooler: `DB_HOST=aws-0-<region>.pooler.supabase.com`, `DB_PORT=6543`, `DB_USER=postgres.<project-ref>`
- `REDIS_URL` from Railway Redis service

> Never commit `.env`. It is listed in `.gitignore`.

---

## Notes

- All migrations are committed. Do not run `makemigrations` in production.
- The `audit_log` table is append-only. Write access is handled exclusively through Django signals in `apps/core/signals.py`.
- Static files are served by WhiteNoise in production. `collectstatic` runs in the Railway start command.
- Scheduler jobs record their own execution status in `scheduler_log`. Check this table when debugging missed or failed jobs.
