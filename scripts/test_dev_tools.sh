#!/bin/bash
# Test all development tools are working correctly

set -e

echo "=================================================="
echo "Testing Development Tools"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_test() {
    echo -e "${YELLOW}Testing:${NC} $1"
}

print_pass() {
    echo -e "${GREEN}✓ PASS:${NC} $1"
}

print_fail() {
    echo -e "${RED}✗ FAIL:${NC} $1"
}

FAILED=0

echo "Backend Tests"
echo "--------------------------------------------------"

# Test 1: Black formatting (dry run)
print_test "Black formatter (dry run)"
cd src/backend
if poetry run black --check app/ 2>/dev/null; then
    print_pass "Black - all files formatted correctly"
else
    print_fail "Black - some files need formatting"
    echo "  Run: cd src/backend && poetry run black app/"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 2: Ruff linting
print_test "Ruff linter"
cd src/backend
if poetry run ruff check app/ 2>/dev/null; then
    print_pass "Ruff - no linting issues"
else
    print_fail "Ruff - linting issues found"
    echo "  Run: cd src/backend && poetry run ruff check app/ --fix"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 3: mypy type checking
print_test "mypy type checker"
cd src/backend
if poetry run mypy app/ 2>/dev/null; then
    print_pass "mypy - no type errors"
else
    print_fail "mypy - type errors found"
    echo "  Review output above and fix type issues"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 4: Bandit security scanning
print_test "Bandit security scanner"
cd src/backend
if poetry run bandit -r app/ -q 2>/dev/null; then
    print_pass "Bandit - no security issues"
else
    print_fail "Bandit - security issues found"
    echo "  Review output above and fix security issues"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 5: Backend tests
print_test "Backend unit tests"
cd src/backend
if poetry run pytest tests/ -q 2>/dev/null; then
    print_pass "pytest - all tests passed"
else
    print_fail "pytest - some tests failed"
    echo "  Run: cd src/backend && poetry run pytest -v"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

echo "Frontend Tests"
echo "--------------------------------------------------"

# Test 6: ESLint
print_test "ESLint linter"
cd src/frontend
if pnpm lint 2>/dev/null; then
    print_pass "ESLint - no linting issues"
else
    print_fail "ESLint - linting issues found"
    echo "  Run: cd src/frontend && pnpm lint:fix"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 7: Prettier formatting
print_test "Prettier formatter (check only)"
cd src/frontend
if pnpm prettier --check \"src/**/*.{ts,tsx,js,jsx}\" 2>/dev/null; then
    print_pass "Prettier - all files formatted correctly"
else
    print_fail "Prettier - some files need formatting"
    echo "  Run: cd src/frontend && pnpm format"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 8: TypeScript type checking
print_test "TypeScript type checker"
cd src/frontend
if pnpm type-check 2>/dev/null; then
    print_pass "TypeScript - no type errors"
else
    print_fail "TypeScript - type errors found"
    echo "  Review output above and fix type issues"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

# Test 9: Frontend tests
print_test "Frontend unit tests"
cd src/frontend
if pnpm test --run 2>/dev/null; then
    print_pass "Frontend tests - all tests passed"
else
    print_fail "Frontend tests - some tests failed"
    echo "  Run: cd src/frontend && pnpm test"
    FAILED=$((FAILED + 1))
fi
cd ../..
echo ""

echo "Pre-commit Hooks Test"
echo "--------------------------------------------------"

# Test 10: Pre-commit hooks
print_test "Pre-commit hooks on all files"
if pre-commit run --all-files 2>/dev/null; then
    print_pass "Pre-commit - all hooks passed"
else
    print_fail "Pre-commit - some hooks failed"
    echo "  Run: pre-commit run --all-files"
    echo "  Some hooks auto-fix issues - review and commit changes"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "=================================================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo "=================================================="
    exit 0
else
    echo -e "${RED}✗ $FAILED tests failed${NC}"
    echo "=================================================="
    echo ""
    echo "Review the failed tests above and fix the issues."
    echo "Many issues can be auto-fixed with:"
    echo "  - Backend: cd src/backend && poetry run black . && poetry run ruff check . --fix"
    echo "  - Frontend: cd src/frontend && pnpm lint:fix && pnpm format"
    exit 1
fi
