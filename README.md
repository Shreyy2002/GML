# Goal Management System (GMS) MVP

Production-ready Goal Management System built with Django + DRF + PostgreSQL and Next.js (App Router).

## Project Structure

```text
codex/
├── backend/
│   ├── apps/
│   │   ├── accounts/
│   │   ├── teams/
│   │   ├── goals/
│   │   ├── dashboard/
│   │   └── reports/
│   ├── config/
│   ├── requirements/
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── manage.py
├── frontend/
│   ├── app/
│   │   ├── login/
│   │   ├── register/
│   │   ├── dashboard/
│   │   ├── goals/
│   │   ├── reports/
│   │   └── admin/teams/
│   ├── components/
│   ├── hooks/
│   ├── lib/
│   ├── types/
│   └── Dockerfile
├── docker-compose.yml
├── render.yaml
└── railway.json
```

## MVP Coverage

- JWT auth (`/api/auth/register/`, `/api/auth/login/`) with role in token claims.
- Strict roles: `TEAM_MEMBER`, `EVALUATOR`, `ADMIN`.
- Goal hierarchy with `parent_goal` and levels `COMPANY`, `TEAM`, `INDIVIDUAL`.
- Lifecycle state machine:
  - `DRAFT -> PENDING -> ACTIVE -> COMPLETED -> SCORED`
  - `PENDING -> REJECTED`
  - Only `DRAFT` and `REJECTED` editable.
  - Reject requires comment.
  - Score requires both member + evaluator feedback.
- At-risk flag implemented (`>70%` timeline elapsed and `<50%` completion).
- Admin team management and evaluator assignment.
- Dashboard endpoint + frontend charts.
- Reports endpoints with CSV + PDF exports:
  - `/api/reports/individual/`
  - `/api/reports/team/`
  - `/api/reports/company/`

## API Routes

- `/api/auth/`
- `/api/teams/`
- `/api/users/`
- `/api/goals/`
- `/api/goals/{id}/submit/`
- `/api/goals/{id}/approve/`
- `/api/goals/{id}/reject/`
- `/api/goals/{id}/complete/`
- `/api/goals/{id}/score/`
- `/api/dashboard/`
- `/api/reports/individual/`
- `/api/reports/team/`
- `/api/reports/company/`

## Local Setup

### 1. Prepare environment files

Already included:

- `backend/.env`
- `frontend/.env`

You can customize from the matching `.env.example` files.

### 2. Run with Docker

```bash
docker-compose up --build
```

App URLs:

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000/api`
- Django admin: `http://localhost:8000/admin`

### 3. Create admin user

```bash
docker-compose exec backend python manage.py createsuperuser
```

## Render Deployment (Production)

This repo includes `render.yaml` for Blueprint deployment.

1. Push this repository to GitHub.
2. In Render, choose **New +** -> **Blueprint**.
3. Select your repo; Render reads `render.yaml` and creates:
   - PostgreSQL database
   - `gms-backend` web service
   - `gms-frontend` web service
4. Set `DJANGO_SECRET_KEY` in backend service environment variables.
5. Deploy.

Public URLs after deployment:

- Frontend: `https://gms-frontend.onrender.com`
- Backend: `https://gms-backend.onrender.com/api`

Update `NEXT_PUBLIC_API_BASE_URL` to your actual backend URL.

## Railway Deployment (Alternative)

1. Create PostgreSQL plugin/service.
2. Create backend and frontend services from this repo.
3. Backend:
   - Build using `backend/Dockerfile`
   - Set env vars from `backend/.env.example`
4. Frontend:
   - Build using `frontend/Dockerfile`
   - Set `NEXT_PUBLIC_API_BASE_URL` to backend public URL + `/api`

## Notes

- Backend migration files are included for required models.
- Report exports use `reportlab` for PDF and standard CSV generation.
- Frontend uses App Router, role-based guards, skeletons, optimistic updates, and responsive layout.
# GML
# GML
