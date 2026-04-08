# Job Portal API

A production-ready REST API for a job portal platform, built with **FastAPI**, **SQLAlchemy**, and **JWT authentication**.

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat-square&logo=fastapi)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## Features

- **JWT Authentication** — Access token (30 min) + Refresh token (7 days)
- **Role-Based Access Control** — Separate permissions for Job Seekers and Recruiters
- **Job CRUD** — Create, list, search, update, delete job listings
- **Application Flow** — Apply to jobs, track status (pending → shortlisted → accepted)
- **Bookmarks** — Seekers can save/unsave jobs
- **Search & Pagination** — Filter jobs by title, location, type with full pagination
- **Alembic Migrations** — Version-controlled database schema
- **Swagger UI** — Auto-generated interactive API docs at `/docs`

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI 0.115 |
| Server | Uvicorn (ASGI) |
| Database | PostgreSQL / SQLite (dev) |
| ORM | SQLAlchemy 2.0 |
| Migrations | Alembic |
| Auth | python-jose (JWT) |
| Password | passlib + bcrypt |
| Validation | Pydantic v2 |
| Config | pydantic-settings |

---

## Project Structure

```
job-portal-api/
├── app/
│   ├── main.py                      # App factory, middleware, startup
│   ├── core/
│   │   ├── config.py                # Settings loaded from .env
│   │   ├── security.py              # bcrypt hashing, JWT encode/decode
│   │   └── dependencies.py          # get_db, get_current_user, require_role
│   ├── database/
│   │   └── session.py               # SQLAlchemy engine + session
│   ├── models/
│   │   ├── user.py                  # User model + UserRole enum
│   │   ├── job.py                   # Job model + JobType, ExperienceLevel
│   │   ├── application.py           # Application model + ApplicationStatus
│   │   └── bookmark.py              # Bookmark model
│   ├── schemas/
│   │   ├── auth.py                  # RegisterRequest, LoginRequest, TokenResponse
│   │   ├── user.py                  # UserOut, UserUpdate
│   │   ├── job.py                   # JobCreate, JobUpdate, JobOut
│   │   ├── application.py           # ApplicationCreate, ApplicationOut
│   │   └── bookmark.py              # BookmarkOut, BookmarkListResponse
│   ├── routes/
│   │   ├── auth.py                  # POST /auth/register, /login, /refresh
│   │   ├── users.py                 # GET/PUT /users/me
│   │   ├── jobs.py                  # CRUD /jobs
│   │   ├── applications.py          # /applications endpoints
│   │   └── bookmarks.py             # /bookmarks endpoints
│   ├── services/
│   │   ├── auth_handler.py          # register, login, token refresh logic
│   │   ├── profile_manager.py       # user profile read/update
│   │   ├── job_service.py           # job CRUD + search + ownership checks
│   │   ├── application_manager.py   # apply, view, update status
│   │   └── bookmark_manager.py      # toggle + list bookmarks
│   └── utils/
│       └── paginator.py             # Generic pagination helper
├── alembic/                         # Database migrations
├── alembic.ini
├── requirements.txt
├── render.yaml                      # Render deployment config
├── .env.example
└── Postman_Collection.json
```

---

## Getting Started

### Prerequisites

- Python 3.11+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/IamSingh19/Job-Portal-API.git
cd Job-Portal-API
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

