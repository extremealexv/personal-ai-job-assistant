#!/usr/bin/env python3
"""Show exact lines and their fixes for manual editing."""

from pathlib import Path


def show_file_lines(filepath, line_numbers):
    """Show specific lines from a file."""
    path = Path(filepath)
    if not path.exists():
        print(f"File not found: {filepath}")
        return
    
    lines = path.read_text().splitlines()
    print(f"\n{filepath}")
    print("=" * 80)
    for line_num in line_numbers:
        if line_num <= len(lines):
            print(f"Line {line_num}: {lines[line_num-1]}")
    print()


print("Current problematic lines:")
print("=" * 80)

show_file_lines("src/backend/app/config.py", [56, 75, 76])
show_file_lines("src/backend/database/init_db.py", [189])
show_file_lines("src/backend/scripts/test_config.py", [62, 66, 79, 142])

print("\n" + "=" * 80)
print("MANUAL FIXES NEEDED:")
print("=" * 80)

print("""
Open each file and make these changes:

1. src/backend/app/config.py line 56:
   Change the long Field() call to multi-line format

2. src/backend/app/config.py lines 75-76:
   Change the long Field() calls to multi-line format

3. src/backend/database/init_db.py line 189:
   Split the long print statement across multiple lines

4. src/backend/scripts/test_config.py line 62:
   Change 'for example in examples:' to 'for _ in examples:'

5. src/backend/scripts/test_config.py line 66:
   Change '{example['name']}' to '{_['name']}'

6. src/backend/scripts/test_config.py line 79:
   Split the long database_async_url line

7. src/backend/scripts/test_config.py line 142:
   Split the long print statement

Use nano or vim to edit these files directly.
""")
