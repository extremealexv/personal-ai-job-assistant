### Overview
Install and configure development tools, linters, formatters, and pre-commit hooks for code quality.

### Prerequisites
- Python 3.11+ installed
- Node.js 18+ installed
- Git configured

### Installation Steps

#### 1. Install Git (if not already installed)
```bash
sudo apt update
sudo apt install -y git

# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Verify Git configuration
git config --list
```

#### 2. Install Python Development Tools
```bash
# Activate Poetry shell
cd src/backend
poetry shell

# Install development dependencies
poetry add --group dev black ruff mypy bandit pytest pytest-asyncio pytest-cov pre-commit

# Verify installations
black --version
ruff --version
mypy --version
pytest --version
```

#### 3. Install Frontend Development Tools
```bash
cd src/frontend

# Install ESLint, Prettier, and TypeScript tools
pnpm add -D eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-config-airbnb eslint-config-airbnb-typescript eslint-plugin-react eslint-plugin-react-hooks prettier eslint-config-prettier

# Verify installations
pnpm exec eslint --version
pnpm exec prettier --version
pnpm exec tsc --version
```

#### 4. Setup Pre-commit Hooks
```bash
# Navigate to project root
cd ~/personal-ai-job-assistant

# Install pre-commit globally (if not already done)
pip install pre-commit

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (initial check)
pre-commit run --all-files
```

#### 5. Create Configuration Files
See docs/architecture/CODE_STYLE.md for complete configuration file templates.

### Verification Checklist
- [ ] Git installed and configured
- [ ] Python linters installed (black, ruff, mypy)
- [ ] Frontend tools installed (eslint, prettier, typescript)
- [ ] Pre-commit hooks installed and configured
- [ ] Configuration files created
- [ ] Pre-commit runs successfully on test files

### Test Development Workflow
```bash
# Create test file
cd ~/personal-ai-job-assistant
echo "print('hello world')" > test.py

# Stage file
git add test.py

# Commit (pre-commit hooks will run)
git commit -m "test: verify pre-commit hooks"

# Hooks should format and check the file
```

### Useful Commands
```bash
# Run pre-commit manually
pre-commit run --all-files

# Update pre-commit hooks
pre-commit autoupdate

# Skip pre-commit hooks (not recommended)
git commit --no-verify -m "message"

# Format Python code
cd src/backend
black .
ruff . --fix

# Format TypeScript code
cd src/frontend
pnpm exec prettier --write "src/**/*.{ts,tsx}"
pnpm exec eslint --fix "src/**/*.{ts,tsx}"
```

### Troubleshooting

**If pre-commit fails to install:**
```bash
# Ensure Python 3.11+ is available
python3 --version

# Reinstall pre-commit
pip install --upgrade pre-commit
pre-commit clean
pre-commit install
```

**If mypy fails with missing types:**
```bash
# Install stub packages
poetry add --group dev types-all
```

**If prettier/eslint not found:**
```bash
# Ensure installed in project
cd src/frontend
pnpm install
```

### References
- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [ESLint Documentation](https://eslint.org/)
- [Prettier Documentation](https://prettier.io/)
