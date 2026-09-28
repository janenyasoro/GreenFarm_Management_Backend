# GreenFarm Management API

Flask REST API for managing farms and agricultural operations, including crops, livestock, health records, inventory, income, expenses, and tasks.

- Frontend: https://greenfarm-management-frontend.onrender.com/
- Backend API: https://greenfarm-management-backend-kwjs.onrender.com/
- Health: https://greenfarm-management-backend-kwjs.onrender.com/api/health

## Roles and features

- `ADMIN`: global farm and user administration through `/api/v1/admin`.
- `FARM_OWNER`: owns farms and manages their operational records.
- `FARM_WORKER`: accesses operational records for an assigned farm.
- JWT authentication, bcrypt password hashing, farm-scoped operations, dashboard summaries, and soft-deactivation of farms/accounts.

Public registration creates `FARM_OWNER` accounts only. Admins and workers are created by an administrator or the initial seed command.

## Local setup

1. Clone this repository and enter the backend directory.
2. Create and activate a virtual environment: `python3 -m venv .venv && source .venv/bin/activate`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`; set strong `SECRET_KEY`, `JWT_SECRET_KEY`, and admin seed credentials.
5. Set `DATABASE_URL` to SQLite for local development or a PostgreSQL URL for deployment.
6. Apply schema migrations where a migration history is configured: `flask --app app db upgrade`.
7. Create the initial admin: `python3 seed_admin.py`.
8. Start the API: `python3 app.py` (default `http://localhost:5000`).

The first local run creates missing tables in SQLite. For an existing deployment, back up the database, apply the migration with `flask --app app db upgrade`, then run the seed command. The seed command requires all three `ADMIN_*` variables and leaves an existing admin unchanged.

## Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | SQLAlchemy database URL | `sqlite:///greenharvest.db` |
| `SECRET_KEY` | Flask application secret | Development fallback; replace in production |
| `JWT_SECRET_KEY` | JWT signing secret | Development fallback; replace in production |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access token lifetime in seconds | `3600` |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh token lifetime in seconds | `86400` |
| `FRONTEND_ORIGIN` | Additional allowed frontend origin | GreenFarm Render frontend |
| `FLASK_ENV` | Runtime environment | `development` |
| `DEBUG` | Enable debug setting | `false` |
| `ADMIN_EMAIL` | Initial admin email for seed command | Required by seed |
| `ADMIN_PASSWORD` | Initial admin password (minimum 12 chars) | Required by seed |
| `ADMIN_NAME` | Initial admin display name | Required by seed |

Do not commit `.env` or production secrets. Render should provide production environment values through its environment settings.

## Commands

| Task | Command |
| --- | --- |
| Run development server | `python3 app.py` |
| Run production server | `gunicorn --bind 0.0.0.0:8080 app:app` |
| Seed initial admin | `python3 seed_admin.py` |
| Create migration | `flask --app app db migrate -m "describe change"` |
| Apply migrations | `flask --app app db upgrade` |
| Install dependencies | `pip install -r requirements.txt` |

This is a Python/Flask backend; frontend npm commands such as `npm run dev` and `npm run build` belong to the separate frontend repository. No test command is configured in this repository.

## Authentication

Send `Authorization: Bearer <access_token>` for protected endpoints. Login uses `POST /api/auth/login` with `{ "email": "...", "password": "..." }`. Admin-only management paths are under `/api/v1/admin`.

## API reference

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for the frontend contract, request examples, pagination/filter fields, and error responses.
