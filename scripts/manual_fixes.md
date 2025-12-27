# Manual Fixes for Remaining Ruff Errors

Since the automated script couldn't match the Black-formatted code, here are the exact manual fixes needed:

## 1. Fix `src/backend/database/init_db.py` line 192

**Find this line (around line 192):**
```python
                f"  Password: {example['password']} (Use this to login)"
```

**Replace with:**
```python
                f"  Password: {example['password']} "
                f"(Use this to login)"
```

## 2. Fix `src/backend/scripts/test_config.py` line 63

**Find this (around line 63):**
```python
    for example in examples:
        print(f"   - {example['name']}")
```

**Replace with:**
```python
    for _ in examples:
        print(f"   - {_['name']}")
```

## 3. Fix `src/backend/scripts/test_config.py` line 84

**Find this (around line 84):**
```python
            database_async_url="postgresql+asyncpg://user:pass@localhost:5432/testdb",
```

**Replace with:**
```python
            database_async_url=(
                "postgresql+asyncpg://user:pass@localhost:5432/testdb"
            ),
```

## 4. Fix `src/backend/scripts/test_config.py` line 149

**Find this (around line 149):**
```python
        print(f"   Upload directory: {settings.upload_dir} (type: {type(settings.upload_dir).__name__})")
```

**Replace with:**
```python
        print(
            f"   Upload directory: {settings.upload_dir} "
            f"(type: {type(settings.upload_dir).__name__})"
        )
```

---

## Commands to apply fixes:

### Quick vim commands (for each file):

```bash
# 1. Fix init_db.py
vim +192 src/backend/database/init_db.py
# Press 'dd' to delete line 192
# Press 'O' to insert above, then paste:
#                 f"  Password: {example['password']} "
# Press Enter, then paste:
#                 f"(Use this to login)"
# Press Esc, then :wq

# 2. Fix test_config.py line 63
vim +63 src/backend/scripts/test_config.py
# Change 'example' to '_' on both lines 63 and 64
# :%s/for example in examples:/for _ in examples:/
# :%s/{example\['name'\]}/{_['name']}/
# :wq

# 3. Fix test_config.py line 84
vim +84 src/backend/scripts/test_config.py
# Replace line 84 with the multi-line version shown above
# :wq

# 4. Fix test_config.py line 149
vim +149 src/backend/scripts/test_config.py
# Replace line 149 with the multi-line version shown above
# :wq
```

### Or use sed (safer):

```bash
cd ~/personal-ai-job-assistant

# Create backup
cp src/backend/database/init_db.py src/backend/database/init_db.py.bak
cp src/backend/scripts/test_config.py src/backend/scripts/test_config.py.bak

# Apply fixes with sed - run each one separately and verify
```

Actually, the easiest way is to just edit these 3 files manually in nano or vim following the patterns above.
