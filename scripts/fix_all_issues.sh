#!/bin/bash
# Auto-fix all code formatting and linting issues

echo "Auto-fixing Backend Code"
echo "=================================================="

cd src/backend

echo "Running Black formatter..."
poetry run black app/ database/ scripts/
echo ""

echo "Running Ruff auto-fix..."
poetry run ruff check app/ database/ scripts/ --fix
echo ""

cd ../..

echo ""
echo "=================================================="
echo "✓ Auto-fixes complete!"
echo "=================================================="
echo ""
echo "Remaining issues to fix manually:"
echo "  - mypy type errors in app/config.py"
echo "  - Markdown linting (optional, can be fixed later)"
echo ""
echo "Next steps:"
echo "  1. Review changes: git diff"
echo "  2. Commit: git add . && git commit -m 'style: auto-fix formatting and linting issues'"
echo ""
