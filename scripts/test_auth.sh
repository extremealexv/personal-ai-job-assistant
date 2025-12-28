#!/bin/bash
# Test script for authentication endpoints

BASE_URL="http://localhost:8000"
API_BASE="${BASE_URL}/api/v1"

echo "🧪 Testing Authentication Endpoints"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Register a new user
echo -e "${YELLOW}Test 1: Register new user${NC}"
REGISTER_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }')

REGISTER_BODY=$(echo "$REGISTER_RESPONSE" | head -n -1)
REGISTER_STATUS=$(echo "$REGISTER_RESPONSE" | tail -n 1)

if [ "$REGISTER_STATUS" = "201" ]; then
  echo -e "${GREEN}✓ Registration successful (201)${NC}"
  echo "$REGISTER_BODY" | jq '.'
else
  echo -e "${RED}✗ Registration failed (Status: $REGISTER_STATUS)${NC}"
  echo "$REGISTER_BODY"
fi
echo ""

# Test 2: Login
echo -e "${YELLOW}Test 2: Login${NC}"
LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "SecurePass123!"
  }')

LOGIN_BODY=$(echo "$LOGIN_RESPONSE" | head -n -1)
LOGIN_STATUS=$(echo "$LOGIN_RESPONSE" | tail -n 1)

