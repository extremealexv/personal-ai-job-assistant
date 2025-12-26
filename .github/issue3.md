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
