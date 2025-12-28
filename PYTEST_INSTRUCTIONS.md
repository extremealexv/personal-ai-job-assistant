# Running Pytest Tests on VPS

## Prerequisites

The pytest tests are now in `src/backend/tests/` directory:
- `test_resume_phase1.py` - Master resume upload/get/delete (6 tests)
- `test_resume_phase2.py` - Structured data CRUD (8 tests)  
- `test_resume_phase3.py` - Resume version management (6 tests)
- `test_resume_phase4.py` - Advanced features: search/stats/duplicate (9 tests)

**Total: 29 unit tests covering all 33 resume management endpoints**

## Running Tests on VPS

### 1. Pull Latest Changes

```bash
cd ~/personal-ai-job-assistant
git pull origin feature/resume-management-54
```

### 2. Activate Poetry Environment

```bash
cd src/backend
poetry shell
```

### 3. Run All Resume Tests

```bash
# Run all resume tests with verbose output
poetry run pytest tests/test_resume_phase*.py -v

# Run with short traceback
poetry run pytest tests/test_resume_phase*.py -v --tb=short

# Run specific phase
poetry run pytest tests/test_resume_phase1.py -v
poetry run pytest tests/test_resume_phase2.py -v
poetry run pytest tests/test_resume_phase3.py -v
poetry run pytest tests/test_resume_phase4.py -v
```

### 4. Run with Coverage

```bash
# Generate coverage report for resume endpoints
poetry run pytest tests/test_resume_phase*.py --cov=app.api.v1.endpoints.resumes --cov-report=term-missing
```

### 5. Run All Backend Tests

```bash
# Run entire test suite
poetry run pytest tests/ -v

# Run with markers
poetry run pytest tests/ -v -m unit        # Unit tests only
poetry run pytest tests/ -v -m integration # Integration tests
```

## Expected Results

### Individual Phase Results

- **Phase 1**: 6/6 tests should pass (upload, get, delete)
- **Phase 2**: 8/8 tests should pass (work exp, education, skills, certs CRUD)
- **Phase 3**: 6/6 tests should pass (version CRUD)
- **Phase 4**: 9/9 tests should pass (search, stats, duplicate)

### Total Expected

```
29 tests collected
29 passed, 0 failed, 0 skipped
```

## Troubleshooting

### Test Database Issues

If you see database connection errors:

```bash
# Check test database exists
psql -U ai_job_user -d ai_job_assistant_test -c "SELECT version();"

# Create test database if missing
python scripts/setup_test_db.py

# Drop and recreate
python scripts/setup_test_db.py --drop
```

### Authentication Errors

If JWT token tests fail, ensure:
- `JWT_SECRET_KEY` is set in environment
- User model has correct password hashing

### File Upload Errors

If PDF upload tests fail:
- Check `UPLOAD_DIR` exists: `mkdir -p uploads/resumes`
- Verify permissions: `chmod 755 uploads/`

## Test Comparison

| Test Type | Location | Count | Purpose |
|-----------|----------|-------|---------|
| **Bash Integration** | `scripts/test_resume_phase*.sh` | 74 tests | End-to-end API validation on VPS |
| **Pytest Unit** | `src/backend/tests/test_resume_phase*.py` | 29 tests | Fast unit tests with test DB |

**Both test suites complement each other:**
- Bash tests prove functionality in production-like environment
- Pytest tests enable fast CI/CD, code coverage, and development workflow

## Next Steps After Tests Pass

1. ✅ Verify all 29 pytest tests pass on VPS
2. ⏭️ Update API documentation (OpenAPI/Swagger)
3. ⏭️ Update README with Issue #54 completion
4. ⏭️ Create Pull Request to merge `feature/resume-management-54` → `main`

## Notes

- Tests use **PostgreSQL test database** (`ai_job_assistant_test`)
- Each test runs in isolated transaction (rollback after test)
- `conftest.py` provides fixtures: `async_client`, `auth_headers`, `test_pdf_content`
- Tests use existing user authentication system
- Resume files use minimal valid PDF format (454 bytes)
