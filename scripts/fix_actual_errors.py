#!/usr/bin/env python3
"""Fix the 8 ruff errors based on actual line content."""

from pathlib import Path


def fix_actual_errors():
    """Fix based on what we actually found."""
    
    # Fix config.py - indentation issues on lines 56-57 and 71-73
    print("Fixing config.py indentation...")
    config = Path("src/backend/app/config.py")
    content = config.read_text()
    
    # Fix gmail_client_id - remove extra space in indentation
    content = content.replace(
        '    gmail_client_id: Optional[str] = Field(\n'
        '         default=None, description="Gmail OAuth client ID"\n'
        '     )',
        '    gmail_client_id: Optional[str] = Field(\n'
        '        default=None, description="Gmail OAuth client ID"\n'
        '    )'
    )
    
    # Fix secret_key - remove extra space in indentation
    content = content.replace(
        '    secret_key: str = Field(\n'
        '         ..., description="Secret key for session management and JWT"\n'
        '     )',
        '    secret_key: str = Field(\n'
        '        ..., description="Secret key for session management and JWT"\n'
        '    )'
    )
    
    config.write_text(content)
    print("  ✓ Fixed config.py")
    
    # Fix init_db.py line 189 - split long prompt string
    print("Fixing database/init_db.py...")
    initdb = Path("src/backend/database/init_db.py")
    content = initdb.read_text()
    
    content = content.replace(
        '                "prompt": """You are an expert resume writer specializing in backend engineering roles.',
        '                "prompt": """\n'
        'You are an expert resume writer specializing in backend engineering roles.'
    )
    
    initdb.write_text(content)
    print("  ✓ Fixed init_db.py line 189")
    
    # Fix test_config.py
    print("Fixing scripts/test_config.py...")
    test = Path("src/backend/scripts/test_config.py")
    content = test.read_text()
    
    # Line 62: Change 'example' to '_' in loop variable
    content = content.replace(
        '    for var, example in required.items():',
        '    for var, _ in required.items():'
    )
    
    # Line 66: Split long elif line
    content = content.replace(
        '        elif any(placeholder in str(value) for placeholder in ["your-", "generate-", "your_password", "your_key"]):',
        '        elif any(\n'
        '            placeholder in str(value)\n'
        '            for placeholder in ["your-", "generate-", "your_password", "your_key"]\n'
        '        ):'
    )
    
    # Line 79: Split long print line
    content = content.replace(
        '        print(\'     ENCRYPTION_KEY: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"\')',
        '        print(\n'
        '            \'     ENCRYPTION_KEY: python -c "from cryptography.fernet import Fernet; \'\n'
        '            \'print(Fernet.generate_key().decode())"\'\n'
        '        )'
    )
    
    # Line 142: Split long print line
    content = content.replace(
        '        print(f"   Database: {settings.database_url.split(\'@\')[1] if \'@\' in settings.database_url else \'configured\'}")',
        '        print(\n'
        '            f"   Database: {settings.database_url.split(\'@\')[1] "\n'
        '            f"if \'@\' in settings.database_url else \'configured\'}"\n'
        '        )'
    )
    
    test.write_text(content)
    print("  ✓ Fixed test_config.py (4 issues)")
    
    print("\n" + "=" * 50)
    print("✓ All fixes applied!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        fix_actual_errors()
        print("\nVerify with:")
        print("  cd src/backend && poetry run ruff check .")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
