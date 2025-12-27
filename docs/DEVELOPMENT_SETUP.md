# Development Environment Setup

**Project:** Personal AI Job Assistant  
**Date:** December 26, 2025

This guide walks you through setting up the complete development environment for this project.

---

## Prerequisites

### Required Software

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Verify: `node --version`

3. **PostgreSQL 15+**
   - Download: https://www.postgresql.org/download/
   - Verify: `psql --version`

4. **Git**
   - Download: https://git-scm.com/downloads
   - Verify: `git --version`

---

## Step 1: Install Package Managers

### Poetry (Python Dependency Management)

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Linux/macOS:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Add to PATH:**
- Windows: Add `%APPDATA%\Python\Scripts` to PATH
- Linux/macOS: Add `~/.local/bin` to PATH

**Verify:**
```bash
poetry --version
```

### pnpm (Node.js Package Management)

**Via npm:**
```bash
npm install -g pnpm
```

**Verify:**
```bash
pnpm --version
```

---

## Step 2: Clone and Setup Repository

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/personal-ai-job-assistant.git
cd personal-ai-job-assistant

# Create .env file from template
cp .env.example .env

# Edit .env with your settings
# On Windows: notepad .env
# On Linux/macOS: nano .env
```

### Required .env Configuration

At minimum, set these values:
```env
# Database
DATABASE_ASYNC_URL=postgresql+asyncpg://ai_job_user:your_password@localhost:5432/ai_job_assistant

# Security (generate with setup scripts)
SECRET_KEY=your_generated_secret_key
ENCRYPTION_KEY=your_generated_encryption_key

# Environment
ENVIRONMENT=development
DEBUG=true
```

**Quick Setup (generates keys automatically):**

**Windows:**
```powershell
.\src\backend\scripts\setup_env.ps1
```

**Linux/macOS:**
```bash
chmod +x src/backend/scripts/setup_env.sh
./src/backend/scripts/setup_env.sh
```

---

## Step 3: Backend Setup

```bash
cd src/backend

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Verify configuration
python scripts/test_config.py

# Initialize database
python database/init_db.py --drop --seed

# Run tests
pytest

# Start server
uvicorn app.main:app --reload --port 8000
```

### Common Backend Issues

**Issue: `poetry: command not found`**
- Solution: Add Poetry to PATH (see Step 1)

**Issue: Database connection failed**
- Solution: Check PostgreSQL is running and .env DATABASE_ASYNC_URL is correct
- Verify: `psql -U ai_job_user -d ai_job_assistant -W`

**Issue: Import errors**
- Solution: Ensure you're in Poetry shell: `poetry shell`

---

## Step 4: Frontend Setup

```bash
cd src/frontend

# Install dependencies
pnpm install

# Start development server
pnpm dev

# Build for production
pnpm build

# Run tests
pnpm test
```

### Common Frontend Issues

**Issue: `pnpm: command not found`**
- Solution: Install pnpm globally: `npm install -g pnpm`

**Issue: Port 5173 already in use**
- Solution: Stop other Vite instances or change port in `vite.config.ts`

---

## Step 5: Browser Extension Setup

```bash
cd src/extension

# Install dependencies
npm install

# Build extension
npm run build

# Watch mode for development
npm run dev
```

### Load Extension in Browser

**Chrome/Edge:**
1. Open `chrome://extensions` (or `edge://extensions`)
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select `src/extension/dist` folder

**Reload after changes:**
- Click reload icon in extensions page, or
- Use `Ctrl+R` in extension popup

---

## Step 6: Development Tools Setup

### Install Pre-commit Hooks

```bash
# In project root
pip install pre-commit

# Or via Poetry (in backend)
cd src/backend
poetry add --group dev pre-commit

# Install hooks
pre-commit install
```

### Verify Pre-commit Setup

```bash
# Run on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black --all-files
pre-commit run ruff --all-files
pre-commit run prettier --all-files
```

### Expected Output:
```
black....................................................................Passed
ruff.....................................................................Passed
mypy.....................................................................Passed
bandit...................................................................Passed
prettier.................................................................Passed
eslint...................................................................Passed
trailing-whitespace......................................................Passed
end-of-file-fixer........................................................Passed
check-yaml...............................................................Passed
```

