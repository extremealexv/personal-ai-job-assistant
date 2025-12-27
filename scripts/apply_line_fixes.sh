#!/bin/bash
# Direct line-by-line fixes using sed

cd ~/personal-ai-job-assistant/src/backend

echo "Fixing config.py..."
# These need to be done character-by-character to match exactly
# We'll use a Python one-liner instead

python3 << 'EOF'
from pathlib import Path

# Fix config.py
config = Path("app/config.py")
lines = config.read_text().split('\n')

# Line 56 - find gmail_client_id line
for i, line in enumerate(lines):
    if 'gmail_client_id' in line and 'Optional[str]' in line and 'Field' in line:
        if 'default=None' in line and len(line) > 100:
            lines[i] = '    gmail_client_id: Optional[str] = Field('
            lines.insert(i+1, '        default=None, description="Gmail OAuth client ID"')
            lines.insert(i+2, '    )')
            print(f"✓ Fixed config.py line {i+1}")
            break

# Line 75-76 - find secret_key line
for i, line in enumerate(lines):
    if 'secret_key: str = Field' in line and len(line) > 100:
        lines[i] = '    secret_key: str = Field('
        lines.insert(i+1, '        ..., description="Secret key for session management and JWT"')
        lines.insert(i+2, '    )')
        print(f"✓ Fixed config.py line {i+1}")
        break

config.write_text('\n'.join(lines))

# Fix init_db.py
initdb = Path("database/init_db.py")
lines = initdb.read_text().split('\n')

for i, line in enumerate(lines):
    if 'User created with hashed password' in line and len(line) > 100:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'print('
        lines.insert(i+1, ' ' * (indent+4) + 'f"✓ User created with hashed password: "')
        lines.insert(i+2, ' ' * (indent+4) + 'f"{example[\'email\']}"')
        lines.insert(i+3, ' ' * indent + ')')
        print(f"✓ Fixed init_db.py line {i+1}")
        break

initdb.write_text('\n'.join(lines))

# Fix test_config.py
test = Path("scripts/test_config.py")
lines = test.read_text().split('\n')

# Fix loop variable
for i, line in enumerate(lines):
    if 'for example in examples:' in line:
        lines[i] = line.replace('for example in examples:', 'for _ in examples:')
        print(f"✓ Fixed test_config.py line {i+1} (loop variable)")
        # Also fix the next line that uses it
        if i+1 < len(lines) and 'example[' in lines[i+1]:
            lines[i+1] = lines[i+1].replace("example['name']", "_['name']")
            print(f"✓ Fixed test_config.py line {i+2} (variable usage)")
        break

# Fix database_async_url
for i, line in enumerate(lines):
    if 'database_async_url="postgresql+asyncpg' in line and len(line) > 100:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'database_async_url=('
        lines.insert(i+1, ' ' * (indent+4) + '"postgresql+asyncpg://user:pass@localhost:5432/testdb"')
        lines.insert(i+2, ' ' * indent + '),')
        print(f"✓ Fixed test_config.py line {i+1} (database_async_url)")
        break

# Fix upload_dir print
for i, line in enumerate(lines):
    if 'Upload directory:' in line and '(type:' in line and len(line) > 100:
        indent = len(line) - len(line.lstrip())
        lines[i] = ' ' * indent + 'print('
        lines.insert(i+1, ' ' * (indent+4) + 'f"   Upload directory: {settings.upload_dir} "')
        lines.insert(i+2, ' ' * (indent+4) + 'f"(type: {type(settings.upload_dir).__name__})"')
        lines.insert(i+3, ' ' * indent + ')')
        print(f"✓ Fixed test_config.py line {i+1} (upload_dir)")
        break

test.write_text('\n'.join(lines))

print("\n" + "="*50)
print("✓ All fixes applied!")
print("="*50)
EOF

echo ""
echo "Verifying fixes..."
poetry run ruff check .
