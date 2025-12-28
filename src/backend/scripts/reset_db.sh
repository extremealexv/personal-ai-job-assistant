#!/bin/bash
# Reset database - drop all tables and recreate with migrations

set -e

cd "$(dirname "$0")/.."

echo "⚠️  WARNING: This will drop all database tables!"
echo "Press Ctrl+C to cancel, or Enter to continue..."
read

echo "🗑️  Downgrading to base (dropping all tables)..."
poetry run alembic downgrade base

echo ""
echo "📝 Creating fresh migration..."
poetry run alembic revision --autogenerate -m "initial schema"

echo ""
echo "🔄 Applying migrations..."
poetry run alembic upgrade head

echo ""
echo "✅ Database reset complete"
