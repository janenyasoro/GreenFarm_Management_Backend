# GreenHarvest API — Backend

A RESTful API for the GreenFarm Management System, built with Flask. It handles authentication, farm data, crops, livestock, health records, expenses, income, inventory, and task management.

## Tech Stack

- Python / Flask
- Flask-SQLAlchemy + Flask-Migrate
- Flask-JWT-Extended (authentication)
- Flask-Bcrypt (password hashing)
- Flask-CORS
- SQLite (development) / PostgreSQL (production)

## Getting Started

### Prerequisites

- Python 3.10+
- pip or pipenv

### Installation

```bash
cd GreenFarm_Management_Backend

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env
```

Edit `.env` and set your `SECRET_KEY`, `JWT_SECRET_KEY`, and `DATABASE_URL`.

### Running the Server

```bash
# Initialize the database
flask db upgrade

# Start the development server
flask run
```

The API will be available at `http://localhost:5000`.

## API Endpoints

| Resource        | Base URL                            |
|-----------------|-------------------------------------|
| Auth            | `/api/auth`                         |
| Crops           | `/api/crops`                        |
| Livestock       | `/api/livestock`                    |
| Health Records  | `/api/livestock/{id}/health-records`|
| Expenses        | `/api/expenses`                     |
| Income          | `/api/income`                       |
| Inventory       | `/api/inventory`                    |
| Tasks           | `/api/tasks`                        |
| Dashboard       | `/api/dashboard`                    |
| Admin           | `/api/admin`                        |
| Health Check    | `/api/health`                       |

## Environment Variables

| Variable          | Description                        |
|-------------------|------------------------------------|
| `FLASK_APP`       | Entry point (`app.py`)             |
| `FLASK_ENV`       | `development` or `production`      |
| `SECRET_KEY`      | Flask secret key                   |
| `JWT_SECRET_KEY`  | JWT signing key                    |
| `DATABASE_URL`    | Database connection string         |
| `FRONTEND_ORIGIN` | Allowed CORS origin                |

## Project Structure

```
GreenFarm_Management_Backend/
├── routes/          # Blueprint route handlers
├── models.py        # SQLAlchemy models
├── app.py           # App factory
├── config.py        # Configuration
├── extensions.py    # Flask extensions
└── requirements.txt
```

## Contributors

| Name             | Role               |
|------------------|--------------------|
| Felix Macharia   | Backend Developer  |
| Hiel Sang        | Backend Developer  |
| Jane Nyasoro     | Backend Developer  |
| Gloria Wanja     | Backend Developer  |
| Ezra Kipyego     | Backend Developer  |
| Ian Kinoti       | Backend Developer  |
