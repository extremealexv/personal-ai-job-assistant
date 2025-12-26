### Overview
Set up environment variables, configuration files, and secure secrets management.

### Prerequisites
- All previous setup steps completed
- Database and services running

### Installation Steps

#### 1. Create .env File Template
```bash
cd ~/personal-ai-job-assistant

# Create .env file (DO NOT COMMIT)
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

#### 3. Configure Environment Variables
Edit `.env` file with:
```bash
# Database Configuration
DATABASE_URL=postgresql://ai_job_user:your_password@localhost:5432/ai_job_assistant
DATABASE_ASYNC_URL=postgresql+asyncpg://ai_job_user:your_password@localhost:5432/ai_job_assistant

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Application Configuration
APP_ENV=development
SECRET_KEY=your-generated-secret-key
DEBUG=true

# API Keys (DO NOT COMMIT)
OPENAI_API_KEY=sk-...your-key-here

# Encryption Key
ENCRYPTION_KEY=your-generated-encryption-key

# Frontend Configuration
VITE_API_BASE_URL=http://localhost:8000
```

#### 4. Configure Backend Settings
```bash
cd src/backend

# Install python-dotenv
poetry add python-dotenv

# Settings will be loaded from .env file
```

#### 5. Configure Frontend Environment
```bash
cd src/frontend

# Create .env.local (not committed)
cat > .env.local << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_NAME="Personal AI Job Assistant"
EOF
```

#### 6. Configure CORS for Development
Update backend to allow frontend origins for local development.

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
poetry run python -c "from app.config import settings; print('Config loaded successfully')"

# Verify .env not tracked by git
git status | grep .env
# Should not appear in tracked files
```

### Security Best Practices

**Never commit these files:**
```bash
# Verify .gitignore
cat .gitignore | grep -E "\.env|secrets|\.key"
```

**Rotate keys regularly:**
- Generate new keys periodically
- Update .env
- Restart services

### Troubleshooting

**If environment variables not loading:**
```bash
# Check .env file location
ls -la .env

# Check file format (no spaces around =)
cat .env | grep -v "^#" | grep "="
```

**If CORS errors in browser:**
- Check backend CORS configuration
- Ensure frontend URL is in allow_origins list
- Restart backend server

### References
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [12 Factor App Config](https://12factor.net/config)
