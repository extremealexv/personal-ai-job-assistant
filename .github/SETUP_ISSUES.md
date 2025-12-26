# Development Environment Setup Issues

Copy each issue below into GitHub Issues to track environment setup progress.

---

## Issue 1: Install PostgreSQL 15+ on Ubuntu Server

**Labels:** `setup`, `infrastructure`, `database`

**Title:** Setup: Install PostgreSQL 15+ on Ubuntu Server

**Description:**

### Overview
Install and configure PostgreSQL 15+ for the Personal AI Job Assistant database.

### Prerequisites
- Ubuntu Server 22.04 LTS or newer
- Sudo access

### Installation Steps

#### 1. Update System Packages
```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install PostgreSQL 15
```bash
# Add PostgreSQL APT repository
sudo apt install -y postgresql-common
sudo /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh

# Install PostgreSQL 15
sudo apt install -y postgresql-15 postgresql-contrib-15
```

#### 3. Verify Installation
```bash
# Check PostgreSQL version
psql --version
# Expected: psql (PostgreSQL) 15.x

# Check service status
sudo systemctl status postgresql
```

#### 4. Configure PostgreSQL

**Set postgres user password:**
```bash
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'your_secure_password';"
```

**Enable remote connections (if needed):**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/15/main/postgresql.conf
# Change: listen_addresses = 'localhost' to listen_addresses = '*'

# Edit pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf
# Add line: host    all    all    0.0.0.0/0    scram-sha-256

# Restart PostgreSQL
sudo systemctl restart postgresql
```

#### 5. Create Database and User
```bash
sudo -u postgres psql << EOF
CREATE DATABASE ai_job_assistant;
CREATE USER ai_job_user WITH ENCRYPTED PASSWORD 'your_db_password';
GRANT ALL PRIVILEGES ON DATABASE ai_job_assistant TO ai_job_user;
\c ai_job_assistant
GRANT ALL ON SCHEMA public TO ai_job_user;
EOF
```

#### 6. Install Required Extensions
```bash
sudo -u postgres psql -d ai_job_assistant << EOF
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
EOF
```

#### 7. Configure Firewall (if enabled)
```bash
# Allow PostgreSQL through firewall
sudo ufw allow 5432/tcp
sudo ufw reload
```

#### 8. Test Connection
```bash
# Test local connection
psql -h localhost -U ai_job_user -d ai_job_assistant -W
# Enter password when prompted
# Type \q to exit
```

### Verification Checklist
- [ ] PostgreSQL 15+ installed and running
- [ ] Database `ai_job_assistant` created
- [ ] User `ai_job_user` created with proper permissions
- [ ] Extensions installed (uuid-ossp, pgcrypto, pg_trgm)
- [ ] Can connect to database successfully

### Environment Variables
Add to your `.env` file:
```bash
DATABASE_URL=postgresql://ai_job_user:your_db_password@localhost:5432/ai_job_assistant
```

### Troubleshooting

**If PostgreSQL fails to start:**
```bash
sudo journalctl -u postgresql@15-main.service -n 50
sudo systemctl status postgresql@15-main.service
```

**If connection refused:**
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify port is listening: `sudo netstat -plunt | grep 5432`
- Check pg_hba.conf authentication settings

