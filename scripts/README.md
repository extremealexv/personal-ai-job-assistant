# Scripts Overview

All scripts for setting up and testing the development environment.

## Quick Reference

| Script | Purpose | Usage |
|--------|---------|-------|
| `install_dev_tools.sh` | Main installation script | `./scripts/install_dev_tools.sh` |
| `setup_pre_commit.sh` | Setup Git hooks | `./scripts/setup_pre_commit.sh` |
| `test_dev_tools.sh` | Test all tools | `./scripts/test_dev_tools.sh` |
| `quick_check.sh` | Quick status check | `./scripts/quick_check.sh` |
| `format_all.sh` | Format all code | `./scripts/format_all.sh` |
| `check_dev_tools.py` | Detailed tool check | `python3 scripts/check_dev_tools.py` |

## Installation Order

See [INSTALLATION_ORDER.md](INSTALLATION_ORDER.md) for complete step-by-step guide.

### Quick Start

```bash
# 1. Setup environment
./src/backend/scripts/setup_env.sh

# 2. Edit .env file
nano .env

# 3. Install all tools
./scripts/install_dev_tools.sh

# 4. Setup hooks
./scripts/setup_pre_commit.sh

# 5. Initialize database
cd src/backend && poetry run python database/init_db.py --drop --seed

# 6. Verify setup
./scripts/quick_check.sh
```

## Backend Scripts

Located in `src/backend/scripts/`:

### `setup_env.sh` / `setup_env.ps1`
- Creates `.env` file from `.env.example`
- Generates `SECRET_KEY` and `ENCRYPTION_KEY`
- Prompts for manual edits

**Usage:**
```bash
./src/backend/scripts/setup_env.sh
```

### `test_config.py`
- Validates `.env` configuration
- Tests database connection
- Checks for placeholder values

**Usage:**
```bash
cd src/backend
poetry run python scripts/test_config.py
```

## Root Scripts

Located in `scripts/`:

### `install_dev_tools.sh`
**Main installation script** - installs all development tools.

**What it does:**
1. Checks Python 3.11+ is installed
2. Installs Poetry (Python package manager)
3. Installs pre-commit (Git hooks)
4. Verifies Node.js 18+ and installs pnpm
5. Installs backend dependencies (`poetry install`)
6. Installs frontend dependencies (`pnpm install`)
7. Installs extension dependencies (`npm install`)
8. Installs pre-commit hooks

**Duration:** 5-10 minutes

**Usage:**
```bash
chmod +x scripts/install_dev_tools.sh
./scripts/install_dev_tools.sh
```

**Requirements:**
- Python 3.11+
- Node.js 18+
- Internet connection

---

### `setup_pre_commit.sh`
Sets up Git pre-commit hooks.

**What it does:**
1. Verifies pre-commit is installed
2. Installs hooks to `.git/hooks/`
3. Downloads and caches hook environments
4. Tests hooks on sample files

**Duration:** 2-5 minutes (first time)

**Usage:**
```bash
./scripts/setup_pre_commit.sh
```

**What gets installed:**
- Python hooks: black, ruff, mypy, bandit
- JavaScript hooks: prettier, eslint
- General hooks: trailing-whitespace, check-yaml, etc.

---

### `test_dev_tools.sh`
Comprehensive test suite for all development tools.

**What it tests:**
- ✓ Black formatting (dry run)
- ✓ Ruff linting
- ✓ mypy type checking
- ✓ Bandit security scanning
- ✓ pytest unit tests
- ✓ ESLint linting
- ✓ Prettier formatting
- ✓ TypeScript type checking
- ✓ Frontend tests
- ✓ Pre-commit hooks

**Duration:** 2-5 minutes

**Usage:**
```bash
./scripts/test_dev_tools.sh
```

**Exit codes:**
- `0` - All tests passed
- `1` - Some tests failed (see output)

---

### `quick_check.sh`
Fast status check to verify setup.

**What it checks:**
- ✓ .env file exists
- ✓ Poetry installed
- ✓ pre-commit installed
- ✓ pnpm installed
- ✓ Configuration files exist
- ✓ Dependencies installed

**Duration:** < 5 seconds

