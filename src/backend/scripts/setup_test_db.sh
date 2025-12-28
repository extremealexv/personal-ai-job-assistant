#!/bin/bash
# Setup test database script
# Run this before executing pytest for the first time

set -e  # Exit on error

echo "🔧 Setting up test database..."

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to backend directory
cd "$BACKEND_DIR"

# Check if --drop flag is provided
DROP_FLAG=""
if [ "$1" = "--drop" ]; then
    DROP_FLAG="--drop"
    echo "⚠️  Will drop existing test database"
fi

# Run setup script
python scripts/setup_test_db.py $DROP_FLAG

echo ""
echo "✅ Setup complete! You can now run: pytest"
