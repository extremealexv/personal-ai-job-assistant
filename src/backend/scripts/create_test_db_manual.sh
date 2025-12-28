#!/bin/bash
# Manual test database creation script
# Use this if your database user doesn't have CREATE DATABASE privileges

set -e

echo "🔧 Creating test database manually with superuser access..."

# Get database name from environment or use default
DB_NAME="${DATABASE_NAME:-ai_job_assistant}"
TEST_DB_NAME="${DB_NAME}_test"
DB_USER="${DATABASE_USER:-jsappuser}"

echo "📦 Database: $TEST_DB_NAME"
echo "👤 Owner: $DB_USER"

# Check if database already exists
if sudo -u postgres psql -lqt | cut -d \| -f 1 | grep -qw "$TEST_DB_NAME"; then
    echo "⚠️  Database '$TEST_DB_NAME' already exists"
    read -p "Drop and recreate? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Dropping existing database..."
        sudo -u postgres psql -c "DROP DATABASE IF EXISTS \"$TEST_DB_NAME\";"
        echo "✅ Dropped database"
    else
        echo "ℹ️  Keeping existing database"
        exit 0
    fi
fi

# Create database
echo "📦 Creating database..."
sudo -u postgres psql -c "CREATE DATABASE \"$TEST_DB_NAME\" OWNER $DB_USER;"
echo "✅ Created database: $TEST_DB_NAME"

# Grant privileges
echo "🔑 Granting privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$TEST_DB_NAME\" TO $DB_USER;"
echo "✅ Granted privileges"

echo ""
echo "🎉 Test database created successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: python scripts/setup_test_db.py"
echo "     (This will create the tables)"
echo "  2. Run: pytest"
echo ""
