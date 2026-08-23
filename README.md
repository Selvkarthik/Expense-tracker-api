# Expense Tracker API

A production-style REST API for managing personal expenses, categories, monthly budgets, and spending summaries.

Built with **FastAPI, PostgreSQL, SQLAlchemy, JWT authentication, and Alembic**.

---

## 🚀 Features

- JWT-based authentication
- OAuth2 password authentication
- Secure password hashing with bcrypt
- User management
- Category management
- Expense management
- Monthly budget management
- Expense summaries
- Automatic budget-overrun warnings
- Expense filtering by category and date
- Pagination
- Sorting by amount, date, title, and creation time
- Monthly and yearly expense summaries
- User-level data isolation
- PostgreSQL database
- Alembic database migrations
- Automated testing with Pytest
- **59 automated tests**
- **98% code coverage**

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Programming language |
| FastAPI | REST API framework |
| PostgreSQL | Relational database |
| SQLAlchemy | ORM |
| Alembic | Database migrations |
| Pydantic | Data validation |
| JWT / OAuth2 | Authentication |
| bcrypt | Password hashing |
| Pytest | Automated testing |
| pytest-cov | Test coverage |
| Uvicorn | ASGI server |

---

## 📁 Project Structure

```text
expense-tracker-api/
│
├── alembic/
│   ├── versions/
│   └── env.py
│
├── app/
│   ├── routes/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── categories.py
│   │   ├── expenses.py
│   │   └── budgets.py
│   │
│   ├── auth.py
│   ├── database.py
│   ├── dependencies.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   └── main.py
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_categories.py
│   ├── test_expenses.py
│   ├── test_budgets.py
│   └── test_setup.py
│
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the repository

```bash
git clone https://github.com/Selvkarthik/Expense-tracker-api.git
cd Expense-tracker-api
```

## 2. Create a virtual environment

### Windows

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
```

### Linux / macOS

```bash
python -m venv env
source env/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# 🔐 Environment Variables

Create a `.env` file based on `.env.example`.

```env
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
DB_NAME=

JWT_SECRET_KEY=
JWT_ALGORITHM=
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=

