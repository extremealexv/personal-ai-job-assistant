# VPS Test Fix Execution Guide

## Quick Start

Run these commands on your VPS to fix the pytest issues:

```bash
# 1. Navigate to project directory
cd ~/personal-ai-job-assistant

# 2. Pull latest changes
git pull

# 3. Activate virtual environment
source venv/bin/activate  # or: . venv/bin/activate

# 4. Run the fix script
python3 scripts/fix_async_fixtures.py

# 5. Run tests to verify
cd src/backend
pytest --co -q  # Verify test collection works

# 6. Run full test suite
pytest -v
```

## Expected Output

After running `fix_async_fixtures.py`, you should see:

```
✅ Removed type hints from src/backend/tests/test_auth_endpoints.py
✅ Removed type hints from src/backend/tests/integration/test_analytics_api.py
✅ Removed type hints from src/backend/tests/integration/test_search_api.py
...

📊 Summary: Modified X file(s)
```

## What Gets Fixed

The script removes type hints from async fixture parameters:

**Before:**
```python
async def test_login(self, async_client: AsyncClient, test_user: User):
```

**After:**
```python
async def test_login(self, async_client, test_user):
```

This fixes errors like:
- ❌ `RuntimeWarning: coroutine 'test_user' was never awaited`
- ❌ `AttributeError: 'coroutine' object has no attribute 'email'`
- ❌ `fixture 'sample_user' not found`

## Verification

After running fixes, check test results:

```bash
cd ~/personal-ai-job-assistant/src/backend

# Quick check - should show 328 tests collected
pytest --co -q

# Run specific test file
pytest tests/unit/test_search_service.py -v

# Run all tests with output
pytest -v --tb=short

# Run with coverage
pytest --cov=app/services --cov=app/api/v1/endpoints
```

## Expected Test Results

After fixes, you should see:
- ✅ All 328 tests collected successfully
- ✅ No "fixture not found" errors
- ✅ No "coroutine was never awaited" warnings
- ✅ Tests pass or fail based on actual logic (not fixture issues)

## Troubleshooting

### If tests still fail:

1. **Check fixture definitions exist:**
   ```bash
   grep -n "def test_user" src/backend/tests/conftest.py
   grep -n "def other_user_job" src/backend/tests/conftest.py
   grep -n "def other_user_application" src/backend/tests/conftest.py
   ```
   All should show `async def` definitions.

2. **Check database is initialized:**
   ```bash
   cd src/backend
   python database/init_db.py --drop --seed
   ```

3. **Re-run migrations:**
   ```bash
   cd src/backend
   alembic upgrade head
   ```

4. **Check environment variables:**
   ```bash
   cat .env | grep DATABASE
   ```
   Should show `DATABASE_URL` and `DATABASE_ASYNC_URL`.

## Common Issues

### Issue: Script says "No changes needed"
**Meaning:** Type hints were already removed (changes already applied locally)
**Action:** Just run pytest to verify everything works

### Issue: "ModuleNotFoundError"
**Cause:** Not in virtual environment
**Fix:** Run `source venv/bin/activate` first

### Issue: Tests still show "coroutine" errors
**Cause:** May need to remove `__pycache__` directories
**Fix:**
```bash
find src/backend/tests -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
pytest --cache-clear
```

## Success Indicators

✅ No warnings about coroutines not awaited
✅ Test collection completes (328 tests found)
✅ Tests run without fixture errors
✅ Only legitimate test failures remain (if any)

## Contact

If issues persist after running these fixes, capture the output:
```bash
pytest -v > test_results.log 2>&1
```

Then share the `test_results.log` file for further diagnosis.
