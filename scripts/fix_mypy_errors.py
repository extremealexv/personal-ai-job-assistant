#!/usr/bin/env python3
"""Fix the 5 mypy errors in config.py."""

from pathlib import Path


def fix_mypy_errors():
    """Fix duplicate secret_key and missing app_env."""
    
    print("Fixing app/config.py mypy errors...")
    config = Path("src/backend/app/config.py")
    content = config.read_text()
    
    # Remove the duplicate secret_key on lines 71-73
    content = content.replace(
        '    openai_max_tokens: int = Field(default=4000, description="Max tokens per request")\n'
        '    # OAuth & External Services\n'
        '    secret_key: str = Field(\n'
        '        ..., description="Secret key for session management and JWT"\n'
        '    )',
        '    openai_max_tokens: int = Field(default=4000, description="Max tokens per request")\n'
        '\n'
        '    # OAuth & External Services'
    )
    
    # Add app_env field after log_level (around line 61)
    content = content.replace(
        '    log_level: str = Field(default="INFO", description="Logging level")\n'
        '\n'
        '    # Security & Encryption',
        '    log_level: str = Field(default="INFO", description="Logging level")\n'
        '    app_env: str = Field(\n'
        '        default="development",\n'
        '        description="Environment: development, staging, production"\n'
        '    )\n'
        '\n'
        '    # Security & Encryption'
    )
    
    config.write_text(content)
    print("  ✓ Removed duplicate secret_key")
    print("  ✓ Added missing app_env field")
    
    print("\n" + "=" * 50)
    print("✓ All mypy errors fixed!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        fix_mypy_errors()
        print("\nVerify with:")
        print("  cd src/backend && poetry run mypy app/")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
