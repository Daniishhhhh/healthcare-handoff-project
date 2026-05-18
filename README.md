# Healthcare Handoff Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org)
[![Node 18+](https://img.shields.io/badge/Node-18%2B-green)](https://nodejs.org)
[![React 19+](https://img.shields.io/badge/React-19%2B-blue)](https://react.dev)

A production-grade, full-stack healthcare management system designed to streamline patient handoffs between medical professionals. This comprehensive platform enables secure, HIPAA-compliant workflows for managing patient transitions of care with built-in audit logging, escalation handling, and real-time status tracking.

## 🎯 Overview

Healthcare Handoff Management System is a modern web application built to improve communication and documentation during patient care transitions. It provides doctors, nurses, and healthcare administrators with tools to efficiently document, track, and manage patient handoffs while maintaining comprehensive audit trails for compliance and accountability.

**Key Use Case:** When a patient is transferred from one care team to another, this system ensures all critical information, pending tests, medication changes, and follow-up requirements are clearly communicated and tracked.

## ✨ Key Features

### 🔐 Security & Authentication
- **JWT-based Authentication** - Secure token-based user authentication
- **Role-Based Access Control (RBAC)** - Three user roles: Doctor, Nurse, and Admin with granular permissions
- **Password Hashing** - Industry-standard bcrypt password encryption
- **Session Management** - Automatic token expiry with configurable duration

### 📋 Core Functionality
- **Patient Management** - Create, view, and manage patient profiles (Doctor/Admin only)
- **Handoff Workflows** - Create and track patient handoffs with comprehensive clinical details
- **Readiness Assessment** - Mark handoffs as ready and track completion status
- **Escalation System** - Flag and escalate critical handoffs that require immediate attention
- **Item Management** - Track pending tests, medication changes, and follow-up items
- **Audit Logging** - Complete audit trail of all actions with timestamps and user attribution

### 📊 User Interface
- **Responsive Dashboard** - Overview of patient statistics and recent handoffs
- **Patient Directory** - Browse and manage all patients in the system
- **Handoff Tracking** - View, create, and manage handoffs with status filters
- **Detail Views** - Comprehensive detail pages for patient and handoff information
- **Real-time Notifications** - Toast notifications for user feedback

### 🔄 Workflow Support
- **Handoff Status Tracking** - Progress through workflow states (created → ready → escalated)
- **Priority Levels** - Support for high/medium/low priority handoffs
- **Deadline Management** - Track follow-up deadlines for critical care items
- **Comprehensive Logging** - Audit trail for compliance and quality assurance

## 📱 Technology Stack

### Backend
- **Framework:** FastAPI 0.109.0 - Modern, high-performance Python web framework
- **Language:** Python 3.11+ (tested with 3.13.9)
- **Database:** PostgreSQL 15 - Robust relational database
- **ORM:** SQLAlchemy 2.0.25 - Powerful Python SQL toolkit
- **Validation:** Pydantic 2.6.0 - Data validation using Python type annotations
- **Authentication:** Python-Jose 3.3.0 + PyJWT - JWT token handling
- **Security:** bcrypt 4.1.1 + cryptography 41.0.7 - Password hashing and encryption
- **Background Jobs:** APScheduler 3.10.4 - Scheduled task execution
- **Caching:** Redis 5.0.1 (optional, phase 2) - In-memory data store
- **Testing:** Pytest 7.4.4 + pytest-asyncio - Comprehensive test framework
- **Code Quality:** Black, isort, flake8 - Code formatting and linting

### Frontend
- **Framework:** React 19.2.4 - Modern UI library
- **Language:** TypeScript 5.9.3 - Type-safe JavaScript
- **Build Tool:** Vite 8.0.1 - Lightning-fast development server
- **Routing:** React Router DOM 7.13.1 - Client-side routing
- **Styling:** Tailwind CSS 4.2.2 - Utility-first CSS framework
- **Icons:** Lucide React 0.577.0 - Beautiful icon library
- **HTTP Client:** Axios 1.13.6 - Promise-based HTTP client
- **PostCSS:** 8.5.8 - CSS transformations
- **Linting:** ESLint 9.39.4 + TypeScript ESLint - Code quality

### Deployment & DevOps
- **Version Control:** Git
- **Database Migrations:** Alembic 1.13.1 - SQLAlchemy migration tool
- **Environment Management:** Python-dotenv 1.0.0

## 📁 Project Structure

```
healthcare-handoff-project/
├── README.md                          # This file
├── healthcare-handoff-backend/        # Python FastAPI backend
│   ├── app/                           # Main application package
│   │   ├── main.py                    # FastAPI application factory
│   │   ├── config.py                  # Configuration settings (environment-based)
│   │   ├── utils.py                   # Utility functions
│   │   ├── exceptions.py              # Custom exception definitions
│   │   ├── dependencies.py            # Dependency injection utilities
│   │   │
│   │   ├── auth/                      # Authentication module
│   │   │   ├── routes.py              # Auth endpoints (login, signup)
│   │   │   └── schemas.py             # Request/response schemas
│   │   │
│   │   ├── api/v1/                    # API v1 endpoints
│   │   │   ├── patients.py            # Patient CRUD operations
│   │   │   ├── handoffs.py            # Handoff management endpoints
│   │   │   └── items.py               # Handoff items endpoints
│   │   │
│   │   ├── models/                    # SQLAlchemy ORM models
│   │   │   ├── user.py                # User model with roles
│   │   │   ├── patient.py             # Patient profile model
│   │   │   ├── handoff.py             # Handoff workflow model
│   │   │   ├── handoff_item.py        # Items within handoffs
│   │   │   ├── audit_log.py           # Audit trail model
│   │   │   └── escalation_event.py    # Escalation tracking
│   │   │
│   │   ├── schemas/                   # Pydantic validation schemas
│   │   │   ├── user.py
│   │   │   ├── patient.py
│   │   │   ├── handoff.py
│   │   │   └── auth.py
│   │   │
│   │   ├── services/                  # Business logic layer
│   │   │   ├── handoff_service.py     # Handoff creation & management
│   │   │   ├── readiness_service.py   # Readiness checking logic
│   │   │   ├── escalation_service.py  # Escalation handling
│   │   │   └── audit_service.py       # Audit logging
│   │   │
│   │   ├── repositories/              # Data access layer (optional)
│   │   │
│   │   ├── db/                        # Database configuration
│   │   │   ├── database.py            # SQLAlchemy setup
│   │   │   └── base.py                # Base model configuration
│   │   │
│   │   └── middleware/                # Request/response middleware (future)
│   │
│   ├── migrations/                    # Alembic database migrations
│   │   ├── versions/                  # Migration files
│   │   └── alembic.ini               # Alembic configuration
│   │
│   ├── tests/                         # Test suite
│   │   ├── conftest.py               # Pytest configuration
│   │   ├── test_auth.py              # Authentication tests
│   │   └── ...
│   │
│   ├── requirements.txt               # Python dependencies
│   ├── .env.example                   # Example environment variables
│   └── README.md                      # Backend-specific documentation
│
├── healthcare-handoff-frontend/       # React + TypeScript frontend
│   ├── src/
│   │   ├── App.tsx                   # Main application component with routing
│   │   ├── main.tsx                  # React DOM mount point
│   │   │
│   │   ├── pages/                    # Page components (one per route)
│   │   │   ├── LoginPage.tsx
│   │   │   ├── SignupPage.tsx
│   │   │   ├── DashboardPage.tsx
│   │   │   ├── PatientsPage.tsx
│   │   │   ├── HandoffsPage.tsx
│   │   │   ├── HandoffDetailPage.tsx
│   │   │   └── NotFoundPage.tsx
│   │   │
│   │   ├── components/               # Reusable components
│   │   │   ├── auth/                 # Auth-related components
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── SignupForm.tsx
│   │   │   │
│   │   │   ├── common/               # Shared UI components
│   │   │   │   ├── Navbar.tsx
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Modal.tsx
│   │   │   │   └── Toast.tsx
│   │   │   │
│   │   │   ├── patients/             # Patient-related components
│   │   │   │   ├── PatientForm.tsx
│   │   │   │   └── PatientCard.tsx
│   │   │   │
│   │   │   └── handoffs/             # Handoff-related components
│   │   │       ├── HandoffForm.tsx
│   │   │       ├── HandoffCard.tsx
│   │   │       ├── ReadinessModal.tsx
│   │   │       └── ItemList.tsx
│   │   │
│   │   ├── context/                  # React Context providers
│   │   │   ├── AuthContext.tsx       # Authentication state
│   │   │   └── ToastContext.tsx      # Toast notifications
│   │   │
│   │   ├── hooks/                    # Custom React hooks
│   │   │   ├── useAuth.ts
│   │   │   └── useToast.ts
│   │   │
│   │   ├── api/                      # API client integration
│   │   │   ├── client.ts            # Axios HTTP client
│   │   │   └── endpoints.ts         # API endpoints
│   │   │
│   │   ├── types/                    # TypeScript type definitions
│   │   │   └── index.ts             # Shared types
│   │   │
│   │   ├── assets/                   # Static assets
│   │   │   ├── hero.png
│   │   │   ├── react.svg
│   │   │   └── vite.svg
│   │   │
│   │   └── index.css                # Global styles
│   │
│   ├── public/                        # Static files
│   ├── package.json                   # npm dependencies
│   ├── package-lock.json
│   ├── vite.config.ts                 # Vite configuration
│   ├── tsconfig.json                  # TypeScript configuration
│   ├── tailwind.config.js            # Tailwind CSS configuration
│   ├── postcss.config.js             # PostCSS configuration
│   ├── eslint.config.js              # ESLint configuration
│   ├── .env.example                   # Example environment variables
│   └── README.md                      # Frontend-specific documentation
│
└── app/                               # Utility scripts/shared code
    ├── main.py
    └── services/
```

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

**Backend Requirements:**
- Python 3.11 or higher (tested with 3.13.9)
- PostgreSQL 15 or higher
- pip (Python package manager)
- virtualenv or venv

**Frontend Requirements:**
- Node.js 18 or higher
- npm (included with Node.js)

**Optional:**
- Redis 7+ (for caching, phase 2)
- Docker & Docker Compose (for containerized setup)

### Backend Setup

#### 1. Clone the Repository
```bash
git clone https://github.com/Daniishhhhh/healthcare-handoff-project.git
cd healthcare-handoff-project/healthcare-handoff-backend
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Key environment variables to configure:**
```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/handoff_db

# Security (Change in production!)
SECRET_KEY=your_super_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_EXPIRY_HOURS=1

# Application
DEBUG=True
LOG_LEVEL=INFO
APP_NAME=Healthcare Handoff Backend
APP_VERSION=0.1.0

# Features
ENABLE_BACKGROUND_JOBS=True
NOTIFICATION_SERVICE_ENABLED=False
```

#### 5. Setup Database
```bash
# Create database (if using PostgreSQL)
createdb handoff_db

# Run migrations (when available)
alembic upgrade head
```

#### 6. Run Development Server
```bash
# Development server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API Base URL:** `http://localhost:8000`
- **Interactive API Docs (Swagger UI):** `http://localhost:8000/docs`
- **Alternative API Docs (ReDoc):** `http://localhost:8000/redoc`

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
cd healthcare-handoff-project/healthcare-handoff-frontend
```

#### 2. Install Dependencies
```bash
npm install
```

#### 3. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

**Key environment variables:**
```env
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

#### 4. Run Development Server
```bash
# Start development server with HMR
npm run dev
```

The frontend will be available at:
- **Application URL:** `http://localhost:5173` (or the URL shown in terminal)
- **Hot Module Replacement (HMR):** Enabled for instant updates during development

### Running Both Services

For optimal development experience, run both services in separate terminal windows:

**Terminal 1 - Backend:**
```bash
cd healthcare-handoff-project/healthcare-handoff-backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd healthcare-handoff-project/healthcare-handoff-frontend
npm run dev
```

Then access the application at `http://localhost:5173`

## 🔗 API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication

All protected endpoints require a JWT token in the `Authorization` header:
```
Authorization: Bearer <your_jwt_token>
```

### User Roles
- **Doctor** - Create patients, manage handoffs
- **Nurse** - View and manage assigned handoffs
- **Admin** - Full system access and management

### API Endpoints

#### Authentication Endpoints
```
POST   /auth/signup              # Create new user account
POST   /auth/login               # Login and receive JWT token
GET    /auth/health              # Health check endpoint
```

#### Patient Endpoints
```
POST   /patients                 # Create patient (doctor/admin only)
GET    /patients/{patient_id}    # Get patient details
GET    /patients                 # List all patients
```

#### Handoff Endpoints
```
POST   /handoffs                 # Create new handoff (doctor/admin only)
GET    /handoffs                 # List handoffs
GET    /handoffs/{handoff_id}    # Get handoff details
PUT    /handoffs/{handoff_id}/ready       # Mark handoff as ready
POST   /handoffs/{handoff_id}/escalate    # Escalate handoff
```

#### Item Endpoints
```
POST   /handoffs/{handoff_id}/items       # Add item to handoff
GET    /handoffs/{handoff_id}/items       # List handoff items
```

### Example Requests

**Signup:**
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePassword123!",
    "full_name": "Dr. John Smith",
    "role": "doctor"
  }'
```

**Login:**
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@hospital.com",
    "password": "SecurePassword123!"
  }'
```

**Create Patient:**
```bash
curl -X POST http://localhost:8000/patients \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "date_of_birth": "1990-01-01",
    "medical_record_number": "MRN123456"
  }'
```

For complete API documentation with interactive examples, visit the Swagger UI at:
```
http://localhost:8000/docs
```

## 🧪 Testing

### Running Tests

#### Backend Tests
```bash
cd healthcare-handoff-project/healthcare-handoff-backend

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app

# Run specific test file
pytest tests/test_auth.py -v

# Run tests matching pattern
pytest -k "test_login" -v
```

#### Frontend Tests
Frontend testing setup to be added in future iterations.

### Code Quality

#### Backend Code Quality
```bash
cd healthcare-handoff-project/healthcare-handoff-backend

# Format code with Black
black app tests

# Sort imports with isort
isort app tests

# Lint with flake8
flake8 app tests

# Run all quality checks
black app tests && isort app tests && flake8 app tests
```

#### Frontend Code Quality
```bash
cd healthcare-handoff-project/healthcare-handoff-frontend

# Type checking
npm run lint

# Build check
npm run build
```

## 📦 Building for Production

### Backend Production Build

1. **Set environment variables:**
```bash
DEBUG=False
LOG_LEVEL=WARNING
SECRET_KEY=<long-random-key>
JWT_EXPIRY_HOURS=24
```

2. **Use production ASGI server:**
```bash
# Gunicorn with Uvicorn workers
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Production Build

```bash
cd healthcare-handoff-project/healthcare-handoff-frontend

# Create optimized production build
npm run build

# Outputs to: dist/
# Serve with: npm run preview
```

The production build:
- Minifies JavaScript and CSS
- Optimizes images
- Creates source maps
- Bundles for optimal delivery

## 🐳 Docker Deployment (Optional)

Docker configuration for containerized deployment to be implemented in future iterations.

## 🔐 Security Considerations

- **JWT Tokens:** Expire after configured duration (default: 1 hour)
- **Password Hashing:** bcrypt with automatic salt
- **CORS:** Restricted to frontend origins (configurable)
- **Input Validation:** Pydantic schemas validate all inputs
- **SQL Injection:** SQLAlchemy ORM prevents SQL injection
- **Audit Logging:** All actions logged with user attribution
- **Role-Based Access:** Granular permission checks on endpoints

**Production Recommendations:**
- Use HTTPS/TLS for all communications
- Set `DEBUG=False` in production
- Use strong `SECRET_KEY` (32+ characters)
- Store secrets in secure vault (not in .env)
- Enable database backups
- Implement rate limiting
- Add API key management for external integrations
- Regular security audits and dependency updates

## 🛠️ Development Guidelines

### Code Style

**Python Backend:**
- Follow PEP 8 style guide
- Use Black for automatic formatting
- Use isort for import sorting
- Use type hints throughout
- Target Python 3.11+

**TypeScript Frontend:**
- Use strict mode (`"strict": true`)
- Use ESLint rules from config
- Follow React best practices
- Use functional components with hooks
- Maintain consistent naming conventions

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git add .
git commit -m "Brief description of changes"

# Push to origin
git push origin feature/your-feature-name

# Create Pull Request on GitHub
```

### Commit Message Convention

```
type(scope): brief description

Optional longer explanation of the changes and why they were made.
```

**Types:** feat, fix, docs, style, refactor, test, chore

## 📋 Database Schema Overview

### Core Tables

**users**
- Stores user accounts with encrypted passwords
- Supports multiple roles: doctor, nurse, admin
- Tracks creation and last login timestamps

**patients**
- Patient demographic information
- Medical record number for hospital integration
- Created by doctor/admin users

**handoffs**
- Main handoff workflow records
- Links creator (sending doctor) with assignee (receiving doctor/nurse)
- Tracks status: created, ready, escalated
- Stores clinical details: diagnosis, tests, medications

**handoff_items**
- Individual items within a handoff
- Types: pending_tests, medication_changes, follow_up_items
- Each item has status and completion tracking

**audit_logs**
- Complete audit trail of all system actions
- Records: action, user, timestamp, affected resources
- For compliance and accountability

**escalation_events**
- Records escalation events on handoffs
- Tracks reason and escalation timestamp
- Used for reporting and analysis

## 🔄 Workflow Example

1. **Handoff Creation**
   - Doctor creates new handoff for a patient
   - Provides diagnosis summary, pending tests, medication changes
   - Assigns to another doctor/nurse

2. **Readiness Assessment**
   - Receiving provider reviews handoff details
   - Marks handoff as "ready" when all information is received
   - System tracks readiness timestamp

3. **Escalation (if needed)**
   - If critical issues arise, handoff can be escalated
   - Escalation triggers notifications and creates audit log entry
   - Tracks escalation reason and timestamp

4. **Completion**
   - Handoff remains in system for audit and reference
   - Complete history available for quality assurance

## 📊 Key Metrics Tracked

- Total patients in system
- Total handoffs created
- Ready handoffs (completed readiness assessment)
- Escalated handoffs (requiring immediate attention)
- Average handoff processing time
- User activity audit trail

## 🚨 Troubleshooting

### Backend Issues

**Port 8000 already in use:**
```bash
# Linux/macOS - Find and kill process
lsof -i :8000
kill -9 <PID>

# Or use different port
uvicorn app.main:app --reload --port 8001
```

**Database connection error:**
- Verify PostgreSQL is running
- Check DATABASE_URL in .env
- Ensure database exists: `createdb handoff_db`
- Verify credentials and permissions

**ModuleNotFoundError:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port 5173 already in use:**
```bash
# Vite will auto-increment port (5174, 5175, etc.)
# Or specify port manually
npm run dev -- --port 3000
```

**Dependencies not installing:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

**API requests failing:**
- Verify backend is running on port 8000
- Check VITE_API_BASE_URL in .env
- Check browser console for CORS errors
- Verify authentication token is valid

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 📅 Project Timeline

- **Phase 1 (Complete):** Foundation - Authentication, user management, patient CRUD
- **Phase 2 (In Progress):** Handoff workflows - Create, track, and manage handoffs
- **Phase 3 (Planned):** Escalation & Audit - Advanced escalation handling, comprehensive auditing
- **Phase 4 (Future):** Notifications - Email/SMS alerts, real-time updates
- **Phase 5 (Future):** Mobile App - Native mobile support
- **Phase 6 (Future):** Analytics - Dashboards and reporting

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes following our commit convention
4. Push to your fork (`git push origin feature/AmazingFeature`)
5. Open a Pull Request with detailed description

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Project Team

**Healthcare Engineering Team**
- Built with ❤️ for better healthcare workflows

## 📞 Support & Contact

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact the development team

## 🙏 Acknowledgments

- FastAPI community for excellent framework
- React and TypeScript communities for tooling
- Healthcare professionals for domain expertise and requirements

---

**Last Updated:** May 2026  
**Version:** 1.0.0-beta  
**Status:** Active Development
