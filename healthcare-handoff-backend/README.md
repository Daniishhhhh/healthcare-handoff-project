# Healthcare Handoff Backend

Production-grade backend for managing patient handoffs in healthcare workflows.

## Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create .env File
```bash
cp .env.example .env
```

### 4. Run Tests
```bash
pytest tests/ -v
```

### 5. Start Development Server
```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## Features

- ✅ JWT Authentication
- ✅ Role-Based Access Control
- ✅ Patient Management
- ✅ Handoff Workflows
- ✅ Audit Logging
- ✅ Error Handling
- ✅ Comprehensive Tests

## Tech Stack

- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- PostgreSQL 15
- Pydantic 2.6.0
- Python 3.11-3.13.9

## Project Structure

```
app/
├── auth/          # Authentication
├── models/        # SQLAlchemy ORM models
├── schemas/       # Pydantic request/response models
├── db/            # Database configuration
├── repositories/  # Data access layer
├── services/      # Business logic
├── api/           # Route handlers
├── middleware/    # Request/response middleware
└── background_tasks/  # Background jobs
```

## API Endpoints

### Auth
- `POST /auth/signup` - Create new user
- `POST /auth/login` - Login and get JWT token
- `GET /auth/health` - Health check

### Patients
- `POST /patients` - Create patient (doctor/admin only)
- `GET /patients/{patient_id}` - Get patient

## Development

### Code Quality
```bash
black app tests
isort app tests
flake8 app tests
```

### Run Tests
```bash
pytest tests/ -v --cov=app
```

## Next Steps

- Day 1: Foundation ✅
- Day 2: Handoff Workflow
- Day 3: Escalation & Audit

---

**Author:** Healthcare Engineering Team