TEST_DB_NAME=
```

Do **not** commit your actual `.env` file to GitHub.

---

# 🗄️ Database Setup

This project uses **PostgreSQL** with **SQLAlchemy**.

Make sure PostgreSQL is installed and running before starting the application.

The database schema is managed using **Alembic migrations**.

Apply the latest migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

Check migration history:

```bash
alembic history
```

---

# ▶️ Running the API

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Interactive API Documentation

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

ReDoc:

```text
http://127.0.0.1:8000/redoc
```

---

# 📚 API Overview

## 🔐 Authentication

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Register a new user |
| POST | `/auth/login` | Login and receive JWT |
| GET | `/auth/me` | Get current authenticated user |

Authentication uses the **OAuth2 password flow with JWT access tokens**.

Protected endpoints require:

```text
Authorization: Bearer <access_token>
```

---

## 👤 Users

| Method | Endpoint | Description |
|---|---|---|
| GET | `/users/` | Get users |
| GET | `/users/{user_id}` | Get user by ID |
| PUT | `/users/{user_id}` | Update user |
| DELETE | `/users/{user_id}` | Delete user |

User-specific resources are protected using authenticated ownership checks.

---

## 🏷️ Categories

| Method | Endpoint | Description |
|---|---|---|
| GET | `/categories/` | Get all categories |
| POST | `/categories/` | Create category |
| GET | `/categories/{category_id}` | Get category by ID |
| PUT | `/categories/{category_id}` | Update category |
| DELETE | `/categories/{category_id}` | Delete category |

Categories currently being used by expenses cannot be deleted.

---

## 💸 Expenses

| Method | Endpoint | Description |
|---|---|---|
| GET | `/expenses/` | Get expenses |
| POST | `/expenses/` | Create expense |
| GET | `/expenses/{expense_id}` | Get expense by ID |
| PUT | `/expenses/{expense_id}` | Update expense |
| DELETE | `/expenses/{expense_id}` | Delete expense |
| GET | `/expenses/summary` | Get expense summary |

### Expense Query Features

The expense listing endpoint supports:

- Pagination
- Category filtering
- Date-range filtering
- Sorting
- Multiple sort fields

### Pagination

```text
GET /expenses/?skip=0&limit=10
```

### Filter by category

```text
GET /expenses/?category_id=1
```

### Filter by date

```text
GET /expenses/?start_date=2026-08-01&end_date=2026-08-31
```

### Sort by amount

```text
GET /expenses/?sort_by=amount&sort_order=asc
```

### Sort descending

```text
GET /expenses/?sort_by=amount&sort_order=desc
```

---

# 📊 Expense Summary

The expense summary endpoint provides:

- Total expenses
- Expense count
- Average expense
- Monthly summaries
- Yearly summaries

### Overall summary

```text
GET /expenses/summary
```

### Monthly summary

```text
GET /expenses/summary?month=8
```

### Yearly summary

```text
GET /expenses/summary?year=2026
```

### Specific month and year

```text
GET /expenses/summary?month=8&year=2026
```

When a month is provided without a year, the current year is automatically used.

---

# 💰 Budgets

| Method | Endpoint | Description |
|---|---|---|
| GET | `/budgets/` | Get budgets |
| POST | `/budgets/` | Create budget |
| GET | `/budgets/{budget_id}` | Get budget by ID |
| PUT | `/budgets/{budget_id}` | Update budget |
| DELETE | `/budgets/{budget_id}` | Delete budget |
| GET | `/budgets/{budget_id}/summary` | Get budget summary |

Each user can have a budget for a specific month and year.

Duplicate budgets for the same user, month, and year are prevented.

---

# ⚠️ Budget Warnings

When creating an expense, the API automatically checks whether the user has a budget for that expense's month.

For example:

```text
Budget Limit:       ₹25,000
Previous Spending:  ₹20,000
New Expense:        ₹10,000
--------------------------------
Total Spending:     ₹30,000
Exceeded By:         ₹5,000
```

The expense is still created, but the API returns a budget warning.

Example response:

```json
{
    "expense": {
        "id": 1,
        "title": "Laptop",
        "amount": "10000.00"
    },
    "budget_warning": {
        "exceeded": true,
        "exceeded_by": "5000.00"
    }
}
```

---

# 🔒 Security

The API implements:

- JWT authentication
- OAuth2 password flow
- bcrypt password hashing
- Authenticated route protection
- User ownership checks
- Cross-user data isolation
- Protected expense operations
- Protected budget operations
- Environment-based secrets

Users cannot access, modify, or delete another user's expenses or budgets.

---

# 🧪 Testing

The project uses **Pytest** for automated testing.

Run the complete test suite:

```bash
pytest
```

Current test results:

```text
59 passed
```

Run tests with coverage:

```bash
pytest --cov=app --cov-report=term-missing
```

Current coverage:

```text
98%
```

### Test Coverage Includes

- Authentication
- User CRUD
- User authentication
- Category CRUD
- Category validation
- Expense CRUD
- Expense ownership
- Expense filtering
- Pagination
- Sorting
- Date validation
- Expense summaries
- Monthly summaries
- Yearly summaries
- Budget CRUD
- Budget ownership
- Budget validation
- Budget summaries
- Budget exceeded calculations
- Automatic budget warnings

---

# 🔄 Database Migrations

The project uses **Alembic** for database schema management.

### Create a migration

After modifying SQLAlchemy models:

```bash
alembic revision --autogenerate -m "description"
```

### Apply migrations

```bash
alembic upgrade head
```

### Check current migration

```bash
alembic current
```

### View migration history

```bash
alembic history
```

### Rollback one migration

```bash
alembic downgrade -1
```

---

# 🚧 Future Improvements

Possible future improvements include:

- Docker and Docker Compose support
- GitHub Actions CI/CD
- Refresh token implementation
- Expense analytics and charts
- Recurring expenses
- Export expenses to CSV
- API rate limiting
- Production deployment configuration
- Cloud database deployment

---

# 👨‍💻 Author

**Selvkarthik S**

GitHub:  
https://github.com/Selvkarthik

---

# 📌 Project Highlights

```text
FastAPI + PostgreSQL
SQLAlchemy + Alembic
JWT + OAuth2
bcrypt password hashing
User-level authorization
Expense & Budget business logic
59 automated tests
98% code coverage
```

Built as a backend-focused project to practice designing, implementing, securing, and testing a production-style REST API.