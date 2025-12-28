#!/bin/bash
# Create a new Alembic migration

set -e

if [ -z "$1" ]; then
    echo "Usage: ./scripts/create_migration.sh \"migration message\""
    echo "Example: ./scripts/create_migration.sh \"add user table\""
    exit 1
fi

MESSAGE="$1"

echo "📝 Creating new migration: $MESSAGE"

cd "$(dirname "$0")/.."

# Create migration with autogenerate
poetry run alembic revision --autogenerate -m "$MESSAGE"

echo "✅ Migration created successfully"
echo ""
echo "Next steps:"
echo "  1. Review the generated migration file in alembic/versions/"
echo "  2. Apply migration: ./scripts/run_migration.sh"
