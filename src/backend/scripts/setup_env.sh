#!/bin/bash
# Setup script for environment configuration
# Run this after cloning the repository

set -e  # Exit on error

echo "================================================"
echo "Personal AI Job Assistant - Environment Setup"
echo "================================================"
echo

# Check if .env already exists
if [ -f "../../.env" ]; then
    echo "⚠️  .env file already exists"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing .env file"
        exit 0
    fi
fi

# Copy template
echo "📝 Creating .env file from template..."
cp ../../.env.example ../../.env

# Generate SECRET_KEY
echo "🔐 Generating SECRET_KEY..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
sed -i "s/generate-with-python-secrets-token-urlsafe-32/$SECRET_KEY/" ../../.env

# Generate ENCRYPTION_KEY
echo "🔐 Generating ENCRYPTION_KEY..."
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
sed -i "s/generate-with-fernet-generate-key/$ENCRYPTION_KEY/" ../../.env

echo
echo "✅ Environment file created successfully!"
echo
echo "⚠️  IMPORTANT: You still need to configure:"
echo "   1. Database credentials (DATABASE_URL)"
echo "   2. OpenAI API key (OPENAI_API_KEY)"
echo "   3. Gmail/Calendar OAuth credentials (optional)"
echo
echo "Edit .env file to add your credentials:"
echo "   nano ../../.env"
echo
echo "Then test your configuration:"
echo "   python scripts/test_config.py"