---

## Step 7: IDE Configuration

### VS Code (Recommended)

**Install Extensions:**
```bash
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.mypy-type-checker
code --install-extension dbaeumer.vscode-eslint
code --install-extension esbenp.prettier-vscode
code --install-extension bradlc.vscode-tailwindcss
```

**Settings Applied Automatically:**
- `.vscode/settings.json` - Format on save, linting
- `.vscode/extensions.json` - Recommended extensions

### PyCharm

1. File → Settings → Project → Python Interpreter
   - Select Poetry environment
2. Tools → Black → Configure
   - Path: `<poetry_env>/bin/black`
3. Tools → External Tools
   - Add Ruff, mypy as external tools

---

## Step 8: Verify Complete Setup

### Run All Checks

**Backend:**
```bash
cd src/backend
poetry shell

# Code quality
black . --check
ruff . --fix
mypy app/

# Security
bandit -r app/

# Tests
pytest --cov
```

**Frontend:**
```bash
cd src/frontend

# Code quality
pnpm lint
pnpm format

# Type checking
pnpm type-check

# Tests
pnpm test
```

### Database Verification

```bash
cd src/backend
python scripts/test_config.py
```

**Expected output:**
```
✅ Environment file found: /path/to/project/.env
✅ Required variables present
✅ Database connected: PostgreSQL 17.7
✅ All tests passed! Configuration is ready.
```

### Test Commit

```bash
# Stage some changes
git add .

# Pre-commit hooks will run automatically
git commit -m "test: verify pre-commit hooks"

# Should see all hooks pass
```

---

## Troubleshooting

### Reset Backend Environment

```bash
cd src/backend
poetry env remove python
poetry install
poetry shell
```

### Reset Frontend Dependencies

```bash
cd src/frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Reset Database

```bash
cd src/backend
python database/init_db.py --drop --seed
```

### Clear All Caches

```bash
# Python
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type d -name ".pytest_cache" -exec rm -r {} +
find . -type d -name ".mypy_cache" -exec rm -r {} +

# Node.js
find . -type d -name "node_modules" -exec rm -r {} +

# Pre-commit
pre-commit clean
```

---

## Development Workflow

### Daily Workflow

1. **Pull latest changes:**
   ```bash
   git pull origin main
   ```

2. **Create feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Start services:**
   ```bash
   # Terminal 1: Backend
   cd src/backend && poetry shell && uvicorn app.main:app --reload
   
   # Terminal 2: Frontend
   cd src/frontend && pnpm dev
   ```

4. **Make changes and test:**
   ```bash
   # Backend tests
   cd src/backend && pytest
   
   # Frontend tests
   cd src/frontend && pnpm test
   ```

5. **Pre-commit will run on commit:**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   # Hooks run automatically
   ```

6. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   # Create PR on GitHub
   ```

### Code Quality Commands

**Format code:**
```bash
# Backend
cd src/backend && black . && ruff . --fix

# Frontend
cd src/frontend && pnpm format
```

**Run linters:**
```bash
# Backend
cd src/backend && ruff . && mypy app/

# Frontend
cd src/frontend && pnpm lint
```

**Run tests with coverage:**
```bash
# Backend
cd src/backend && pytest --cov --cov-report=html

# Frontend
cd src/frontend && pnpm test -- --coverage
```

---

## Next Steps

After completing setup:

1. ✅ Read [CONTRIBUTING.md](../CONTRIBUTING.md) for contribution guidelines
2. ✅ Review [docs/architecture/](../architecture/) for architecture details
3. ✅ Check [ROADMAP.md](../../ROADMAP.md) for planned features
4. ✅ Pick an issue from GitHub Issues to work on
5. ✅ Join discussions in GitHub Discussions

---

## Getting Help

- **Issues:** Create an issue on GitHub
- **Discussions:** Ask in GitHub Discussions
- **Documentation:** Check `/docs` directory
- **Code Examples:** See `/tests` directory

**Happy Coding!** 🚀
