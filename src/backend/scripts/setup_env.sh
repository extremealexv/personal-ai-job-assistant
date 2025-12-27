#!/bin/bash
# Setup script for environment configuration
# Run this after cloning the repository
# Usage: cd src/backend && bash scripts/setup_env.sh

set -e  # Exit on error

echo "================================================"
echo "Personal AI Job Assistant - Environment Setup"
echo "================================================"
echo

# Navigate to project root (2 levels up from scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
ENV_PATH="$PROJECT_ROOT/.env"
ENV_EXAMPLE_PATH="$PROJECT_ROOT/.env.example"

echo "📍 Project root: $PROJECT_ROOT"
echo "📍 .env location: $ENV_PATH"
echo

# Check if .env.example exists
if [ ! -f "$ENV_EXAMPLE_PATH" ]; then
    echo "❌ .env.example not found at: $ENV_EXAMPLE_PATH"
    echo "   Make sure you're running this from src/backend directory"
    exit 1
fi

# Check if .env already exists
if [ -f "$ENV_PATH" ]; then
    echo "⚠️  .env file already exists at:"
    echo "   $ENV_PATH"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Copy template
echo "📝 Creating .env file from template..."
cp "$ENV_EXAMPLE_PATH" "$ENV_PATH"

# Generate SECRET_KEY
echo "🔐 Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/generate-with-python-secrets-token-urlsafe-32/$SECRET_KEY/" ../../.env

# Generate ENCRYPTION_KEY
echo "🔐 Generating ENCRYPTION_KEY..."
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
sed -i "s/generate-with-fernet-generate-key/$ENCRYPTION_KEY/" "$ENV_PATH"

echo
echo "✅ Environment file created successfully!"
echo
echo "📍 Location: $ENV_PATH"
echo
echo "⚠️  IMPORTANT: You still need to configure:"
echo "   1. Database credentials (DATABASE_URL)"
echo "   2. OpenAI API key (OPENAI_API_KEY)"
echo "   3. Gmail/Calendar OAuth credentials (optional)"
echo
echo "Edit .env file to add your credentials:"
echo "   nano $ENV_PATH"
echo
echo "Then test your configuration:"
echo "   cd src/backend"
echo "   python scripts/test_config.py"