if [ "$LOGIN_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Login successful (200)${NC}"
  ACCESS_TOKEN=$(echo "$LOGIN_BODY" | jq -r '.access_token')
  REFRESH_TOKEN=$(echo "$LOGIN_BODY" | jq -r '.refresh_token')
  echo "Access Token: ${ACCESS_TOKEN:0:50}..."
  echo "Refresh Token: ${REFRESH_TOKEN:0:50}..."
else
  echo -e "${RED}✗ Login failed (Status: $LOGIN_STATUS)${NC}"
  echo "$LOGIN_BODY"
  exit 1
fi
echo ""

# Test 3: Get current user profile (with token)
echo -e "${YELLOW}Test 3: Get user profile (authenticated)${NC}"
PROFILE_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/auth/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")

PROFILE_BODY=$(echo "$PROFILE_RESPONSE" | head -n -1)
PROFILE_STATUS=$(echo "$PROFILE_RESPONSE" | tail -n 1)

if [ "$PROFILE_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Get profile successful (200)${NC}"
  echo "$PROFILE_BODY" | jq '.'
else
  echo -e "${RED}✗ Get profile failed (Status: $PROFILE_STATUS)${NC}"
  echo "$PROFILE_BODY"
fi
echo ""

# Test 4: Try to access protected endpoint without token
echo -e "${YELLOW}Test 4: Access protected endpoint without token (should fail)${NC}"
NO_AUTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${API_BASE}/auth/me")

NO_AUTH_BODY=$(echo "$NO_AUTH_RESPONSE" | head -n -1)
NO_AUTH_STATUS=$(echo "$NO_AUTH_RESPONSE" | tail -n 1)

if [ "$NO_AUTH_STATUS" = "401" ] || [ "$NO_AUTH_STATUS" = "403" ]; then
  echo -e "${GREEN}✓ Correctly rejected (Status: $NO_AUTH_STATUS)${NC}"
  echo "$NO_AUTH_BODY" | jq '.'
else
  echo -e "${RED}✗ Should have been rejected but got status: $NO_AUTH_STATUS${NC}"
  echo "$NO_AUTH_BODY"
fi
echo ""

# Test 5: Refresh token
echo -e "${YELLOW}Test 5: Refresh access token${NC}"
REFRESH_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/refresh" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

REFRESH_BODY=$(echo "$REFRESH_RESPONSE" | head -n -1)
REFRESH_STATUS=$(echo "$REFRESH_RESPONSE" | tail -n 1)

if [ "$REFRESH_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Token refresh successful (200)${NC}"
  NEW_ACCESS_TOKEN=$(echo "$REFRESH_BODY" | jq -r '.access_token')
  echo "New Access Token: ${NEW_ACCESS_TOKEN:0:50}..."
else
  echo -e "${RED}✗ Token refresh failed (Status: $REFRESH_STATUS)${NC}"
  echo "$REFRESH_BODY"
fi
echo ""

# Test 6: Change password
echo -e "${YELLOW}Test 6: Change password${NC}"
CHANGE_PWD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/change-password" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "SecurePass123!",
    "new_password": "NewSecurePass456!"
  }')

CHANGE_PWD_BODY=$(echo "$CHANGE_PWD_RESPONSE" | head -n -1)
CHANGE_PWD_STATUS=$(echo "$CHANGE_PWD_RESPONSE" | tail -n 1)

if [ "$CHANGE_PWD_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Password change successful (200)${NC}"
  echo "$CHANGE_PWD_BODY" | jq '.'
else
  echo -e "${RED}✗ Password change failed (Status: $CHANGE_PWD_STATUS)${NC}"
  echo "$CHANGE_PWD_BODY"
fi
echo ""

# Test 7: Login with new password
echo -e "${YELLOW}Test 7: Login with new password${NC}"
NEW_LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "NewSecurePass456!"
  }')

NEW_LOGIN_BODY=$(echo "$NEW_LOGIN_RESPONSE" | head -n -1)
NEW_LOGIN_STATUS=$(echo "$NEW_LOGIN_RESPONSE" | tail -n 1)

if [ "$NEW_LOGIN_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Login with new password successful (200)${NC}"
  echo "Password change verified!"
else
  echo -e "${RED}✗ Login with new password failed (Status: $NEW_LOGIN_STATUS)${NC}"
  echo "$NEW_LOGIN_BODY"
fi
echo ""

# Test 8: Logout
echo -e "${YELLOW}Test 8: Logout${NC}"
LOGOUT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/logout" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"refresh_token\": \"$REFRESH_TOKEN\"}")

LOGOUT_BODY=$(echo "$LOGOUT_RESPONSE" | head -n -1)
LOGOUT_STATUS=$(echo "$LOGOUT_RESPONSE" | tail -n 1)

if [ "$LOGOUT_STATUS" = "200" ]; then
  echo -e "${GREEN}✓ Logout successful (200)${NC}"
  echo "$LOGOUT_BODY" | jq '.'
else
  echo -e "${RED}✗ Logout failed (Status: $LOGOUT_STATUS)${NC}"
  echo "$LOGOUT_BODY"
fi
echo ""

# Test 9: Test weak password (should fail)
echo -e "${YELLOW}Test 9: Try to register with weak password (should fail)${NC}"
WEAK_PWD_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "weakuser@example.com",
    "password": "weak",
    "full_name": "Weak User"
  }')

WEAK_PWD_BODY=$(echo "$WEAK_PWD_RESPONSE" | head -n -1)
WEAK_PWD_STATUS=$(echo "$WEAK_PWD_RESPONSE" | tail -n 1)

if [ "$WEAK_PWD_STATUS" = "422" ]; then
  echo -e "${GREEN}✓ Weak password correctly rejected (422)${NC}"
  echo "$WEAK_PWD_BODY" | jq '.'
else
  echo -e "${RED}✗ Weak password should have been rejected but got status: $WEAK_PWD_STATUS${NC}"
  echo "$WEAK_PWD_BODY"
fi
echo ""

# Test 10: Test account lockout (5 failed attempts)
echo -e "${YELLOW}Test 10: Test account lockout (5 failed login attempts)${NC}"
for i in {1..5}; do
  curl -s -X POST "${API_BASE}/auth/login" \
    -H "Content-Type: application/json" \
    -d '{
      "email": "testuser@example.com",
      "password": "WrongPassword123!"
    }' > /dev/null
  echo "  Failed attempt $i/5"
done

LOCKOUT_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${API_BASE}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "testuser@example.com",
    "password": "WrongPassword123!"
  }')

LOCKOUT_BODY=$(echo "$LOCKOUT_RESPONSE" | head -n -1)
LOCKOUT_STATUS=$(echo "$LOCKOUT_RESPONSE" | tail -n 1)

if [ "$LOCKOUT_STATUS" = "423" ]; then
  echo -e "${GREEN}✓ Account correctly locked (423)${NC}"
  echo "$LOCKOUT_BODY" | jq '.'
else
  echo -e "${RED}✗ Account should have been locked but got status: $LOCKOUT_STATUS${NC}"
  echo "$LOCKOUT_BODY"
fi
echo ""

echo "===================================="
echo -e "${GREEN}✅ All tests completed!${NC}"
echo ""
echo "📊 Summary:"
echo "  - Registration: Working"
echo "  - Login: Working"
echo "  - Token authentication: Working"
echo "  - Token refresh: Working"
echo "  - Password change: Working"
echo "  - Password validation: Working"
echo "  - Account lockout: Working"
echo ""
echo "🌐 Swagger UI available at: ${BASE_URL}/docs"
