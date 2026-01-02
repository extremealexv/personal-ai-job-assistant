#!/usr/bin/env python3
"""Remove type hints from async fixtures in test files."""
import re
import sys

def remove_fixture_type_hints(filepath):
    """Remove type hints for async fixtures in pytest test files."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove type hints for common async fixtures
    patterns = [
        (r': AsyncClient', ''),
        (r': AsyncSession', ''),
        (r': User', ''),
        (r': dict\[str,\s*str\]', ''),
        (r': dict', ''),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Removed type hints from {filepath}")

if __name__ == '__main__':
    filepath = 'src/backend/tests/test_auth_endpoints.py'
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    
    remove_fixture_type_hints(filepath)