**Usage:**
```bash
./scripts/quick_check.sh
```

**Use this:**
- Before starting development
- After pulling changes
- To verify setup

---

### `format_all.sh`
Formats all code in the project.

**What it formats:**
- Python: Black formatter
- Python: Ruff auto-fixes
- TypeScript/JavaScript: Prettier
- Configuration files: Prettier

**Duration:** 10-30 seconds

**Usage:**
```bash
./scripts/format_all.sh
```

**When to use:**
- Before committing changes
- After pulling upstream changes
- When pre-commit fails on formatting

---

### `check_dev_tools.py`
Detailed Python script that checks all tools.

**What it checks:**
- System prerequisites (Python, Node, Git, PostgreSQL)
- Package managers (Poetry, pnpm, npm)
- Python tools (black, ruff, mypy, bandit, pytest)
- JavaScript tools (eslint, prettier)
- Configuration files
- Database connection

**Duration:** 5-10 seconds

**Usage:**
```bash
python3 scripts/check_dev_tools.py
```

**Output:** Detailed report with version numbers

---

## Troubleshooting Scripts

### Reset backend environment
```bash
cd src/backend
rm -rf .venv poetry.lock
poetry install
```

### Reset frontend dependencies
```bash
cd src/frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

### Reinstall pre-commit hooks
```bash
pre-commit uninstall
pre-commit install
pre-commit install-hooks
```

### Update pre-commit hooks
```bash
pre-commit autoupdate
```

---

## Common Workflows

### First Time Setup
```bash
# 1. Setup environment
./src/backend/scripts/setup_env.sh
nano .env  # Edit configuration

# 2. Install everything
./scripts/install_dev_tools.sh

# 3. Setup hooks
./scripts/setup_pre_commit.sh

# 4. Initialize database
cd src/backend
poetry run python database/init_db.py --drop --seed

# 5. Verify
./scripts/quick_check.sh
python3 scripts/check_dev_tools.py
```

### Daily Development
```bash
# Check status
./scripts/quick_check.sh

# Format code before committing
./scripts/format_all.sh

# Test everything
./scripts/test_dev_tools.sh

# Commit (pre-commit runs automatically)
git add .
git commit -m "feat: your changes"
```

### After Pulling Changes
```bash
# Update dependencies
cd src/backend && poetry install
cd src/frontend && pnpm install

# Update hooks
pre-commit autoupdate

# Verify everything works
./scripts/quick_check.sh
```

### Before Creating PR
```bash
# Format all code
./scripts/format_all.sh

# Run all tests
./scripts/test_dev_tools.sh

# Run pre-commit on all files
pre-commit run --all-files

# Commit any fixes
git add .
git commit -m "style: format code and fix linting issues"
```

---

## CI/CD Integration

These scripts are designed to work in CI/CD pipelines:

**GitHub Actions example:**
```yaml
- name: Install dependencies
  run: ./scripts/install_dev_tools.sh

- name: Run tests
  run: ./scripts/test_dev_tools.sh
```

---

## Permissions

All shell scripts need execute permission:

```bash
chmod +x scripts/*.sh
chmod +x src/backend/scripts/*.sh
```

---

## Help & Documentation

- **Setup Guide:** [INSTALLATION_ORDER.md](INSTALLATION_ORDER.md)
- **Detailed Setup:** [../docs/DEVELOPMENT_SETUP.md](../docs/DEVELOPMENT_SETUP.md)
- **Code Style:** [../docs/architecture/CODE_STYLE.md](../docs/architecture/CODE_STYLE.md)
- **Contributing:** [../CONTRIBUTING.md](../CONTRIBUTING.md)

---

## Getting Help

If scripts fail:
1. Read the error message carefully
2. Check prerequisites are installed
3. Verify .env file is configured
4. Review logs from failed step
5. Try running individual commands manually
6. Check GitHub Issues for similar problems

**Common Issues:**
- `command not found` → Tool not in PATH
- `permission denied` → Run `chmod +x script.sh`
- `connection refused` → Database not running
- `poetry: command not found` → Add to PATH: `export PATH="$HOME/.local/bin:$PATH"`
