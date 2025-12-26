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
sudo apt install -y ca-certificates curl gnupg lsb-release
```

#### 3. Add Docker GPG Key
```bash
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
```

#### 4. Add Docker Repository
```bash
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
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

# Create docker-compose.yml (content provided in project documentation)
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
