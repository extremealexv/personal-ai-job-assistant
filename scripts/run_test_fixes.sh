#!/bin/bash
# Run all test fixes on the VPS
# This script applies all necessary fixes to get pytest passing

set -e  # Exit on error

echo "🔧 Applying test fixes..."
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# 1. Fix async fixture type hints
echo "📝 Step 1: Removing type hints from async fixtures..."
python3 scripts/fix_async_fixtures.py
echo ""

# 2. Check if there are any remaining issues
echo "📝 Step 2: Running pytest to check for remaining issues..."
cd src/backend
pytest --co -q 2>&1 | head -20
echo ""

echo "✅ Test fixes applied!"
echo ""
echo "💡 Next steps:"
echo "   1. Run tests: cd src/backend && pytest"
echo "   2. Check coverage: pytest --cov=app/services --cov=app/api/v1/endpoints"
echo "   3. If all pass, commit: git add -A && git commit -m 'fix: resolve pytest fixture issues'"
