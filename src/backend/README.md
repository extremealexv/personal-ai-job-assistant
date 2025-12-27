# Backend

This directory contains the backend application code for the Personal AI Job Assistant.

## Structure

```
src/backend/
├── app/
│   ├── __init__.py
│   ├── config.py          # Environment configuration
│   ├── main.py            # FastAPI application (TBD)
│   ├── api/               # API endpoints (TBD)
│   ├── models/            # SQLAlchemy models (TBD)
│   └── services/          # Business logic (TBD)
├── database/
│   ├── schema.sql         # PostgreSQL schema
│   └── init_db.py         # Database initialization
└── tests/                 # Test files (TBD)
```

## Getting Started

### 1. Install Dependencies

```bash
cd src/backend

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install
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
# Linux/Mac:
bash scripts/setup_env.sh

# Option 2: Generate keys manually
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
python -c "from cryptography.fernet import Fernet; print('ENCRYPTION_KEY=' + Fernet.generate_key().decode())"

# Edit .env and add your generated keys and API credentials
# Use an editor to open: <project-root>/.env
nano ../../.env  # or notepad, vim, etc.
```

**Location structure:**
```
personal-ai-job-assistant/    ← .env goes HERE
├── .env                       ✓ Correct location
├── .env.example
└── src/
    └── backend/
        ├── app/
        └── ...
```

### 3. Initialize Database

```bash
# Create database and run migrations
python database/init_db.py --drop --seed

# Or without dropping existing data
python database/init_db.py --seed
```

### 4. Run Development Server

```bash
# Start FastAPI server with hot reload
uvicorn app.main:app --reload --port 8000

# API documentation available at:
# http://localhost:8000/docs
```

## Testing Configuration

Verify your environment is properly configured:

```bash
# Test configuration loading
python -c "from app.config import settings; print('✅ Config loaded successfully')"

# Check database connection
python -c "from database.init_db import check_connection; import asyncio; asyncio.run(check_connection())"
```

## Environment Variables

See [.env.example](../../.env.example) for all available configuration options.

**Required variables:**
- `DATABASE_URL` - PostgreSQL connection string
- `DATABASE_ASYNC_URL` - Async PostgreSQL connection string
- `SECRET_KEY` - Application secret key
- `ENCRYPTION_KEY` - Fernet encryption key
- `OPENAI_API_KEY` - OpenAI API key

## Security Notes

**Never commit these files:**
- `.env` - Contains sensitive credentials
- `*.key` - Encryption keys
- Local database backups

Check `.gitignore` to ensure sensitive files are excluded.