### References
- [PostgreSQL Ubuntu Installation](https://www.postgresql.org/download/linux/ubuntu/)
- [PostgreSQL First Steps](https://www.postgresql.org/docs/15/tutorial-start.html)

---

## Issue 2: Install Python 3.11+ and Poetry on Ubuntu Server

**Labels:** `setup`, `infrastructure`, `backend`

**Title:** Setup: Install Python 3.11+ and Poetry on Ubuntu Server

**Description:**

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

---

## Issue 3: Install Node.js 18+ and pnpm on Ubuntu Server

**Labels:** `setup`, `infrastructure`, `frontend`

**Title:** Setup: Install Node.js 18+ and pnpm on Ubuntu Server

**Description:**

### Overview
Install Node.js 18+ and pnpm package manager for frontend and extension development.

### Prerequisites
- Ubuntu Server 22.04 LTS or newer
- Sudo access

### Installation Steps

#### 1. Install Node.js 18 LTS using NodeSource
```bash
# Download and setup NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -

# Install Node.js
sudo apt install -y nodejs

# Verify installation
node --version   # Expected: v18.x.x
npm --version    # Expected: 9.x.x or higher
```

#### Alternative: Install via nvm (Recommended for Development)
```bash
# Install nvm (Node Version Manager)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.5/install.sh | bash

# Load nvm into current session
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

# Add to bashrc for permanent access
echo 'export NVM_DIR="$HOME/.nvm"' >> ~/.bashrc
echo '[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"' >> ~/.bashrc
source ~/.bashrc

# Install Node.js 18 LTS
nvm install 18
nvm use 18
nvm alias default 18

# Verify installation
node --version
npm --version
```

#### 2. Install pnpm (Faster Alternative to npm)
```bash
# Install pnpm globally
npm install -g pnpm

# Verify pnpm installation
pnpm --version
# Expected: 8.x.x or higher

# Configure pnpm
pnpm setup
source ~/.bashrc
```

#### 3. Configure npm/pnpm Registry (Optional)
```bash
# Set registry (use default or custom mirror)
pnpm config set registry https://registry.npmjs.org/

# Verify configuration
pnpm config get registry
```

#### 4. Install Global Development Tools
```bash
# Install TypeScript globally
pnpm add -g typescript

# Install Vite CLI (optional)
pnpm add -g vite

# Verify installations
tsc --version
vite --version
```

### Verification Checklist
- [ ] Node.js 18+ installed
- [ ] npm installed and working
- [ ] pnpm installed globally
- [ ] TypeScript installed globally
- [ ] Can create and run Node.js scripts

### Test Frontend Setup
```bash
# Navigate to frontend directory
cd src/frontend

# Initialize package.json (if not exists)
pnpm init

# Install basic dependencies
pnpm add react react-dom
pnpm add -D vite @vitejs/plugin-react typescript

# Verify installation
node -e "console.log('Node.js:', process.version)"
pnpm list --depth=0
```

### Environment Configuration

**Configure package manager:**
```bash
# Use pnpm for this project
echo "package-manager=pnpm" >> .npmrc
```

**Set up TypeScript:**
```bash
cd src/frontend
pnpm tsc --init
```

### Troubleshooting

**If Node.js installation fails:**
```bash
# Remove existing Node.js installations
sudo apt remove nodejs
sudo apt autoremove

# Clean npm cache
sudo rm -rf /usr/local/lib/node_modules
sudo rm -rf ~/.npm

# Reinstall
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**If pnpm command not found:**
```bash
# Install via npm
npm install -g pnpm

# Or use corepack (Node.js 16.13+)
corepack enable
corepack prepare pnpm@latest --activate
```

**Check Node.js path:**
```bash
which node
which npm
which pnpm
```

### Performance Tips
```bash
# Increase max memory for Node.js
export NODE_OPTIONS="--max-old-space-size=4096"

# Add to bashrc
echo 'export NODE_OPTIONS="--max-old-space-size=4096"' >> ~/.bashrc
```

### References
- [Node.js Official Downloads](https://nodejs.org/)
- [NodeSource Setup](https://github.com/nodesource/distributions)
- [pnpm Documentation](https://pnpm.io/)
- [nvm GitHub](https://github.com/nvm-sh/nvm)

---

## Issue 4: Install Docker and Docker Compose on Ubuntu Server

**Labels:** `setup`, `infrastructure`, `docker`

**Title:** Setup: Install Docker and Docker Compose on Ubuntu Server

**Description:**

### Overview
Install Docker and Docker Compose for running Redis, PostgreSQL (optional), and other containerized services.

### Prerequisites
- Ubuntu Server 22.04 LTS or newer
- Sudo access

### Installation Steps

#### 1. Uninstall Old Docker Versions (if any)
```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

#### 2. Install Docker Dependencies
```bash
sudo apt update
sudo apt install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release
```

#### 3. Add Docker GPG Key
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

#### 4. Add Docker Repository
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

#### 5. Install Docker Engine
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

#### 6. Verify Docker Installation
```bash
# Check Docker version
docker --version
# Expected: Docker version 24.0.x+

# Check Docker Compose version
docker compose version
# Expected: Docker Compose version v2.x.x+
```

#### 7. Start and Enable Docker Service
```bash
sudo systemctl start docker
sudo systemctl enable docker

# Verify service is running
sudo systemctl status docker
```

#### 8. Add User to Docker Group (Run without sudo)
```bash
# Add current user to docker group
sudo usermod -aG docker $USER

# Apply group changes (logout/login or use newgrp)
newgrp docker

# Verify docker works without sudo
docker run hello-world
```

#### 9. Configure Docker Daemon (Optional)
```bash
# Create daemon configuration
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json > /dev/null <<EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

# Restart Docker to apply changes
sudo systemctl restart docker
```

#### 10. Test Redis Container
```bash
# Run Redis container
docker run -d --name redis-test -p 6379:6379 redis:7-alpine

# Test Redis connection
docker exec -it redis-test redis-cli ping
# Expected: PONG

# Stop and remove test container
docker stop redis-test
docker rm redis-test
```

### Create Docker Compose File for Services
```bash
# Navigate to project root
cd ~/personal-ai-job-assistant

# Create docker-compose.yml
cat > docker-compose.dev.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    container_name: ai-job-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

  postgres:
    image: postgres:15-alpine
    container_name: ai-job-postgres
    environment:
      POSTGRES_DB: ai_job_assistant
      POSTGRES_USER: ai_job_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
EOF

# Start services
docker compose -f docker-compose.dev.yml up -d

# Check running containers
docker ps
```

### Verification Checklist
- [ ] Docker Engine installed
- [ ] Docker Compose V2 installed
- [ ] Docker service running and enabled
- [ ] User added to docker group (can run without sudo)
- [ ] Redis container runs successfully
- [ ] docker-compose.yml created for dev services

### Useful Docker Commands
```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View running containers
docker ps

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune
```

### Troubleshooting

**If Docker permission denied:**
```bash
# Ensure you're in docker group
groups | grep docker

# If not, re-add to group
sudo usermod -aG docker $USER

# Logout and login again, or run:
newgrp docker
```

**If Docker service fails to start:**
```bash
# Check service status and logs
sudo systemctl status docker
sudo journalctl -u docker.service -n 50
```

**If port already in use:**
```bash
# Check what's using the port
sudo netstat -plunt | grep 6379

# Kill the process or change docker-compose port mapping
```

### Security Configuration (Production)
```bash
# Enable firewall
sudo ufw enable

# Allow Docker ports (be specific)
sudo ufw allow from 172.17.0.0/16 to any port 5432
sudo ufw allow from 172.17.0.0/16 to any port 6379
```

### References
- [Docker Official Installation](https://docs.docker.com/engine/install/ubuntu/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Post-Installation](https://docs.docker.com/engine/install/linux-postinstall/)

---

## Issue 5: Setup Development Tools and Pre-commit Hooks

**Labels:** `setup`, `developer-experience`, `code-quality`

**Title:** Setup: Configure Development Tools and Pre-commit Hooks

**Description:**

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
poetry add --group dev \
    black \
    ruff \
    mypy \
    bandit \
    pytest \
    pytest-asyncio \
    pytest-cov \
    pre-commit

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
pnpm add -D \
    eslint \
    @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin \
    eslint-config-airbnb \
    eslint-config-airbnb-typescript \
    eslint-plugin-react \
    eslint-plugin-react-hooks \
    prettier \
    eslint-config-prettier

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

# Create .pre-commit-config.yaml
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict]

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v3.1.0
    hooks:
      - id: prettier
        types_or: [javascript, typescript, tsx, json, css, markdown]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
EOF

# Install pre-commit hooks
pre-commit install

# Run pre-commit on all files (initial check)
pre-commit run --all-files
```

#### 5. Setup VS Code Server (Optional, for Remote Development)
```bash
# Install code-server for web-based VS Code
curl -fsSL https://code-server.dev/install.sh | sh

# Start code-server
code-server --bind-addr 0.0.0.0:8080

# Or setup systemd service
sudo systemctl enable --now code-server@$USER

# Access at: http://your-server-ip:8080
# Default password in: ~/.config/code-server/config.yaml
```

#### 6. Create Configuration Files

**Python pyproject.toml additions:**
```bash
cd src/backend
cat >> pyproject.toml << 'EOF'

[tool.black]
line-length = 100
target-version = ['py311']

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "ANN", "S", "B"]

[tool.mypy]
python_version = "3.11"
strict = true
EOF
```

**Frontend .eslintrc.json:**
```bash
cd src/frontend
cat > .eslintrc.json << 'EOF'
{
  "root": true,
  "extends": [
    "airbnb",
    "airbnb-typescript",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "project": "./tsconfig.json"
  }
}
EOF
```

**Frontend .prettierrc:**
```bash
cat > .prettierrc << 'EOF'
{
  "semi": true,
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
EOF
```

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

---

## Issue 6: Environment Configuration and Secrets Management

**Labels:** `setup`, `configuration`, `security`

**Title:** Setup: Configure Environment Variables and Secrets

**Description:**

### Overview
Set up environment variables, configuration files, and secure secrets management.

### Prerequisites
- All previous setup steps completed
- Database and services running

### Installation Steps

#### 1. Create .env File Template
```bash
cd ~/personal-ai-job-assistant

# Create .env.example template
cat > .env.example << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://ai_job_user:your_password@localhost:5432/ai_job_assistant
DATABASE_ASYNC_URL=postgresql+asyncpg://ai_job_user:your_password@localhost:5432/ai_job_assistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Configuration
APP_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DEBUG=true

# API Keys (DO NOT COMMIT)
OPENAI_API_KEY=sk-...your-key-here
ANTHROPIC_API_KEY=sk-ant-...your-key-here

# Gmail OAuth (for email integration)
GMAIL_CLIENT_ID=your-client-id
GMAIL_CLIENT_SECRET=your-client-secret

# Google Calendar OAuth
GOOGLE_CALENDAR_CLIENT_ID=your-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-client-secret

# Encryption Key (for credentials)
ENCRYPTION_KEY=generate-a-32-byte-key-here

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME="Personal AI Job Assistant"
EOF

# Copy to actual .env (DO NOT COMMIT)
cp .env.example .env

# Add .env to .gitignore
echo ".env" >> .gitignore
echo ".env.local" >> .gitignore
```

#### 2. Generate Secure Keys
```bash
# Generate SECRET_KEY for backend
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (32 bytes, base64)
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Update .env with generated keys
nano .env
```

#### 3. Configure Backend Environment
```bash
cd src/backend

# Install python-dotenv
poetry add python-dotenv

# Create config.py for settings management
cat > app/config.py << 'EOF'
"""Application configuration."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str
    database_async_url: str
    
    # Redis
    redis_url: str
    
    # Application
    app_env: str = "development"
    secret_key: str
    debug: bool = True
    
    # API Keys
    openai_api_key: str
    
    # Encryption
    encryption_key: str
    
    class Config:
        env_file = "../../.env"
        case_sensitive = False

settings = Settings()
EOF
```

#### 4. Configure Frontend Environment
```bash
cd src/frontend

# Create .env.local (not committed)
cat > .env.local << 'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME="Personal AI Job Assistant"
EOF

# Create env.d.ts for TypeScript
cat > src/env.d.ts << 'EOF'
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
  readonly VITE_APP_NAME: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
EOF
```

#### 5. Setup Secrets Management (Optional - Production)

**Option A: Use environment variables directly (Development)**
```bash
# Already done in steps above
```

**Option B: Use systemd environment files (Production)**
```bash
# Create systemd environment file
sudo mkdir -p /etc/ai-job-assistant
sudo nano /etc/ai-job-assistant/env

# Add variables (same as .env format)
# Restrict permissions
sudo chmod 600 /etc/ai-job-assistant/env
sudo chown $USER:$USER /etc/ai-job-assistant/env
```

**Option C: Use Docker secrets (Production)**
```bash
# Create secrets directory
mkdir -p .secrets

# Store sensitive values in separate files
echo "your-openai-key" > .secrets/openai_api_key
echo "your-db-password" > .secrets/db_password

# Update docker-compose.yml to use secrets
# (See Docker documentation for details)

# Add to .gitignore
echo ".secrets/" >> .gitignore
```

#### 6. Configure CORS for Development
```bash
cd src/backend

# Update main.py with CORS middleware
cat >> app/main.py << 'EOF'

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
EOF
```

### Verification Checklist
- [ ] .env file created with all required variables
- [ ] SECRET_KEY and ENCRYPTION_KEY generated
- [ ] .env added to .gitignore
- [ ] Backend can load environment variables
- [ ] Frontend can access VITE_ variables
- [ ] Sensitive files not committed to git

### Test Configuration
```bash
# Test backend config loading
cd src/backend
poetry run python -c "from app.config import settings; print(f'Database: {settings.database_url[:20]}...')"

# Test frontend env loading
cd src/frontend
cat > test-env.ts << 'EOF'
console.log('API URL:', import.meta.env.VITE_API_BASE_URL);
EOF
pnpm vite --open
```

### Security Best Practices

**Never commit these files:**
```bash
# Add to .gitignore
cat >> .gitignore << 'EOF'
.env
.env.local
.env.*.local
.secrets/
*.pem
*.key
*.cert
EOF
```

**Rotate keys regularly:**
```bash
# Schedule key rotation (example: every 90 days)
# Generate new keys
# Update .env
# Restart services
```

**Use environment-specific configs:**
```bash
# Development
.env.development

# Staging
.env.staging

# Production
.env.production
```

### Troubleshooting

**If environment variables not loading:**
```bash
# Check .env file location
ls -la .env

# Check file contents (careful with sensitive data)
cat .env | grep -v "KEY\|SECRET"

# Verify python-dotenv installed
poetry show python-dotenv
```

**If CORS errors in browser:**
```bash
# Check backend CORS configuration
# Ensure frontend URL is in allow_origins list
# Restart backend server
```

### References
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [12 Factor App Config](https://12factor.net/config)

---

## Completion Checklist

Once all issues are resolved, verify complete setup:

```bash
# Backend
cd src/backend
poetry run python -c "import fastapi, sqlalchemy, psycopg2; print('✅ Backend dependencies OK')"

# Frontend
cd src/frontend
pnpm exec tsc --version && echo "✅ Frontend tools OK"

# Services
docker ps | grep redis && echo "✅ Redis running"
psql -h localhost -U ai_job_user -d ai_job_assistant -c "SELECT version();" && echo "✅ PostgreSQL OK"

# Pre-commit
cd ~/personal-ai-job-assistant
pre-commit run --all-files && echo "✅ Pre-commit hooks OK"
```

---

## Next Steps After Setup

1. Initialize database schema: `python src/backend/database/init_db.py --drop --seed`
2. Start development servers
3. Begin Phase 1 development (see ROADMAP.md)
