#!/bin/bash
# Apply Alembic migrations

set -e

cd "$(dirname "$0")/.."

echo "🔄 Applying database migrations..."

# Show current revision
echo "Current revision:"
poetry run alembic current

echo ""
echo "Upgrading to head..."

# Apply all pending migrations
poetry run alembic upgrade head

echo ""
echo "✅ Migrations applied successfully"
echo ""
echo "Current revision:"
poetry run alembic current
