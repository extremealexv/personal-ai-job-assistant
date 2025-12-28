# Backend

**Personal AI Job Assistant - FastAPI Backend**

This directory contains the backend API for the Personal AI Job Assistant, built with FastAPI, SQLAlchemy 2.0, and PostgreSQL.

## 📚 Documentation

- **[API Endpoints](docs/API_ENDPOINTS.md)** - Complete API reference with examples
- **[Development Guide](docs/DEVELOPMENT.md)** - Developer workflow and best practices
- **[Testing Guide](README_TESTING.md)** - Testing infrastructure and examples
- **[Interactive API Docs](http://localhost:8000/docs)** - Swagger UI (when server is running)
- **[Alternative API Docs](http://localhost:8000/redoc)** - ReDoc (when server is running)

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Poetry (dependency management)

### Installation

```bash
cd src/backend

# Install dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 2. Configure Environment

**Important:** The `.env` file must be in the **project root** (not in `src/backend`).

```bash
# Navigate to project root
cd ../..

# Copy environment template
cp .env.example .env

# Option 1: Run automated setup (recommended)
cd src/backend
# Windows:
powershell scripts/setup_env.ps1
```

### Environment Configuration

**Important:** The `.env` file must be in the **project root** (not in `src/backend`).

```bash
# Navigate to project root
cd ../..

# Copy environment template
cp .env.example .env

# Edit .env with your configuration
nano .env  # or use your preferred editor
```

**Required environment variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Application secret key (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- `OPENAI_API_KEY` - OpenAI API key (for AI features)

See [.env.example](../../.env.example) for all available options.

### Database Setup

```bash
cd src/backend

# Create database and run migrations
python database/init_db.py --drop --seed

# Or without dropping existing data
python database/init_db.py --seed

# Run migrations (after model changes)
alembic upgrade head
```

### Start Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

Visit:
- **API:** http://localhost:8000
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest -m unit              # Fast unit tests
pytest -m integration       # API integration tests

# Run tests in watch mode
pytest-watch
```

See [README_TESTING.md](README_TESTING.md) for detailed testing guide.

## 📁 Project Structure

```
src/backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── api.py              # API router aggregator
│   │       └── endpoints/
│   │           └── health.py       # Health check endpoints
│   ├── core/
│   │   ├── error_handlers.py       # Exception handlers
│   │   ├── exceptions.py           # Custom exceptions
│   │   ├── logging.py              # Logging configuration
│   │   └── middleware.py           # Request middleware
│   ├── models/
│   │   ├── base.py                 # Base model class
│   │   ├── user.py                 # User model
│   │   ├── resume.py               # Resume models
│   │   └── ...                     # Other models (15 total)
│   ├── schemas/
│   │   ├── user.py                 # User Pydantic schemas
│   │   ├── resume.py               # Resume schemas
│   │   └── ...                     # Other schemas
│   ├── config.py                   # Application configuration
│   ├── db.py                       # Database connection
│   └── main.py                     # FastAPI application
├── alembic/                        # Database migrations
├── database/
│   ├── schema.sql                  # PostgreSQL schema
│   └── init_db.py                  # Database initialization
├── docs/
│   ├── API_ENDPOINTS.md            # API documentation
│   └── DEVELOPMENT.md              # Development guide
├── scripts/
│   ├── setup_test_db.py            # Test database setup
│   └── ...                         # Helper scripts
├── tests/
│   ├── conftest.py                 # Pytest fixtures
│   ├── test_health.py              # Health endpoint tests
│   ├── test_exceptions.py          # Exception tests
│   └── test_models.py              # Model tests
├── alembic.ini                     # Alembic configuration
├── pytest.ini                      # Pytest configuration
├── pyproject.toml                  # Poetry dependencies
└── README.md                       # This file
```

## 🛠 Development

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check . --fix

# Type check
mypy app/

# Run all checks (pre-commit)
pre-commit run --all-files
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

### Adding New Endpoints

1. Create endpoint in `app/api/v1/endpoints/`
2. Add Pydantic schemas in `app/schemas/`
3. Register router in `app/api/v1/api.py`
4. Write tests in `tests/`
5. Update API documentation

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for detailed workflow.

## 🔒 Security

- **Authentication:** JWT tokens (implementation pending)
- **Password Hashing:** bcrypt/argon2
- **Data Encryption:** AES-256 for sensitive fields
- **CORS:** Configurable origins
- **Security Headers:** Automatic via middleware

**Never commit:**
- `.env` files
- `*.key` files
- Database backups with real data

## 📊 Current Status

**Completed:**
- ✅ FastAPI application setup
- ✅ 15 SQLAlchemy models
- ✅ Database schema and migrations
- ✅ Pydantic schemas for all models
- ✅ Error handling and middleware
- ✅ Health check endpoints
- ✅ Testing infrastructure (16 tests passing)
- ✅ Comprehensive documentation

**In Progress:**
- 🚧 Authentication endpoints
- 🚧 Resume management endpoints
- 🚧 Job posting endpoints
- 🚧 AI integration services

## 🤝 Contributing

See [CONTRIBUTING.md](../../CONTRIBUTING.md) for contribution guidelines.

## 📝 License

See [LICENSE](../../LICENSE) for details.
