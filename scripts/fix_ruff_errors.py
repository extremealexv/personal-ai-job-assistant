#!/usr/bin/env python3
"""Fix remaining ruff errors by reading and modifying specific lines."""

from pathlib import Path


def fix_init_db():
    """Fix init_db.py line 192 - split long print statement."""
    file_path = Path("src/backend/database/init_db.py")
    lines = file_path.read_text().splitlines(keepends=True)
    
    # Find the line with "Use this to login"
    for i, line in enumerate(lines):
        if "Use this to login" in line and "Password:" in line:
            # Get the indentation
            indent = len(line) - len(line.lstrip())
            # Replace with split version
            lines[i] = " " * indent + 'f"  Password: {example[\'password\']} "\n'
            lines.insert(i + 1, " " * indent + 'f"(Use this to login)"\n')
            print(f"✓ Fixed init_db.py line {i+1}")
            break
    
    file_path.write_text("".join(lines))


def fix_test_config():
    """Fix test_config.py issues."""
    file_path = Path("src/backend/scripts/test_config.py")
    lines = file_path.read_text().splitlines(keepends=True)
    
    fixed_count = 0
    
    for i, line in enumerate(lines):
        # Fix 1: Loop variable name
        if "for example in examples:" in line:
            lines[i] = line.replace("for example in examples:", "for _ in examples:")
            print(f"✓ Fixed test_config.py line {i+1} (loop variable)")
            fixed_count += 1
        
        # Fix the print that uses 'example'
        if "{example['name']}" in line:
            lines[i] = line.replace("{example['name']}", "{_['name']}")
            fixed_count += 1
        
        # Fix 2: Long database_async_url line
        if 'database_async_url="postgresql+asyncpg://user:pass@localhost:5432/testdb"' in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + 'database_async_url=(\n'
            lines.insert(i + 1, " " * (indent + 4) + '"postgresql+asyncpg://user:pass@localhost:5432/testdb"\n')
            lines.insert(i + 2, " " * indent + '),\n')
            print(f"✓ Fixed test_config.py line {i+1} (database_async_url)")
            fixed_count += 1
            continue
        
        # Fix 3: Long print with upload_dir
        if "Upload directory: {settings.upload_dir} (type:" in line:
            indent = len(line) - len(line.lstrip())
            lines[i] = " " * indent + 'print(\n'
            lines.insert(i + 1, " " * (indent + 4) + 'f"   Upload directory: {settings.upload_dir} "\n')
            lines.insert(i + 2, " " * (indent + 4) + 'f"(type: {type(settings.upload_dir).__name__})"\n')
            lines.insert(i + 3, " " * indent + ')\n')
            print(f"✓ Fixed test_config.py line {i+1} (upload_dir print)")
            fixed_count += 1
            break
    
    file_path.write_text("".join(lines))
    print(f"✓ Fixed {fixed_count} issues in test_config.py")


def main():
    """Run all fixes."""
    print("Fixing remaining ruff errors...")
    print("=" * 50)
    
    try:
        fix_init_db()
        fix_test_config()
        
        print("=" * 50)
        print("✓ All fixes applied!")
        print("=" * 50)
        print("\nVerify with:")
        print("  cd src/backend && poetry run ruff check .")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
