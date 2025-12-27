# Installation Order Guide

This guide provides the exact order to run scripts for setting up the development environment on your Linux server.

## Prerequisites

Make sure you have:
- [x] Linux server with sudo access
- [x] Python 3.11+ installed
- [x] Node.js 18+ installed
- [x] PostgreSQL 15+ installed and running
- [x] Git installed

Check prerequisites:
```bash
python3 --version    # Should be 3.11+
node --version       # Should be 18+
psql --version      # Should be 15+
git --version
```

---

## Step-by-Step Installation

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/extremealexv/personal-ai-job-assistant.git
cd personal-ai-job-assistant

# Switch to the dev tools branch (if not already merged)
git checkout setup/dev-tools-23
```

---

### Step 2: Make Scripts Executable

```bash
chmod +x scripts/*.sh
chmod +x src/backend/scripts/*.sh
```

---

### Step 3: Setup Environment Variables

```bash
# Run the environment setup script
./src/backend/scripts/setup_env.sh

# This will:
# - Create .env file in project root
# - Generate SECRET_KEY and ENCRYPTION_KEY
# - Prompt you to edit database credentials
```

**Important:** Edit the `.env` file and update:
- `DATABASE_ASYNC_URL` - Your PostgreSQL connection string
- `OPENAI_API_KEY` - Your OpenAI API key (if available)
- Other settings as needed

```bash
nano .env    # or vim .env
```

---

### Step 4: Verify Configuration

```bash
# Test configuration (requires .env to be set up)
python3 scripts/check_dev_tools.py

# This checks:
# - Python version
# - Configuration files exist
# - .env file is present

# Note: This will show some tools as "not installed" - that's expected
```

---

### Step 5: Install Development Tools

```bash
# Run the main installation script
./scripts/install_dev_tools.sh

# This will:
# 1. Install Poetry (Python package manager)
# 2. Install pre-commit (Git hooks framework)
# 3. Verify Node.js and install pnpm
# 4. Install backend dependencies (Poetry)
# 5. Install frontend dependencies (pnpm)
# 6. Install extension dependencies (npm)
# 7. Install pre-commit hooks

# Duration: 5-10 minutes depending on internet speed
```

**Note:** If the script fails, check the error message and fix the issue, then re-run.

---

### Step 6: Add Poetry to PATH

If Poetry was just installed, add it to your PATH:

```bash
# Add to ~/.bashrc or ~/.zshrc
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify
poetry --version
```

---

### Step 7: Setup Pre-commit Hooks

```bash
# Run pre-commit setup script
./scripts/setup_pre_commit.sh

# This will:
# 1. Verify pre-commit is installed
# 2. Install hooks to .git/hooks/
# 3. Download and cache hook environments
# 4. Test hooks on existing files

# Duration: 2-5 minutes (first time only)
```

---

### Step 8: Initialize Database

```bash
cd src/backend

# Initialize database with schema
poetry run python database/init_db.py --drop --seed

# This will:
# - Connect to PostgreSQL
# - Drop existing schema (if --drop flag)
# - Create all 15 tables
# - Add seed data (if --seed flag)

cd ../..
```

**Verify database:**
```bash
psql -U ai_job_user -d ai_job_assistant -c "\dt"
# Should show 15 tables
```

---

### Step 9: Test Configuration

```bash
# Test backend configuration
cd src/backend
poetry run python scripts/test_config.py

# Expected output:
# ✅ Environment file found
# ✅ Required variables present
# ✅ Database connected: PostgreSQL X.X
# ✅ All tests passed!

cd ../..
```

---

### Step 10: Run Development Tools Tests

```bash
# Run comprehensive test suite
./scripts/test_dev_tools.sh

# This tests:
# - Black formatting
# - Ruff linting
# - mypy type checking
# - Bandit security scanning
# - Backend pytest tests
# - ESLint linting
# - Prettier formatting
# - TypeScript type checking
# - Frontend tests
# - Pre-commit hooks

# Note: Some tests may fail if no code exists yet - that's expected
```

---

### Step 11: Verify Pre-commit Works

```bash
# Test pre-commit on all files
pre-commit run --all-files

# Expected output:
# black....................................................................Passed
# ruff.....................................................................Passed
# mypy.....................................................................Passed
# bandit...................................................................Passed
# prettier.................................................................Passed
# eslint...................................................................Passed
# trailing-whitespace......................................................Passed
# end-of-file-fixer........................................................Passed
# check-yaml...............................................................Passed

# Note: First run may auto-fix some files
```

---

### Step 12: Test a Commit

```bash
# Make a small change
echo "# Test" >> TEST.md

# Stage and commit
git add TEST.md
git commit -m "test: verify pre-commit hooks work"

# Pre-commit hooks should run automatically
# If they pass, the commit succeeds
# If they fail, the commit is blocked

# Clean up test file
rm TEST.md
```

---

## Verification Checklist

After completing all steps, verify:

- [ ] `poetry --version` works
- [ ] `pre-commit --version` works
- [ ] `pnpm --version` works
- [ ] `.env` file exists in project root
- [ ] Database has 15 tables
- [ ] `python3 scripts/check_dev_tools.py` shows all tools installed
- [ ] `./scripts/test_dev_tools.sh` passes (or shows expected failures)
- [ ] `pre-commit run --all-files` completes
- [ ] Test commit triggers pre-commit hooks

---

## Troubleshooting

### Poetry not found after installation

```bash
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc  # or ~/.zshrc
```

### pre-commit command not found

```bash
python3 -m pip install --user pre-commit
export PATH="$HOME/.local/bin:$PATH"
```

### Database connection failed

Check:
1. PostgreSQL is running: `sudo systemctl status postgresql`
2. User and database exist: `psql -U postgres -l`
3. `.env` has correct `DATABASE_ASYNC_URL`

### Permission denied on scripts

```bash
chmod +x scripts/*.sh
chmod +x src/backend/scripts/*.sh
```

### Poetry install fails

```bash
cd src/backend
rm -rf .venv poetry.lock
poetry install
```

### Frontend install fails

```bash
cd src/frontend
rm -rf node_modules pnpm-lock.yaml
pnpm install
```

---

## Next Steps

After successful installation:

1. **Start Backend:**
   ```bash
   cd src/backend
   poetry shell
   uvicorn app.main:app --reload --port 8000
   ```

2. **Start Frontend (in another terminal):**
   ```bash
   cd src/frontend
   pnpm dev
   ```

3. **Build Extension:**
   ```bash
   cd src/extension
   npm run build
   ```

4. **Read Documentation:**
   - [DEVELOPMENT_SETUP.md](../docs/DEVELOPMENT_SETUP.md) - Detailed setup guide
   - [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
   - [CODE_STYLE.md](../docs/architecture/CODE_STYLE.md) - Code style standards

5. **Start Developing:**
   - Check GitHub Issues for tasks
   - Create feature branch: `git checkout -b feature/your-feature`
   - Make changes and commit (hooks will run automatically)

---

## Summary of Scripts

| Script | Purpose | When to Run |
|--------|---------|-------------|
| `setup_env.sh` | Create .env file | Once, before anything else |
| `check_dev_tools.py` | Check what's installed | Anytime to verify setup |
| `install_dev_tools.sh` | Install all tools | Once, main installation |
| `setup_pre_commit.sh` | Setup Git hooks | Once, after install_dev_tools |
| `test_dev_tools.sh` | Test all tools work | After installation, before committing |
| `test_config.py` | Test configuration | After .env setup, verify database |

---

## Getting Help

- **Issues:** Check error messages carefully
- **Logs:** Review output from each script
- **Documentation:** See `docs/DEVELOPMENT_SETUP.md`
- **GitHub Issues:** Create issue if stuck

**Happy Coding!** 🚀
