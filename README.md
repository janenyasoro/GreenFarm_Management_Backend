# GreenHarvest Farm Management API

GreenHarvest is a RESTful backend for managing day-to-day farm operations. It gives authenticated users a single place to track crops, livestock and animal health, inventory, income, expenses, and farm tasks, while providing dashboard data for quicker operational decisions.

The API is built with Flask and SQLAlchemy and is designed to be consumed by a separate web frontend.

**Live API:** [https://greenfarm-management-backend-kwjs.onrender.com/](https://greenfarm-management-backend-kwjs.onrender.com/)

**Health check:** [https://greenfarm-management-backend-kwjs.onrender.com/api/health](https://greenfarm-management-backend-kwjs.onrender.com/api/health)

## Features

- Secure user registration, login, profile management, account activation/deactivation, and password changes.
- JWT-protected API endpoints with role-aware administrative actions.
- Farm-scoped crop records, including planting dates, harvest dates, yield, category, stage, and notes.
- Livestock records and linked health history for vaccinations, checkups, and treatments.
- Financial tracking for income and expenses.
- Inventory monitoring with quantities, units, and reorder levels.
- Task planning with due dates, priority, and status.
- Dashboard summary, crop-yield, and finance-by-category data.
- SQLite for straightforward local development and PostgreSQL support for production.
- CORS support for local and deployed frontend applications.

## Technology

| Area | Tools |
| --- | --- |
| API framework | Flask 3 |
| Database / ORM | SQLAlchemy, Flask-SQLAlchemy |
| Migrations | Alembic, Flask-Migrate |
| Authentication | Flask-JWT-Extended, Flask-Bcrypt |
| Database options | SQLite, PostgreSQL |
| Production server | Gunicorn |

## Project structure

```text
.
├── app.py                 # Application factory, blueprints, CORS, health checks
├── config.py              # Environment-based application configuration
├── extensions.py          # Flask extension instances
├── models.py              # SQLAlchemy data models
├── routes/                # API blueprints by feature
├── migrations/            # Alembic migration configuration
├── requirements.txt       # Python dependencies
├── Procfile               # Production process definition
└── .env.example           # Environment-variable template
```

## Getting started

### Prerequisites

- Python 3.10 or later
- `pip`
- PostgreSQL (only when using PostgreSQL instead of the default SQLite database)

### Installation

1. Clone the repository and enter it.

   ```bash
   git clone <repository-url>
   cd GreenFarm_Management_Backend
   ```

2. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, use `.venv\\Scripts\\Activate.ps1`.

3. Install the dependencies.

   ```bash
   pip install -r requirements.txt
   ```

4. Create your local environment file from the template.

   ```bash
   cp .env.example .env
   ```

5. Set strong values for `SECRET_KEY` and `JWT_SECRET_KEY` in `.env`. Keep `.env` private and never commit production secrets.

6. Start the API.

   ```bash
   python app.py
   ```

The API runs at `http://localhost:5000` by default. On first local run, the application creates its SQLite tables automatically.

### Verify the service

```bash
curl http://localhost:5000/api/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "GreenHarvest API",
  "environment": "development",
  "version": "1.0.0"
}
```

## Configuration

The application reads configuration from environment variables. `.env.example` lists the available settings.

| Variable | Purpose | Local default |
| --- | --- | --- |
| `SECRET_KEY` | Flask session/application secret | Development-only fallback |
| `JWT_SECRET_KEY` | Secret used to sign JWTs | Development-only fallback |
| `DATABASE_URL` | SQLite or PostgreSQL connection URL | `sqlite:///greenharvest.db` |
| `FRONTEND_ORIGIN` | Allowed frontend origin for CORS | `http://localhost:3000` |
| `JWT_ACCESS_TOKEN_EXPIRES` | Access-token lifetime in seconds | `3600` |
| `JWT_REFRESH_TOKEN_EXPIRES` | Refresh-token lifetime in seconds | `86400` |
| `FLASK_ENV` | Application environment | `development` |
| `DEBUG` | Enables Flask debugging when `true` | `false` |

For PostgreSQL, set a valid URL such as:

```env
DATABASE_URL=postgresql://username:password@hostname:5432/greenharvest
```

The configuration also accepts legacy `postgres://` URLs and converts them to `postgresql://`.

## Authentication

Register a user, then log in to receive an access token. Send that token with every protected request:

```http
Authorization: Bearer <access_token>
```

### Register

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Jane Farmer",
    "email": "jane@example.com",
    "password": "secure-password",
    "role": "owner"
  }'
```

Passwords must contain at least six characters. Valid user roles in the current data model are `owner`, `admin`, and `worker`.

### Login

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"jane@example.com","password":"secure-password"}'
```

The response includes `access_token` (as well as compatibility aliases `accessToken` and `token`) and the signed-in user record.

## API overview

All endpoints below are prefixed with `/api`. Except for health checks and registration/login, endpoints require a bearer access token. Resources are scoped to the current user's farm.

| Area | Endpoint | Methods | Purpose |
| --- | --- | --- | --- |
| Service | `/health` | `GET` | Health check |
| Service | `/` | `GET` | API endpoint index |
| Authentication | `/auth/register` | `POST` | Create an account |
| Authentication | `/auth/login` and `/login` | `POST` | Sign in |
| Authentication | `/auth/profile` | `GET`, `PUT` | View or update the signed-in profile |
| Authentication | `/auth/change-password` | `POST` | Change the signed-in user's password |
| Authentication | `/auth/deactivate` | `POST` | Deactivate the signed-in account |
| Crops | `/crops`, `/crops/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Manage crop records |
| Livestock | `/livestock`, `/livestock/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Manage livestock records |
| Livestock | `/livestock/summary` | `GET` | Livestock counts and summaries |
| Health records | `/health/livestock/<livestock_id>/health-records` | `GET`, `POST` | List or create livestock health records |
| Health records | `/health/health-records/<record_id>` | `PUT`, `DELETE` | Update or delete a livestock health record |
| Expenses | `/expenses`, `/expenses/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Track farm expenses |
| Income | `/income`, `/income/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Track farm income |
| Inventory | `/inventory`, `/inventory/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Manage inventory items |
| Tasks | `/tasks`, `/tasks/<id>` | `GET`, `POST`, `PUT`, `DELETE` | Manage farm tasks |
| Dashboard | `/dashboard/summary` | `GET` | Operational summary |
| Dashboard | `/dashboard/crop-yields` | `GET` | Crop-yield data |
| Dashboard | `/dashboard/finance-by-category` | `GET` | Income and expense breakdown |
| Administration | `/admin/users` | `GET` | List users (admin only) |
| Administration | `/admin/users/<user_id>/status` | `PUT` | Set a user's active status (admin only) |
| Administration | `/admin/activity` | `GET` | Platform activity (admin only) |

Use ISO date format (`YYYY-MM-DD`) for date fields such as `planting_date`, `birth_date`, `date_incurred`, and `date_received`.

## Core data model

```text
User
└── Farm
    ├── Crop
    ├── Livestock
    │   └── HealthRecord
    ├── Expense
    ├── Income
    ├── Inventory
    └── Task
```

Each farm belongs to one user. The business records beneath it are associated with that farm, preserving separation between users' data.

## Database migrations

For schema changes, use Flask-Migrate instead of manually changing a production database:

```bash
flask --app app db migrate -m "describe the change"
flask --app app db upgrade
```

Review generated migrations before applying them, especially in production.

## Production deployment

The included `Procfile` starts the API with Gunicorn on port `8080`:

```text
web: gunicorn --bind 0.0.0.0:8080 app:app
```

Before deployment, set `DATABASE_URL`, `SECRET_KEY`, `JWT_SECRET_KEY`, and `FRONTEND_ORIGIN` in the hosting platform's environment settings. Use PostgreSQL and run migrations for production deployments.

## Agile delivery and team contribution

This project was delivered using Scrum practices. As Scrum Master, I facilitated the delivery process by helping the team organize work into sprint-ready tasks, run Scrum ceremonies, remove blockers, and maintain a shared focus on the product goal. I also supported transparent communication, backlog refinement, sprint progress tracking, and retrospectives to strengthen continuous improvement.

To add individual contributors, replace the placeholders below with verified names and responsibilities:

| Role | Contributor |
| --- | --- |
| Scrum Master | _Your name_ |
| Product Owner | _Name_ |
| Development Team | _Names and responsibilities_ |

## Contributing

1. Create a feature branch.
2. Make a focused change and keep secrets out of version control.
3. Test the affected endpoints locally.
4. Open a pull request that explains the change and any migration or configuration impact.

## License

No license has been specified for this repository. Add a license file before distributing or reusing the project outside the team.
