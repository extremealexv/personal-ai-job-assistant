#!/usr/bin/env python3
"""
Test script to verify environment configuration is correct.

Usage:
    python scripts/test_config.py
"""
import sys
from pathlib import Path

# Add parent directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_env_file():
    """Check if .env file exists."""
    env_file = Path(__file__).parent.parent.parent / ".env"
    if not env_file.exists():
        print("❌ .env file not found!")
        print(f"   Expected location: {env_file}")
        print("   Run: cp .env.example .env")
        return False
    print("✅ .env file exists")
    return True


def test_config_loading():
    """Test if configuration can be loaded."""
    try:
        from app.config import settings
        print("✅ Configuration loaded successfully")
        return True, settings
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        return False, None


def test_required_variables(settings):
    """Check if all required variables are set."""
    required = [
        "database_url",
        "database_async_url",
        "secret_key",
        "encryption_key",
        "openai_api_key",
    ]
    
    missing = []
    for var in required:
        value = getattr(settings, var, None)
        if not value or "your-" in value or "generate-" in value:
            missing.append(var.upper())
    
    if missing:
        print(f"❌ Missing or placeholder values: {', '.join(missing)}")
        print("\nGenerate keys with:")
        print('  python -c "import secrets; print(secrets.token_urlsafe(32))"')
        print('  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"')
        return False
    
    print("✅ All required variables are set")
    return True


def test_gitignore():
    """Check if .env is in .gitignore."""
    gitignore = Path(__file__).parent.parent.parent / ".gitignore"
    if not gitignore.exists():
        print("⚠️  .gitignore not found")
        return False
    
    content = gitignore.read_text()
    if ".env" in content:
        print("✅ .env is in .gitignore")
        return True
    else:
        print("❌ .env not found in .gitignore!")
        print("   Run: echo '.env' >> .gitignore")
        return False


def test_database_connection():
    """Test database connection."""
    import asyncio
    from database.init_db import check_connection
    
    print("\n🔍 Testing database connection...")
    result = asyncio.run(check_connection())
    return result


def main():
    """Run all configuration tests."""
    print("=" * 60)
    print("Personal AI Job Assistant - Configuration Test")
    print("=" * 60)
    print()
    
    results = []
    
    # Test .env file
    results.append(test_env_file())
    print()
    
    # Test config loading
    loaded, settings = test_config_loading()
    results.append(loaded)
    print()
    
    if loaded:
        # Test required variables
        results.append(test_required_variables(settings))
        print()
        
        # Print config summary
        print("📋 Configuration Summary:")
        print(f"   Environment: {settings.app_env}")
        print(f"   Debug: {settings.debug}")
        print(f"   Database: {settings.database_url.split('@')[1] if '@' in settings.database_url else 'configured'}")
        print(f"   Redis: {settings.redis_url}")
        print(f"   AI Model: {settings.openai_model}")
        print(f"   Upload Dir: {settings.upload_dir}")
        print()
    
    # Test .gitignore
    results.append(test_gitignore())
    print()
    
    # Test database connection (optional, requires DB to be running)
    try:
        results.append(test_database_connection())
    except Exception as e:
        print(f"⚠️  Could not test database connection: {e}")
        print("   Make sure PostgreSQL is running")
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! Configuration is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
