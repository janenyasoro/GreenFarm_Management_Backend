# GreenFarm API Documentation

Base URL: `https://greenfarm-management-backend-kwjs.onrender.com/`. Paths begin with `/api`; admin management paths are under `/api/v1/admin`.

Protected requests use `Authorization: Bearer <token>` and JSON requests use `Content-Type: application/json`. Roles are `ADMIN`, `FARM_OWNER`, and `FARM_WORKER`. Error responses use `{ "message": "Human-readable error" }` (older operational routes may also return an `error` key).

## Authentication

| Method | Path | Purpose | Auth |
| --- | --- | --- | --- |
| POST | `/api/auth/register` | Public owner registration; role cannot be chosen | No |
| POST | `/api/auth/login` | Sign in and receive an access token | No |
| GET | `/api/auth/profile` | Get current user | Bearer |
| PUT | `/api/auth/profile` | Update name/email (role changes are prohibited) | Bearer |
| POST | `/api/auth/change-password` | Change password | Bearer |

Login request: `{ "email": "admin@example.com", "password": "..." }`. Success (`200`) includes `access_token`, `token_type`, and `user`. Invalid credentials or inactive accounts return `401`.

## Admin farms

Every route requires an active `ADMIN` bearer token.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/admin/farms` | Create farm; optional `owner_id` |
| GET | `/api/v1/admin/farms?page=1&limit=20&search=&status=active` | Search/filter paginated farms |
| GET | `/api/v1/admin/farms/:id` | Farm details, owner, workers |
| PATCH / PUT | `/api/v1/admin/farms/:id` | Update farm details/owner |
| DELETE | `/api/v1/admin/farms/:id` | Soft-delete (deactivate) farm |

Farm create/update fields: `name` (required on create), `location`, `size` or `size_acres`, `owner_id` (nullable; if set, must identify an active `FARM_OWNER`). Farm responses include `id`, `name`, `location`, `size`, `size_acres`, `owner_id`, and `is_active`. Lists return `{ "items": [], "farms": [], "page": 1, "limit": 20, "total": 0, "pages": 0 }`.

## Admin users

Every route requires an active `ADMIN` bearer token.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/api/v1/admin/users` | Create an admin, owner, or worker |
| GET | `/api/v1/admin/users?page=1&limit=20&search=&role=FARM_WORKER&farm_id=1` | Search/filter paginated users |
| PATCH | `/api/v1/admin/users/:id/assign-farm` | Assign/reassign; `farm_id: null` unassigns |
| PATCH | `/api/v1/admin/users/:id/status` | Activate/deactivate user |
| DELETE | `/api/v1/admin/users/:id` | Soft-deactivate user |

Create request:

```json
{ "full_name": "Amina Kariuki", "email": "amina@example.com", "password": "temporary-password", "role": "FARM_WORKER", "farm_id": 1 }
```

Assignment request: `{ "farm_id": 1 }` (or `null`). Status request: `{ "is_active": false }`. User list results return `items` and `users` arrays, pagination values, and each user includes `id`, `full_name`, `email`, `role`, `farm_id`, and `is_active`. Passwords are never returned.

## Operational modules

All operational resources require authentication and are farm-scoped. Owners use their owned farm; workers use their assigned farm. An admin can select an active farm by passing `?farm_id=<id>` on requests using the shared farm resolver.

| Module | API area |
| --- | --- |
| Health | `/api/health` |
| Dashboard | `/api/dashboard/*` |
| Crops | `/api/crops` |
| Livestock | `/api/livestock` |
| Health records | `/api/health/livestock/:livestock_id/health-records` |
| Expenses | `/api/expenses` |
| Income | `/api/income` |
| Inventory | `/api/inventory` |
| Tasks | `/api/tasks` |
| Admin activity | `GET /api/v1/admin/activity` |

Operational records use ISO dates (`YYYY-MM-DD`). See the route modules for resource-specific fields.

## Error responses

| Status | Meaning | Example |
| --- | --- | --- |
| 400 | Invalid/missing input | `{ "message": "is_active must be a boolean." }` |
| 401 | Missing/invalid/expired token or invalid credentials | `{ "message": "Authentication is required." }` |
| 403 | Authenticated user lacks admin role | `{ "message": "ADMIN role is required." }` |
| 404 | Resource not found | `{ "message": "Farm not found." }` |
| 409 | Duplicate email | `{ "message": "A user with this email already exists." }` |

JWT library errors may use its standard `msg` shape for missing or invalid tokens.
