#!/bin/bash
# Grant permissions on existing test database
# Run this if you get "permission denied for schema public" errors

set -e

# Get database name from environment or use default
DB_NAME="${DATABASE_NAME:-ai_job_assistant}"
TEST_DB_NAME="${DB_NAME}_test"
DB_USER="${DATABASE_USER:-jsappuser}"

echo "🔑 Granting permissions on test database..."
echo "📦 Database: $TEST_DB_NAME"
echo "👤 User: $DB_USER"

# Grant database privileges
echo ""
echo "🔑 Granting database privileges..."
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE \"$TEST_DB_NAME\" TO $DB_USER;"

# Grant schema privileges
echo "🔑 Granting schema privileges..."
sudo -u postgres psql -d "$TEST_DB_NAME" -c "GRANT ALL ON SCHEMA public TO $DB_USER;"
sudo -u postgres psql -d "$TEST_DB_NAME" -c "GRANT CREATE ON SCHEMA public TO $DB_USER;"

# Grant usage on all sequences (for auto-increment columns)
echo "🔑 Granting sequence privileges..."
sudo -u postgres psql -d "$TEST_DB_NAME" -c "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;"

# Set default privileges for future objects
echo "🔑 Setting default privileges..."
sudo -u postgres psql -d "$TEST_DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;"
sudo -u postgres psql -d "$TEST_DB_NAME" -c "ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;"

echo ""
echo "✅ Permissions granted successfully!"
echo ""
echo "Now run: pytest"
