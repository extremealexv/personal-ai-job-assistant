#!/bin/bash
# Quick verification script - checks if everything is ready

echo "Quick Environment Check"
echo "======================="
echo ""

ERRORS=0

# Check .env file
if [ -f .env ]; then
    echo "✓ .env file exists"
else
    echo "✗ .env file missing - run: ./src/backend/scripts/setup_env.sh"
    ERRORS=$((ERRORS + 1))
fi

# Check Poetry
if command -v poetry &> /dev/null; then
    echo "✓ Poetry installed: $(poetry --version)"
else
    echo "✗ Poetry not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit
if command -v pre-commit &> /dev/null; then
    echo "✓ pre-commit installed: $(pre-commit --version)"
else
    echo "✗ pre-commit not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check pnpm
if command -v pnpm &> /dev/null; then
    echo "✓ pnpm installed: $(pnpm --version)"
else
    echo "✗ pnpm not installed"
    ERRORS=$((ERRORS + 1))
fi

# Check pre-commit config
if [ -f .pre-commit-config.yaml ]; then
    echo "✓ .pre-commit-config.yaml exists"
else
    echo "✗ .pre-commit-config.yaml missing"
    ERRORS=$((ERRORS + 1))
fi

# Check if pre-commit hooks are installed
if [ -f .git/hooks/pre-commit ]; then
    echo "✓ pre-commit hooks installed"
else
    echo "✗ pre-commit hooks not installed - run: pre-commit install"
    ERRORS=$((ERRORS + 1))
fi

# Check backend dependencies
if [ -d "src/backend/.venv" ] || [ -f "src/backend/poetry.lock" ]; then
    echo "✓ Backend dependencies installed"
else
    echo "✗ Backend dependencies missing - run: cd src/backend && poetry install"
    ERRORS=$((ERRORS + 1))
fi

# Check frontend dependencies (optional - not set up yet)
if [ -f "src/frontend/package.json" ]; then
    if [ -d "src/frontend/node_modules" ]; then
        echo "✓ Frontend dependencies installed"
    else
        echo "⚠ Frontend dependencies missing - run: cd src/frontend && pnpm install"
        echo "  (Optional: frontend not set up yet)"
    fi
else
    echo "⚠ Frontend not set up yet (optional)"
fi

echo ""
echo "======================="
if [ $ERRORS -eq 0 ]; then
    echo "✓ All critical checks passed!"
    echo "Ready to start development"
    exit 0
else
    echo "✗ $ERRORS critical checks failed"
    echo "See scripts/INSTALLATION_ORDER.md for setup steps"
    exit 1
fi