Edit `.env` and set your values — see [Environment Variables](#environment-variables) below.

### 5. Run database migrations

```bash
alembic upgrade head
```

### 6. Start the server

```bash
uvicorn app.main:app --reload --port 8000
```

API is live at **http://localhost:8000**

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc
- Health → http://localhost:8000/health

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | DB connection string | SQLite (dev) |
| `SECRET_KEY` | JWT access token secret | **Required** |
| `REFRESH_SECRET_KEY` | JWT refresh token secret | **Required** |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token TTL | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token TTL | `7` |
| `ALLOWED_ORIGINS` | CORS origins (comma-separated) | `http://localhost:3000` |
| `DEBUG` | Enable debug logging | `false` |

Generate strong secrets:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## API Endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | ❌ | Register as seeker or recruiter |
| `POST` | `/auth/login` | ❌ | Login, receive access + refresh tokens |
| `POST` | `/auth/refresh` | ❌ | Exchange refresh token for new access token |

### Users

| Method | Endpoint | Auth | Description |
|---|---|---|---|
| `GET` | `/users/me` | ✅ | Get own profile |
| `PUT` | `/users/me` | ✅ | Update own profile |

### Jobs

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/jobs` | ✅ | Recruiter | Create job listing |
| `GET` | `/jobs` | ❌ | — | List + search jobs |
| `GET` | `/jobs/{id}` | ❌ | — | Get single job |
| `PUT` | `/jobs/{id}` | ✅ | Recruiter (owner) | Update job |
| `DELETE` | `/jobs/{id}` | ✅ | Recruiter (owner) | Delete job |

**Query parameters for `GET /jobs`:**

| Param | Type | Description |
|---|---|---|
| `search` | string | Search by title or description |
| `location` | string | Filter by location |
| `job_type` | enum | `full_time`, `part_time`, `contract`, `internship`, `remote` |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Results per page (default: 10, max: 100) |

### Applications

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/applications/{job_id}` | ✅ | Seeker | Apply to a job |
| `GET` | `/applications/me` | ✅ | Seeker | My applications |
| `GET` | `/applications/job/{job_id}` | ✅ | Recruiter (owner) | View applicants |
| `PATCH` | `/applications/{id}/status` | ✅ | Recruiter (owner) | Update status |

**Application status flow:** `pending` → `reviewed` → `shortlisted` → `accepted` / `rejected`

### Bookmarks

| Method | Endpoint | Auth | Role | Description |
|---|---|---|---|---|
| `POST` | `/bookmarks/{job_id}` | ✅ | Seeker | Toggle bookmark (add/remove) |
| `GET` | `/bookmarks` | ✅ | Seeker | My bookmarked jobs |

---

## Authentication Flow

```
1. POST /auth/register     → create your account
2. POST /auth/login        → receive access_token + refresh_token
3. Add header:               Authorization: Bearer <access_token>
4. Token expires in 30 min → POST /auth/refresh to get a new one
```

**In Swagger UI:** Click the **Authorize 🔒** button and enter `Bearer <your_access_token>`

---

## Role-Based Access Control

| Action | Seeker | Recruiter |
|---|---|---|
| Register / Login | ✅ | ✅ |
| View & update own profile | ✅ | ✅ |
| Browse job listings | ✅ | ✅ |
| Create / Update / Delete jobs | ❌ | ✅ own jobs only |
| Apply to jobs | ✅ | ❌ |
| View own applications | ✅ | ❌ |
| View job applicants | ❌ | ✅ own jobs only |
| Update application status | ❌ | ✅ own jobs only |
| Bookmark jobs | ✅ | ❌ |

---

## Deployment (Render)

This project includes a `render.yaml` for one-click deployment.

1. Push code to GitHub
2. Go to [render.com](https://render.com) → **New → Blueprint** → connect your repo
3. Add `DATABASE_URL` in the Render dashboard (use [Neon](https://neon.tech) for free PostgreSQL)
4. Set `ALLOWED_ORIGINS` to your frontend URL

Build command: `pip install -r requirements.txt && alembic upgrade head`  
Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## Testing with Postman

1. Open Postman → **Import** → select `Postman_Collection.json`
2. Set the `base_url` variable to `http://localhost:8000/api/v1`
3. Run **Register** → **Login** (tokens auto-saved to collection variables)
4. All authenticated requests use `{{access_token}}` automatically

---

## License

MIT License — feel free to use this project for learning or portfolio purposes.
