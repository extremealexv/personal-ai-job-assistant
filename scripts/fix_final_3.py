#!/usr/bin/env python3
"""Fix the final 3 ruff errors."""

from pathlib import Path


def fix_final_3():
    """Fix the last 3 errors."""
    
    # Fix test_config.py line 149 - f-string syntax error
    print("Fixing scripts/test_config.py line 149...")
    test = Path("src/backend/scripts/test_config.py")
    content = test.read_text()
    
    # The f-string was split incorrectly - fix it
    content = content.replace(
        '        print(\n'
        '            f"   Database: {settings.database_url.split(\'@\')[1] "\n'
        '            f"if \'@\' in settings.database_url else \'configured\'}"\n'
        '        )',
        '        db_display = (\n'
        '            settings.database_url.split(\'@\')[1]\n'
        '            if \'@\' in settings.database_url\n'
        '            else \'configured\'\n'
        '        )\n'
        '        print(f"   Database: {db_display}")'
    )
    
    test.write_text(content)
    print("  ✓ Fixed test_config.py")
    
    # Fix config.py lines 74-75
    print("Fixing app/config.py lines 74-75...")
    config = Path("src/backend/app/config.py")
    content = config.read_text()
    
    # Line 74: gmail_client_secret
    content = content.replace(
        '    gmail_client_secret: Optional[str] = Field(default=None, description="Gmail OAuth client secret")',
        '    gmail_client_secret: Optional[str] = Field(\n'
        '        default=None, description="Gmail OAuth client secret"\n'
        '    )'
    )
    
    # Line 75: google_calendar_client_id  
    content = content.replace(
        '    google_calendar_client_id: Optional[str] = Field(default=None, description="Google Calendar OAuth client ID")',
        '    google_calendar_client_id: Optional[str] = Field(\n'
        '        default=None, description="Google Calendar OAuth client ID"\n'
        '    )'
    )
    
    config.write_text(content)
    print("  ✓ Fixed config.py")
    
    print("\n" + "=" * 50)
    print("✓ All 3 errors fixed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        fix_final_3()
        print("\nVerify with:")
        print("  cd src/backend && poetry run ruff check .")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
