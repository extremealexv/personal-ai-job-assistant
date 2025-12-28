# Issue #26: Implement User Authentication with JWT Tokens

**Labels:** `enhancement`, `backend`, `security`, `authentication`  
**Milestone:** Phase 1 - Foundation  
**Priority:** High  
**Estimated Time:** 1-2 weeks

---

## 📋 Overview

Implement secure user authentication system with JWT (JSON Web Tokens) for the FastAPI backend. This will protect API endpoints and enable user-specific data isolation.

**Why This Matters:**
- Foundation for all user-specific features (resumes, jobs, applications)
- Security requirement for production deployment
- Required before frontend authentication UI can be built
- Enables proper data isolation per user (per FR-2)

---

## 🎯 Goals

1. **User Registration** - Allow new users to create accounts
2. **User Login** - Generate JWT access tokens for authenticated sessions
3. **Token Refresh** - Implement refresh token mechanism for extended sessions
4. **Password Security** - Hash passwords with bcrypt/argon2
5. **Endpoint Protection** - Secure all non-public endpoints with authentication
6. **User Profile** - Allow users to view/update their profile

---

## 🔧 Technical Requirements

### Authentication Strategy
- **Method:** JWT (JSON Web Tokens)
- **Library:** `python-jose[cryptography]` + `passlib[bcrypt]`
- **Token Type:** Bearer tokens in Authorization header
- **Token Storage:** Access tokens (short-lived, 30 min), Refresh tokens (long-lived, 7 days)
- **Password Hashing:** bcrypt with salt rounds = 12

### Database Schema
Already implemented in `users` table (app/models/user.py):
- ✅ `id`, `email`, `password_hash`, `is_active`, `email_verified`
- ✅ `failed_login_attempts`, `locked_until` (for account lockout)
- ✅ `last_login` timestamp

### API Endpoints to Create

#### Public (No Auth Required)
- `POST /api/v1/auth/register` - Create new user account
- `POST /api/v1/auth/login` - Authenticate and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token using refresh token
- `POST /api/v1/auth/forgot-password` - Request password reset (future)

#### Protected (Auth Required)
- `GET /api/v1/auth/me` - Get current user profile
- `PATCH /api/v1/auth/me` - Update user profile
- `POST /api/v1/auth/logout` - Invalidate refresh token
- `POST /api/v1/auth/change-password` - Change password

---

## ✅ Implementation Tasks

### Task 1: Core Authentication Setup (2-3 days)

**Files to Create:**
- [ ] `app/core/security.py` - Password hashing, JWT creation/validation
- [ ] `app/core/deps.py` - FastAPI dependencies for auth (get_current_user, etc.)
- [ ] `app/schemas/auth.py` - Auth-related Pydantic schemas
- [ ] `app/api/v1/endpoints/auth.py` - Auth endpoints

**Key Functions:**
```python
# app/core/security.py
def verify_password(plain_password: str, hashed_password: str) -> bool
def get_password_hash(password: str) -> str
def create_access_token(data: dict, expires_delta: timedelta) -> str
def create_refresh_token(data: dict) -> str
def verify_token(token: str) -> dict | None
```

**Configuration (app/config.py):**
```python
SECRET_KEY: str  # For JWT signing (already in .env)
ALGORITHM: str = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7
```

### Task 2: Auth Endpoints (2-3 days)

**POST /api/v1/auth/register**
- Accept: `email`, `password`, `full_name`
- Validate: Email format, password strength (8+ chars, complexity)
- Check: Email uniqueness
- Create: User record with hashed password
- Return: User object (without password)

**POST /api/v1/auth/login**
- Accept: `email`, `password`
- Validate: Credentials
- Check: Account not locked, user is_active
- Update: `last_login` timestamp
- Return: `access_token`, `refresh_token`, `token_type`

**POST /api/v1/auth/refresh**
- Accept: `refresh_token` in request body
- Validate: Token signature and expiration
- Return: New `access_token`

**GET /api/v1/auth/me**
- Require: Valid access token
- Return: Current user profile

### Task 3: Protect Existing Endpoints (1 day)

**Update endpoints to require authentication:**
- Health endpoints: Leave public
- Future resume endpoints: Add `current_user: User = Depends(get_current_user)`
- Future job endpoints: Add auth dependency

**Example:**
```python
@router.get("/resumes/me")
async def get_my_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Only return current_user's resumes
    pass
```

### Task 4: Account Security Features (1-2 days)

**Rate Limiting:**
- Max 5 failed login attempts per email
- Lock account for 15 minutes after 5 failures
- Reset counter on successful login

**Password Requirements:**
- Minimum 8 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 number
- At least 1 special character

**Token Security:**
- Store refresh tokens in `refresh_tokens` table (new table)
- Invalidate tokens on logout
- Support token revocation

---

## 📚 Documentation Updates

