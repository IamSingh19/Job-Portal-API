# 🚀 Job Portal API

A **production-ready** REST API for a job portal, built with **FastAPI**, **MySQL**, and **JWT authentication**.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.10+-3776ab?logo=python)](https://python.org)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-4479a1?logo=mysql)](https://mysql.com)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Setup & Installation](#-setup--installation)
- [Environment Variables](#-environment-variables)
- [Running the App](#-running-the-app)
- [Database Migrations](#-database-migrations)
- [API Endpoints](#-api-endpoints)
- [Authentication Flow](#-authentication-flow)
- [Role-Based Access Control](#-role-based-access-control)
- [Testing with Postman](#-testing-with-postman)
- [Deployment on Render](#-deployment-on-render)
- [Project Structure Deep Dive](#-project-structure-deep-dive)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 JWT Auth | Access token (30 min) + Refresh token (7 days) |
| 👥 RBAC | Job Seeker & Recruiter roles with fine-grained guards |
| 💼 Job CRUD | Create, read, update, delete jobs with ownership checks |
| 🔍 Search | Full-text search by title/description, filter by location & type |
| 📄 Pagination | All list endpoints fully paginated |
| 📥 Applications | Apply to jobs, track status (pending → shortlisted → accepted) |
| 🔖 Bookmarks | Seekers can save/unsave jobs |
| 🗄️ Alembic | Schema migrations with version history |
| 📡 Swagger | Auto-generated `/docs` and `/redoc` |
| 🌍 CORS | Configurable allowed origins |
| ⏱️ Middleware | Request timing headers, global error handler |

---

## 🏗️ Architecture

```
Request → FastAPI Router → Service Layer → SQLAlchemy ORM → MySQL
                ↓
         Pydantic Schemas (validation & serialization)
                ↓
         JWT Dependency (auth guard)
```

**Separation of Concerns:**
- `routes/` — HTTP handlers (thin controllers)
- `services/` — Business logic
- `models/` — Database schema (SQLAlchemy)
- `schemas/` — Input/output validation (Pydantic)
- `core/` — Config, security, dependencies

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Server | Uvicorn (ASGI) |
| Database | MySQL 8.0+ |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | python-jose (JWT) |
| Password | passlib + bcrypt |
| Validation | Pydantic v2 |
| Settings | pydantic-settings |

---

## 📁 Project Structure

```
job-portal-api/
├── app/
│   ├── main.py                    # App factory, middleware, router registration
│   ├── __init__.py
│   ├── database/
│   │   ├── session.py             # Engine, SessionLocal, Base
│   │   └── __init__.py
│   ├── models/
│   │   ├── user.py                # User model + UserRole enum
│   │   ├── job.py                 # Job model + JobType, ExperienceLevel
│   │   ├── application.py         # Application model + ApplicationStatus
│   │   ├── bookmark.py            # Bookmark model (bonus)
│   │   └── __init__.py            # Exports all models for Alembic
│   ├── schemas/
│   │   ├── auth.py                # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py                # UserOut, UserUpdate
│   │   ├── job.py                 # JobCreate, JobUpdate, JobOut, JobListResponse
│   │   ├── application.py         # ApplicationCreate, ApplicationOut
│   │   ├── bookmark.py            # BookmarkOut, BookmarkListResponse
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py                # POST /auth/register, /auth/login, /auth/refresh
│   │   ├── users.py               # GET/PUT /users/me
│   │   ├── jobs.py                # CRUD /jobs
│   │   ├── applications.py        # /applications endpoints
│   │   ├── bookmarks.py           # /bookmarks endpoints
│   │   └── __init__.py
│   ├── services/
│   │   ├── auth_service.py        # register, login, refresh
│   │   ├── user_service.py        # get_user, update_user
│   │   ├── job_service.py         # CRUD + search + ownership
│   │   ├── application_service.py # apply, my_apps, applicants, status
│   │   ├── bookmark_service.py    # toggle, list bookmarks
│   │   └── __init__.py
│   ├── core/
│   │   ├── config.py              # Pydantic Settings (.env)
│   │   ├── security.py            # bcrypt hash, JWT encode/decode
│   │   ├── dependencies.py        # get_db, get_current_user, require_role
│   │   └── __init__.py
│   └── utils/
│       ├── pagination.py          # Generic paginate() helper
│       └── __init__.py
├── alembic/
│   ├── env.py                     # Alembic config using our settings
│   ├── script.py.mako
│   └── versions/                  # Migration scripts live here
├── alembic.ini
├── requirements.txt
├── .env.example                   # Template — copy to .env
├── render.yaml                    # Render deployment config
├── Postman_Collection.json        # Import into Postman
└── README.md
```

---

## ⚙️ Setup & Installation

### Prerequisites

- Python 3.10+
- MySQL 8.0+ running locally or on a cloud provider
- pip / virtualenv

### 1. Clone the repository

```bash
git clone https://github.com/yourname/job-portal-api.git
cd job-portal-api
```

### 2. Create a virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in your database credentials and secret keys (see [Environment Variables](#-environment-variables)).

### 5. Create the MySQL database

```sql
CREATE DATABASE job_portal CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 🔑 Environment Variables

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | MySQL connection string | `mysql+pymysql://root:password@localhost:3306/job_portal` |
| `SECRET_KEY` | JWT access token signing key | **REQUIRED** |
| `REFRESH_SECRET_KEY` | JWT refresh token signing key | **REQUIRED** |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `ALLOWED_ORIGINS` | CORS allowed origins (comma-separated) | `http://localhost:3000` |
| `DEBUG` | Enable debug logging | `false` |

**Generate strong secrets:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## ▶️ Running the App

### Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**API is now available at:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
- Health: http://localhost:8000/health

---

## 🗄️ Database Migrations

```bash
# Generate a new migration (after changing models)
alembic revision --autogenerate -m "description of change"

# Apply all pending migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history --verbose
```

> **Note:** On first run, `Base.metadata.create_all()` in `main.py` creates all tables for development convenience. In production, always use Alembic.

---

## 📡 API Endpoints

All endpoints are prefixed with `/api/v1`.

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register as seeker or recruiter |
| `POST` | `/auth/login` | ❌ | Login, get access + refresh tokens |
| `POST` | `/auth/refresh` | ❌ | Exchange refresh token for new access token |

**Register Request:**
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "password": "password123",
  "role": "seeker"
}
```

**Login Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

---

### 👤 Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/users/me` | ✅ Any | Get own profile |
| `PUT` | `/users/me` | ✅ Any | Update own profile |

---

### 💼 Jobs

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/jobs` | ✅ | Recruiter | Create job listing |
| `GET` | `/jobs` | ❌ | — | List jobs (search, filter, paginate) |
| `GET` | `/jobs/{id}` | ❌ | — | Get job details |
| `PUT` | `/jobs/{id}` | ✅ | Recruiter (owner) | Update job |
| `DELETE` | `/jobs/{id}` | ✅ | Recruiter (owner) | Delete job |

**Query Parameters for `GET /jobs`:**

| Param | Type | Description |
|---|---|---|
| `search` | string | Search title or description |
| `location` | string | Filter by location |
| `job_type` | string | `full_time`, `part_time`, `contract`, `internship`, `remote` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 10, max: 100) |

---

### 📥 Applications

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/applications/{job_id}` | ✅ | Seeker | Apply to a job |
| `GET` | `/applications/me` | ✅ | Seeker | My applications |
| `GET` | `/applications/job/{job_id}` | ✅ | Recruiter (owner) | View applicants |
| `PATCH` | `/applications/{id}/status` | ✅ | Recruiter (owner) | Update status |

**Application Status Values:** `pending` → `reviewed` → `shortlisted` → `accepted` / `rejected`

---

### 🔖 Bookmarks (Bonus)

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/bookmarks/{job_id}` | ✅ | Seeker | Toggle bookmark (add/remove) |
| `GET` | `/bookmarks` | ✅ | Seeker | My bookmarked jobs |

---

## 🔐 Authentication Flow

```
1. POST /auth/register  → create account
2. POST /auth/login     → returns access_token + refresh_token
3. Add header: Authorization: Bearer <access_token>
4. When access_token expires (30 min):
   POST /auth/refresh with { "refresh_token": "..." }
   → returns new access_token
```

---

## 👥 Role-Based Access Control

| Action | Seeker | Recruiter |
|---|---|---|
| Register / Login | ✅ | ✅ |
| View / Update profile | ✅ | ✅ |
| View jobs | ✅ | ✅ |
| Create / Update / Delete jobs | ❌ | ✅ (own jobs only) |
| Apply to jobs | ✅ | ❌ |
| View own applications | ✅ | ❌ |
| View job applicants | ❌ | ✅ (own jobs only) |
| Update application status | ❌ | ✅ (own jobs only) |
| Bookmark jobs | ✅ | ❌ |

---

## 🧪 Testing with Postman

1. Open Postman → **Import** → select `Postman_Collection.json`
2. Set the `base_url` collection variable: `http://localhost:8000/api/v1`
3. Run **Register** to create accounts
4. Run **Login** — the test script auto-saves tokens to collection variables
5. All authenticated requests automatically use `{{access_token}}`

---

## 🌐 Deployment on Render

### Option 1: Using render.yaml (Recommended)

1. Push code to GitHub
2. In Render dashboard: **New → Blueprint** → connect your repo
3. Render reads `render.yaml` automatically
4. Set `DATABASE_URL` manually in the Render dashboard (Environment → Secret Files)

### Option 2: Manual Setup

1. **New Web Service** → GitHub repo
2. Runtime: **Python 3**
3. Build Command:
   ```bash
   pip install -r requirements.txt && alembic upgrade head
   ```
4. Start Command:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
5. Add Environment Variables from `.env.example`

### MySQL on Render

Use **PlanetScale**, **Railway**, **Aiven**, or **AWS RDS** for MySQL hosting. Set the `DATABASE_URL` environment variable accordingly.

---

## 🗂️ Database Schema

```
users
├── id (PK)
├── email (UNIQUE)
├── full_name
├── hashed_password
├── role (seeker | recruiter)
├── phone, bio, resume_url, company_name
└── is_active, created_at, updated_at

jobs
├── id (PK)
├── title, description, location
├── salary_min, salary_max
├── job_type (full_time | part_time | contract | internship | remote)
├── experience_level (entry | mid | senior | lead)
├── skills_required
├── is_active
├── recruiter_id (FK → users.id)
└── created_at, updated_at

applications
├── id (PK)
├── job_id (FK → jobs.id)
├── applicant_id (FK → users.id)
├── cover_letter
├── status (pending | reviewed | shortlisted | accepted | rejected)
├── UNIQUE(job_id, applicant_id)
└── created_at, updated_at

bookmarks
├── id (PK)
├── user_id (FK → users.id)
├── job_id (FK → jobs.id)
├── UNIQUE(user_id, job_id)
└── created_at
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m 'Add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
