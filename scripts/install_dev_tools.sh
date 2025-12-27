#!/bin/bash
# Install development tools for Personal AI Job Assistant
# Run this script on your Linux server to set up the development environment

set -e  # Exit on error

echo "=================================================="
echo "Installing Development Tools"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    print_error "Please don't run this script as root"
    exit 1
fi

echo "Step 1: Checking Python installation"
echo "--------------------------------------------------"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    print_status "Python is installed: $PYTHON_VERSION"

    # Check if version is 3.11 or higher
    REQUIRED_VERSION="3.11"
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
        print_status "Python version is 3.11 or higher"
    else
        print_error "Python 3.11+ is required. Current version: $PYTHON_VERSION"
        print_info "Install Python 3.11+: sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev"
        exit 1
    fi
else
    print_error "Python 3 is not installed"
    print_info "Install it with: sudo apt update && sudo apt install python3.11 python3.11-venv python3.11-dev"
    exit 1
fi
echo ""

echo "Step 2: Installing Poetry"
echo "--------------------------------------------------"
if command -v poetry &> /dev/null; then
    print_status "Poetry is already installed: $(poetry --version)"
else
    print_info "Installing Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -

    # Add Poetry to PATH for this session
    export PATH="$HOME/.local/bin:$PATH"

    if command -v poetry &> /dev/null; then
        print_status "Poetry installed successfully: $(poetry --version)"
        print_info "Add to your shell profile: export PATH=\"\$HOME/.local/bin:\$PATH\""
    else
        print_error "Poetry installation failed"
        exit 1
    fi
fi
echo ""

echo "Step 3: Installing pre-commit"
echo "--------------------------------------------------"
if command -v pre-commit &> /dev/null; then
    print_status "pre-commit is already installed: $(pre-commit --version)"
else
    print_info "Installing pre-commit via pip..."
    # Check if we're in a virtualenv
    if [ -n "$VIRTUAL_ENV" ]; then
        print_info "Detected virtualenv, installing without --user flag"
        python3 -m pip install pre-commit
    else
        python3 -m pip install --user pre-commit
    fi

    if command -v pre-commit &> /dev/null; then
        print_status "pre-commit installed successfully: $(pre-commit --version)"
    else
        print_error "pre-commit installation failed"
        print_info "Try manually: python3 -m pip install pre-commit"
        exit 1
    fi
fi
echo ""

echo "Step 4: Installing Node.js and pnpm"
echo "--------------------------------------------------"
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    print_status "Node.js is installed: $NODE_VERSION"

    # Check if version is 18 or higher
    NODE_MAJOR=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        print_status "Node.js version is 18 or higher"
    else
        print_error "Node.js 18+ is required. Current version: $NODE_VERSION"
        print_info "Install Node.js 18+: https://nodejs.org/en/download/"
        exit 1
    fi
else
    print_error "Node.js is not installed"
    print_info "Install it with: curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - && sudo apt install -y nodejs"
    exit 1
fi

if command -v pnpm &> /dev/null; then
    print_status "pnpm is already installed: $(pnpm --version)"
else
    print_info "Installing pnpm..."
    npm install -g pnpm

    if command -v pnpm &> /dev/null; then
        print_status "pnpm installed successfully: $(pnpm --version)"
    else
        print_error "pnpm installation failed"
        exit 1
    fi
fi
echo ""

echo "Step 5: Installing Backend Dependencies"
echo "--------------------------------------------------"
cd src/backend

print_info "Installing Python dependencies with Poetry..."
poetry install

if [ $? -eq 0 ]; then
    print_status "Backend dependencies installed successfully"
else
    print_error "Backend dependency installation failed"
    exit 1
fi

cd ../..
echo ""

echo "Step 6: Installing Frontend Dependencies"
echo "--------------------------------------------------"
cd src/frontend

if [ -f "package.json" ]; then
    print_info "Installing Node.js dependencies with pnpm..."
    pnpm install

    if [ $? -eq 0 ]; then
        print_status "Frontend dependencies installed successfully"
    else
        print_error "Frontend dependency installation failed"
        exit 1
    fi
else
    print_info "No package.json found - frontend not set up yet (skipping)"
fi

cd ../..
echo ""

echo "Step 7: Installing Browser Extension Dependencies"
echo "--------------------------------------------------"
cd src/extension

if [ -f "package.json" ]; then
    print_info "Installing extension dependencies with npm..."
    npm install

    if [ $? -eq 0 ]; then
        print_status "Extension dependencies installed successfully"
    else
        print_error "Extension dependency installation failed"
        exit 1
    fi
else
    print_info "No package.json found - extension not set up yet (skipping)"
fi

cd ../..
echo ""

echo "Step 8: Installing pre-commit hooks"
echo "--------------------------------------------------"
print_info "Installing pre-commit hooks..."
pre-commit install

if [ $? -eq 0 ]; then
    print_status "Pre-commit hooks installed successfully"
else
    print_error "Pre-commit hooks installation failed"
    exit 1
fi
echo ""

echo "=================================================="
echo "✓ Development Tools Installation Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "1. Run: python scripts/check_dev_tools.py"
echo "2. Run: scripts/test_dev_tools.sh"
echo "3. Test pre-commit: pre-commit run --all-files"
echo ""
echo "Add to your shell profile (~/.bashrc or ~/.zshrc):"
echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
echo ""
