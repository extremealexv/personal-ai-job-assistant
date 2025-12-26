### Overview
Install Python 3.11+ and Poetry package manager for backend development.

### Prerequisites
- Ubuntu Server 22.04 LTS or newer
- Sudo access

### Installation Steps

#### 1. Install Python 3.11
```bash
# Add deadsnakes PPA for latest Python versions
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# Install Python 3.11 and related packages
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3.11-distutils
```

#### 2. Set Python 3.11 as Default (Optional)
```bash
# Install update-alternatives
sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Verify Python version
python3 --version
# Expected: Python 3.11.x
```

#### 3. Install pip for Python 3.11
```bash
# Download get-pip.py
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11

# Verify pip installation
python3.11 -m pip --version
```

#### 4. Install Poetry
```bash
# Install Poetry using official installer
curl -sSL https://install.python-poetry.org | python3.11 -

# Add Poetry to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Verify Poetry installation
poetry --version
# Expected: Poetry (version 1.7.0+)
```

#### 5. Configure Poetry
```bash
# Configure Poetry to create virtual environments in project directory
poetry config virtualenvs.in-project true

# Verify configuration
poetry config --list
```

#### 6. Install Development Tools
```bash
# Install build essentials
sudo apt install -y build-essential libssl-dev libffi-dev python3.11-dev

# Install additional dependencies
sudo apt install -y libpq-dev  # PostgreSQL client library
```

#### 7. Install Pre-commit
```bash
# Install pre-commit globally
python3.11 -m pip install pre-commit

# Verify installation
pre-commit --version
```

### Verification Checklist
- [ ] Python 3.11+ installed
- [ ] pip installed for Python 3.11
- [ ] Poetry installed and in PATH
- [ ] Poetry configured for in-project virtualenvs
- [ ] Build tools installed
- [ ] pre-commit installed

### Test Backend Setup
```bash
# Navigate to backend directory
cd src/backend

# Initialize Poetry project (if not already initialized)
poetry init --no-interaction

# Install basic dependencies
poetry add fastapi uvicorn sqlalchemy asyncpg

# Verify installation
poetry run python -c "import fastapi; print(f'FastAPI {fastapi.__version__}')"
```

### Environment Setup
Create a virtual environment:
```bash
cd src/backend
poetry install
poetry shell  # Activate virtual environment
```

### Troubleshooting

**If Poetry not found after installation:**
```bash
# Manually add to PATH
export PATH="$HOME/.local/bin:$PATH"
source ~/.bashrc
```

**If Python 3.11 not found:**
```bash
# Check available Python versions
ls -l /usr/bin/python*
```

**If pip installation fails:**
```bash
# Install pip using apt
sudo apt install -y python3.11-pip
```

### References
- [Python Installation Guide](https://www.python.org/downloads/)
- [Poetry Documentation](https://python-poetry.org/docs/)
- [Deadsnakes PPA](https://launchpad.net/~deadsnakes/+archive/ubuntu/ppa)