### 1. Update API_ENDPOINTS.md

Add new section: **Authentication Endpoints**

```markdown
## Authentication

### Register New User
**POST** `/api/v1/auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Login
**POST** `/api/v1/auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

[Continue for all endpoints...]
```

### 2. Update DEVELOPMENT.md

Add section: **Working with Authentication**

```markdown
## Authentication Flow

### Getting a Token
```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'
```

### Using Authenticated Endpoints
```bash
export TOKEN="your_access_token_here"

curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### Testing Authentication in Swagger UI
1. Go to http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Enter token: `Bearer your_access_token_here`
4. Click "Authorize" and "Close"
5. All protected endpoints now include token
```

### 3. Update README_TESTING.md

Add section: **Testing Authentication**

---

## 🧪 Test Plan

### Unit Tests (tests/test_auth_security.py)

```python
@pytest.mark.unit
def test_password_hashing():
    """Test password hashing and verification."""
    password = "SecurePass123!"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong", hashed) is False

@pytest.mark.unit
def test_create_access_token():
    """Test JWT access token creation."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data, timedelta(minutes=30))
    
    assert token is not None
    assert len(token) > 50
    
    decoded = verify_token(token)
    assert decoded["sub"] == "user@example.com"

@pytest.mark.unit
def test_password_strength_validation():
    """Test password strength requirements."""
    # Valid passwords
    assert is_valid_password("SecurePass123!") is True
    
    # Invalid passwords
    assert is_valid_password("short") is False  # Too short
    assert is_valid_password("alllowercase123!") is False  # No uppercase
    assert is_valid_password("ALLUPPERCASE123!") is False  # No lowercase
    assert is_valid_password("NoNumbers!") is False  # No numbers
    assert is_valid_password("NoSpecialChars123") is False  # No special chars

@pytest.mark.unit
def test_expired_token():
    """Test that expired tokens are rejected."""
    data = {"sub": "user@example.com"}
    token = create_access_token(data, timedelta(seconds=-1))  # Already expired
    
    decoded = verify_token(token)
    assert decoded is None
```

### Integration Tests (tests/test_auth_endpoints.py)

```python
@pytest.mark.integration
async def test_user_registration(async_client: AsyncClient):
    """Test user registration endpoint."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "full_name": "New User"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert "password" not in data
    assert "password_hash" not in data

@pytest.mark.integration
async def test_duplicate_email_registration(async_client: AsyncClient, test_user):
    """Test that duplicate emails are rejected."""
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": test_user.email,  # Already exists
            "password": "SecurePass123!",
            "full_name": "Duplicate User"
        }
    )
    
    assert response.status_code == 409  # Conflict
    assert "already registered" in response.json()["detail"].lower()

@pytest.mark.integration
async def test_login_success(async_client: AsyncClient, test_user):
    """Test successful login."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"  # Plain password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.integration
async def test_login_wrong_password(async_client: AsyncClient, test_user):
    """Test login with wrong password."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "incorrect" in response.json()["detail"].lower()

@pytest.mark.integration
async def test_get_current_user(async_client: AsyncClient, auth_headers):
    """Test getting current user profile."""
    response = await async_client.get(
        "/api/v1/auth/me",
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "password" not in data

@pytest.mark.integration
async def test_protected_endpoint_without_token(async_client: AsyncClient):
    """Test that protected endpoint requires authentication."""
    response = await async_client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    assert "not authenticated" in response.json()["detail"].lower()

@pytest.mark.integration
async def test_account_lockout_after_failed_attempts(
    async_client: AsyncClient, 
    test_user
):
    """Test account locks after 5 failed login attempts."""
    # Attempt 5 failed logins
    for i in range(5):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": test_user.email, "password": "wrong"}
        )
        assert response.status_code == 401
    
    # 6th attempt should be locked
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": test_user.email, "password": "wrong"}
    )
    assert response.status_code == 423  # Locked
    assert "locked" in response.json()["detail"].lower()

@pytest.mark.integration
async def test_refresh_token(async_client: AsyncClient, auth_tokens):
    """Test refreshing access token."""
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": auth_tokens["refresh_token"]}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["access_token"] != auth_tokens["access_token"]

@pytest.mark.integration
async def test_logout(async_client: AsyncClient, auth_headers, auth_tokens):
    """Test logout invalidates refresh token."""
    # Logout
    response = await async_client.post(
        "/api/v1/auth/logout",
        headers=auth_headers,
        json={"refresh_token": auth_tokens["refresh_token"]}
    )
    assert response.status_code == 200
    
    # Try to use refresh token (should fail)
    response = await async_client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": auth_tokens["refresh_token"]}
    )
    assert response.status_code == 401
