#!/usr/bin/env python3
"""
Fix pytest-asyncio fixture issues by removing type hints from async fixtures.

This script removes type hints from test method parameters that use async fixtures,
which can cause pytest-asyncio to not properly await the fixtures.

Usage:
    python scripts/fix_async_fixtures.py
"""
import re
import sys
from pathlib import Path


def remove_fixture_type_hints(filepath: Path) -> bool:
    """
    Remove type hints for async fixtures in pytest test files.
    
    Args:
        filepath: Path to the test file
        
    Returns:
        True if file was modified, False otherwise
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        content = original_content
        
        # Remove type hints for common async fixtures
        # Pattern: parameter_name: TypeHint -> parameter_name
        patterns = [
            (r': AsyncClient', ''),
            (r': AsyncSession', ''),
            (r': User(?!\w)', ''),  # Negative lookahead to avoid matching 'UserCreate', etc.
            (r': dict\[str,\s*str\]', ''),
            (r': dict(?!\[)', ''),  # dict without generic parameter
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)
        
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Removed type hints from {filepath}")
            return True
        else:
            print(f"ℹ️  No changes needed in {filepath}")
            return False
            
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}", file=sys.stderr)
        return False


def main():
    """Main function to fix async fixtures in test files."""
    # Find all test files that might have async fixture issues
    test_files = [
        Path("src/backend/tests/test_auth_endpoints.py"),
        Path("src/backend/tests/test_auth_security.py"),
        Path("src/backend/tests/integration/test_analytics_api.py"),
        Path("src/backend/tests/integration/test_search_api.py"),
        Path("src/backend/tests/integration/test_jobs_api.py"),
        Path("src/backend/tests/integration/test_applications_api.py"),
        Path("src/backend/tests/integration/test_cover_letters_api.py"),
    ]
    
    modified_count = 0
    for test_file in test_files:
        if test_file.exists():
            if remove_fixture_type_hints(test_file):
                modified_count += 1
        else:
            print(f"⚠️  File not found: {test_file}")
    
    print(f"\n📊 Summary: Modified {modified_count} file(s)")
    
    if modified_count > 0:
        print("\n💡 Next steps:")
        print("   1. Review changes: git diff")
        print("   2. Stage changes: git add src/backend/tests/")
        print("   3. Commit: git commit -m 'fix: remove type hints from async fixtures'")
        print("   4. Push: git push")
    
    return 0 if modified_count > 0 else 1


if __name__ == '__main__':
    sys.exit(main())
