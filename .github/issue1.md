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