```

### Test Fixtures (tests/conftest.py)

Add new fixtures:

```python
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a test user."""
    from app.core.security import get_password_hash
    
    user = User(
        email="testuser@example.com",
        password_hash=get_password_hash("testpassword123"),
        full_name="Test User",
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

@pytest.fixture
async def auth_tokens(async_client: AsyncClient, test_user) -> dict:
    """Get auth tokens for test user."""
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user.email,
            "password": "testpassword123"
        }
    )
    return response.json()

@pytest.fixture
def auth_headers(auth_tokens: dict) -> dict:
    """Get authorization headers with access token."""
    return {
        "Authorization": f"Bearer {auth_tokens['access_token']}"
    }
```

### Coverage Goals
- **Target Coverage:** 85%+ for auth module
- **Critical Paths:** Login, registration, token validation (100% coverage)
- **Edge Cases:** Expired tokens, locked accounts, invalid inputs

---

## ✅ Acceptance Criteria

### Functional Requirements
- [ ] Users can register new accounts with valid email and password
- [ ] Users can login and receive JWT access + refresh tokens
- [ ] Users can access protected endpoints with valid token
- [ ] Users can refresh access token using refresh token
- [ ] Users can view their own profile
- [ ] Users can update their profile (name, email)
- [ ] Users can change their password
- [ ] Users can logout (invalidate refresh token)

### Security Requirements
- [ ] Passwords are hashed with bcrypt (never stored plain)
- [ ] JWT tokens are signed and validated
- [ ] Access tokens expire after 30 minutes
- [ ] Refresh tokens expire after 7 days
- [ ] Account locks after 5 failed login attempts
- [ ] Password strength requirements enforced
- [ ] Tokens include user ID and email claims

### Testing Requirements
- [ ] All unit tests pass (20+ tests for auth)
- [ ] All integration tests pass (15+ tests for endpoints)
- [ ] Overall coverage remains above 80%
- [ ] Auth module coverage above 85%

### Documentation Requirements
- [ ] API_ENDPOINTS.md updated with auth endpoints
- [ ] DEVELOPMENT.md updated with auth workflow
- [ ] README_TESTING.md updated with auth test examples
- [ ] Swagger UI includes auth endpoints with examples

---

## 🔗 Dependencies

**Required Issues:**
- ✅ Issue #25: FastAPI backend setup (completed)

**Blocks:**
- Issue #27: Frontend authentication UI (future)
- Issue #28: Resume upload endpoint (future)
- All future user-specific features

**Python Packages to Install:**
```bash
poetry add python-jose[cryptography]
poetry add passlib[bcrypt]
poetry add python-multipart  # For form data
```

---

## 📅 Timeline Estimate

**Total Time:** 7-10 days

| Task | Duration | Dependencies |
|------|----------|--------------|
| Core security utilities | 1-2 days | - |
| Auth endpoints (register, login) | 2-3 days | Security utilities |
| Token refresh & logout | 1 day | Login working |
| Account security (lockout, validation) | 1-2 days | Login working |
| Protect existing endpoints | 1 day | Auth working |
| Write tests | 2-3 days | Endpoints complete |
| Documentation updates | 1 day | Everything complete |

**Milestones:**
- **Day 3:** Registration and login working
- **Day 5:** All endpoints implemented
- **Day 7:** Tests passing, documentation complete

---

## 🚀 Getting Started

### Step 1: Create Branch
```bash
git checkout main
git pull origin main
git checkout -b feature/auth-jwt-26
```

### Step 2: Install Dependencies
```bash
cd src/backend
poetry add python-jose[cryptography] passlib[bcrypt] python-multipart
```

### Step 3: Create Core Files
Start with `app/core/security.py` and implement:
1. Password hashing functions
2. JWT token creation/validation
3. Password strength validation

### Step 4: Build Incrementally
- Get registration working first
- Then login with token generation
- Then protect one endpoint as proof of concept
- Then implement remaining features

### Step 5: Test as You Go
Write tests immediately after implementing each feature.

---

## 📝 Notes

**Security Best Practices:**
- Never log tokens or passwords
- Use HTTPS in production
- Rotate JWT secret keys periodically
- Implement rate limiting on auth endpoints
- Consider adding 2FA support later

**Future Enhancements (Not in Scope):**
- Email verification (send confirmation email)
- Password reset via email
- OAuth integration (Google, GitHub)
- WebAuthn/passwordless authentication
- Session management with Redis
- Multi-factor authentication (2FA)

---

## 📚 References

- [FastAPI Security Documentation](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT.io](https://jwt.io/) - Token debugger
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [python-jose Documentation](https://python-jose.readthedocs.io/)
- [Passlib Documentation](https://passlib.readthedocs.io/)

---

**Issue created by:** GitHub Copilot  
**Date:** December 27, 2025  
**Related:** FUNCTIONAL_REQUIREMENTS.md (FR-2), ROADMAP.md (Phase 1, Week 1-2)
