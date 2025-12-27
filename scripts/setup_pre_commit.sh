#!/bin/bash
# Install and configure pre-commit hooks

set -e

echo "=================================================="
echo "Setting up Pre-commit Hooks"
echo "=================================================="
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}ℹ${NC} $1"
}

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    print_error "pre-commit is not installed"
    print_info "Install it with: python3 -m pip install --user pre-commit"
    exit 1
fi

print_status "pre-commit is installed: $(pre-commit --version)"
echo ""

# Check if .pre-commit-config.yaml exists
if [ ! -f .pre-commit-config.yaml ]; then
    print_error ".pre-commit-config.yaml not found in project root"
    exit 1
fi

print_status "Configuration file found: .pre-commit-config.yaml"
echo ""

# Install pre-commit hooks
print_info "Installing pre-commit hooks to .git/hooks/"
if pre-commit install; then
    print_status "Pre-commit hooks installed successfully"
else
    print_error "Failed to install pre-commit hooks"
    exit 1
fi
echo ""

# Install pre-commit hooks for commit-msg (optional)
print_info "Installing commit-msg hook (for conventional commits)"
if pre-commit install --hook-type commit-msg; then
    print_status "Commit-msg hook installed"
else
    print_info "Commit-msg hook installation skipped (optional)"
fi
echo ""

# Download and cache pre-commit environments
print_info "Downloading and setting up hook environments..."
print_info "This may take a few minutes on first run..."
if pre-commit install-hooks; then
    print_status "All hook environments installed"
else
    print_error "Failed to install hook environments"
    exit 1
fi
echo ""

# Test pre-commit on a few files
print_info "Testing pre-commit hooks on existing files..."
if pre-commit run --files .pre-commit-config.yaml README.md; then
    print_status "Pre-commit test passed"
else
    print_info "Pre-commit made some changes (this is normal)"
    print_info "Hooks will auto-fix formatting issues when you commit"
fi
echo ""

echo "=================================================="
echo "✓ Pre-commit Setup Complete!"
echo "=================================================="
echo ""
echo "What happens now:"
echo "  • Every time you 'git commit', pre-commit will:"
echo "    - Format Python code with Black"
echo "    - Lint Python code with Ruff"
echo "    - Check types with mypy"
echo "    - Scan for security issues with Bandit"
echo "    - Format JavaScript/TypeScript with Prettier"
echo "    - Lint JavaScript/TypeScript with ESLint"
echo "    - Check for trailing whitespace, large files, etc."
echo ""
echo "Testing pre-commit:"
echo "  Run: pre-commit run --all-files"
echo ""
echo "Bypassing hooks (not recommended):"
echo "  Run: git commit --no-verify"
echo ""
echo "Updating hooks:"
echo "  Run: pre-commit autoupdate"
echo ""
