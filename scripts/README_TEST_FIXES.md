# Test Fix Scripts

## Overview

These scripts fix pytest-asyncio fixture issues that cause test failures with async/await patterns.

## Problem

pytest-asyncio v0.21.2+ strictly enforces async patterns. When test methods have type hints on async fixture parameters, pytest doesn't properly await the fixtures, causing errors like:

```
AttributeError: 'coroutine' object has no attribute 'email'
RuntimeWarning: coroutine 'test_user' was never awaited
```

## Solution

Remove type hints from async fixture parameters in test methods. This allows pytest-asyncio to properly detect and await async fixtures.

## Scripts

### 1. `fix_async_fixtures.py`

Automatically removes type hints from async fixtures across all test files.

**Usage:**
```bash
cd ~/personal-ai-job-assistant
python3 scripts/fix_async_fixtures.py
```

**What it does:**
- Removes `: AsyncClient`, `: AsyncSession`, `: User`, `: dict` type hints
- Processes test_auth_endpoints.py and other integration test files
- Shows summary of files modified

**Example transformation:**
```python
# Before
async def test_login(self, async_client: AsyncClient, test_user: User):
    ...

# After
async def test_login(self, async_client, test_user):
    ...
```

### 2. `run_test_fixes.sh`

Convenience script that runs all test fixes in sequence.

**Usage:**
```bash
cd ~/personal-ai-job-assistant
bash scripts/run_test_fixes.sh
```

## Manual Steps (if scripts fail)

If the scripts don't work for any reason, you can manually fix the issues:

1. **Fix test_search_service.py**: Replace `sample_user` with `test_user`
   ```bash
   sed -i 's/sample_user/test_user/g' src/backend/tests/unit/test_search_service.py
   ```

2. **Remove type hints from test_auth_endpoints.py**:
   ```bash
   sed -i 's/: AsyncClient//g' src/backend/tests/test_auth_endpoints.py
   sed -i 's/: AsyncSession//g' src/backend/tests/test_auth_endpoints.py
   sed -i 's/: User//g' src/backend/tests/test_auth_endpoints.py
   ```

3. **Verify fixtures exist in conftest.py**:
   - Ensure `test_user` fixture exists (not `sample_user`)
   - Ensure `other_user_job` and `other_user_application` fixtures exist
   - Ensure `auth_headers` is async fixture

## Verification

After running the fixes:

```bash
cd ~/personal-ai-job-assistant/src/backend
pytest --co -q  # Verify test collection
pytest tests/unit/test_search_service.py -v  # Run specific test
pytest  # Run all tests
```

Expected results:
- No "fixture 'sample_user' not found" errors
- No "coroutine was never awaited" warnings
- Tests should pass or fail based on actual test logic, not fixture issues

## Files Modified

The scripts modify:
- `src/backend/tests/test_auth_endpoints.py`
- `src/backend/tests/integration/test_analytics_api.py`
- `src/backend/tests/integration/test_search_api.py`
- `src/backend/tests/integration/test_jobs_api.py`
- `src/backend/tests/unit/test_search_service.py` (already fixed locally)

## Troubleshooting

### Issue: "coroutine was never awaited"
**Cause:** Test method is not async or fixture is not async
**Fix:** Ensure both test method and fixture use `async def`

### Issue: "AttributeError: 'async_generator' object has no attribute 'post'"
**Cause:** Fixture is async but test method has type hint
**Fix:** Remove type hint from the parameter

### Issue: "fixture 'sample_user' not found"
**Cause:** Test uses wrong fixture name
**Fix:** Replace `sample_user` with `test_user` throughout test file

## Related Documentation

- [pytest-asyncio documentation](https://pytest-asyncio.readthedocs.io/)
- [Project Copilot Instructions](../.github/copilot-instructions.md)
- [Test Fixture Patterns](../docs/architecture/TESTING_STRATEGY.md)
