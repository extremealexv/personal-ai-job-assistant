#!/bin/bash
# Quick fix for syntax errors in test_auth_endpoints.py
# This manually fixes the broken dictionary entries

set -e

echo "🔧 Fixing syntax errors in test_auth_endpoints.py..."

TEST_FILE="src/backend/tests/test_auth_endpoints.py"

if [ ! -f "$TEST_FILE" ]; then
    echo "❌ Error: $TEST_FILE not found!"
    echo "   Are you in the project root directory?"
    exit 1
fi

# Fix broken dictionary entries where `: user` was incorrectly removed
sed -i 's/"email"\.email,/"email": user.email,/g' "$TEST_FILE"
sed -i 's/"password"\.password,/"password": user.password,/g' "$TEST_FILE"

echo "✅ Syntax errors fixed!"
echo ""
echo "💡 Next steps:"
echo "   1. Verify the fix: cd src/backend && pytest --co -q"
echo "   2. Run tests: pytest -v"
