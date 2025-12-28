#!/bin/bash

# Phase 3: Resume Version Management Testing Script
# Tests all resume version CRUD endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000/api/v1}"
TEST_EMAIL="version_test_$(date +%s)@example.com"
TEST_PASSWORD="SecurePass123!"

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST $1]${NC} $2"
}

print_pass() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# ============================================================================
# Setup: Create user and upload master resume
# ============================================================================

echo ""
echo "=========================================="
echo "Phase 3: Resume Version Testing"
echo "=========================================="
echo ""

print_info "Setting up test environment..."

# 1. Create test user
print_test "SETUP-1" "Creating test user"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"Version Tester\"}")

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    print_pass "Test user created"
else
    print_fail "Failed to create test user: $REGISTER_RESPONSE"
    exit 1
fi

# 2. Login to get JWT token
print_test "SETUP-2" "Logging in"
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

JWT_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

if [ -z "$JWT_TOKEN" ]; then
    print_fail "Failed to login: $LOGIN_RESPONSE"
    exit 1
fi

print_pass "Login successful"

# 3. Create a minimal PDF resume for testing
print_test "SETUP-3" "Creating test PDF"
TEST_PDF="/tmp/test_resume_version_$$.pdf"

cat > "$TEST_PDF" << 'PDFEOF'
%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources 4 0 R /MediaBox [0 0 612 792] /Contents 5 0 R >>
endobj
4 0 obj
<< /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >>
endobj
5 0 obj
<< /Length 100 >>
stream
BT
/F1 12 Tf
100 700 Td
(Version Test Resume) Tj
0 -20 Td
(Software Engineer) Tj
ET
endstream
endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
0000000304 00000 n 
trailer
<< /Size 6 /Root 1 0 R >>
startxref
454
%%EOF
PDFEOF

if [ ! -f "$TEST_PDF" ]; then
    print_fail "Failed to create test PDF"
    exit 1
fi

print_pass "Test PDF created"

# 4. Upload master resume
print_test "SETUP-4" "Uploading master resume"
UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/resumes/upload" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -F "file=@$TEST_PDF")

MASTER_RESUME_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -z "$MASTER_RESUME_ID" ]; then
    print_fail "Failed to upload master resume: $UPLOAD_RESPONSE"
    rm -f "$TEST_PDF"
    exit 1
fi

print_pass "Master resume uploaded (ID: ${MASTER_RESUME_ID:0:8}...)"

# ============================================================================
# Test Resume Version CRUD Operations
# ============================================================================

echo ""
echo "=========================================="
echo "Testing Resume Version CRUD"
echo "=========================================="
echo ""

# Test 1: Create resume version
print_test "1" "Create resume version"
VERSION_CREATE_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"version_name\": \"Senior Backend Engineer - TechCorp\",
    \"target_role\": \"Senior Backend Engineer\",
    \"target_company\": \"TechCorp\",
    \"modifications\": {
      \"skills_emphasized\": [\"Python\", \"FastAPI\", \"PostgreSQL\"],
      \"experience_reordered\": true
    },
    \"ai_model_used\": \"gpt-4-turbo\"
  }")

VERSION_ID=$(echo "$VERSION_CREATE_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -n "$VERSION_ID" ] && echo "$VERSION_CREATE_RESPONSE" | grep -q "Senior Backend Engineer"; then
    print_pass "Resume version created (ID: ${VERSION_ID:0:8}...)"
else
    print_fail "Failed to create resume version: $VERSION_CREATE_RESPONSE"
fi

# Test 2: List resume versions
print_test "2" "List resume versions"
VERSION_LIST_RESPONSE=$(curl -s -X GET "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSION_LIST_RESPONSE" | grep -q "\"total\":1" && echo "$VERSION_LIST_RESPONSE" | grep -q "$VERSION_ID"; then
    print_pass "Resume versions listed (1 version)"
else
    print_fail "Failed to list resume versions: $VERSION_LIST_RESPONSE"
fi

# Test 3: Get specific resume version
print_test "3" "Get specific resume version"
VERSION_GET_RESPONSE=$(curl -s -X GET "$API_URL/resumes/versions/$VERSION_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSION_GET_RESPONSE" | grep -q "$VERSION_ID" && echo "$VERSION_GET_RESPONSE" | grep -q "TechCorp"; then
    print_pass "Resume version retrieved"
else
    print_fail "Failed to get resume version: $VERSION_GET_RESPONSE"
fi

# Test 4: Update resume version
print_test "4" "Update resume version"
VERSION_UPDATE_RESPONSE=$(curl -s -X PUT "$API_URL/resumes/versions/$VERSION_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"version_name\": \"Senior Backend Engineer - TechCorp (Updated)\",
    \"target_role\": \"Lead Backend Engineer\",
    \"pdf_file_path\": \"/resumes/versions/senior-backend-techcorp.pdf\"
  }")

if echo "$VERSION_UPDATE_RESPONSE" | grep -q "Updated" && echo "$VERSION_UPDATE_RESPONSE" | grep -q "Lead Backend"; then
    print_pass "Resume version updated"
else
    print_fail "Failed to update resume version: $VERSION_UPDATE_RESPONSE"
fi

# Test 5: Create second version (for job posting test)
print_test "5" "Create second resume version"
VERSION2_CREATE_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"version_name\": \"Data Engineer - DataCo\",
    \"target_role\": \"Data Engineer\",
    \"target_company\": \"DataCo\",
    \"modifications\": {
      \"skills_emphasized\": [\"Python\", \"SQL\", \"ETL\"],
      \"experience_reordered\": false
    }
  }")

VERSION2_ID=$(echo "$VERSION2_CREATE_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -n "$VERSION2_ID" ]; then
    print_pass "Second resume version created (ID: ${VERSION2_ID:0:8}...)"
else
    print_fail "Failed to create second version: $VERSION2_CREATE_RESPONSE"
fi

# Test 6: List versions again (should be 2)
print_test "6" "List resume versions (2 versions)"
VERSION_LIST2_RESPONSE=$(curl -s -X GET "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSION_LIST2_RESPONSE" | grep -q "\"total\":2"; then
    print_pass "Resume versions listed (2 versions)"
else
    print_fail "Expected 2 versions: $VERSION_LIST2_RESPONSE"
fi

# Test 7: Create version with job posting ID (mock UUID for now)
print_test "7" "Create version with job posting ID"
JOB_POSTING_ID="550e8400-e29b-41d4-a716-446655440000"
VERSION3_CREATE_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"version_name\": \"Full Stack - StartupX\",
    \"target_role\": \"Full Stack Developer\",
    \"target_company\": \"StartupX\",
    \"job_posting_id\": \"$JOB_POSTING_ID\",
    \"modifications\": {
      \"skills_emphasized\": [\"React\", \"Node.js\", \"Python\"]
    }
  }")

VERSION3_ID=$(echo "$VERSION3_CREATE_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -n "$VERSION3_ID" ] && echo "$VERSION3_CREATE_RESPONSE" | grep -q "StartupX"; then
    print_pass "Version with job posting created (ID: ${VERSION3_ID:0:8}...)"
else
    print_fail "Failed to create version with job posting: $VERSION3_CREATE_RESPONSE"
fi

# Test 8: Get versions by job posting ID
print_test "8" "Get versions by job posting ID"
VERSION_BY_JOB_RESPONSE=$(curl -s -X GET "$API_URL/resumes/versions/job/$JOB_POSTING_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSION_BY_JOB_RESPONSE" | grep -q "\"total\":1" && echo "$VERSION_BY_JOB_RESPONSE" | grep -q "$VERSION3_ID"; then
    print_pass "Versions filtered by job posting"
else
    print_fail "Failed to get versions by job posting: $VERSION_BY_JOB_RESPONSE"
fi

# Test 9: Delete a resume version
print_test "9" "Delete resume version"
VERSION_DELETE_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$API_URL/resumes/versions/$VERSION2_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$VERSION_DELETE_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "204" ]; then
    print_pass "Resume version deleted"
else
    print_fail "Failed to delete version (status: $HTTP_STATUS)"
fi

# Test 10: Verify version is deleted
print_test "10" "Verify deleted version not listed"
VERSION_LIST3_RESPONSE=$(curl -s -X GET "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSION_LIST3_RESPONSE" | grep -q "\"total\":2" && ! echo "$VERSION_LIST3_RESPONSE" | grep -q "$VERSION2_ID"; then
    print_pass "Deleted version not in list (2 remaining)"
else
    print_fail "Deleted version still appears: $VERSION_LIST3_RESPONSE"
fi

# ============================================================================
# Test Error Handling
# ============================================================================

echo ""
echo "=========================================="
echo "Testing Error Handling"
echo "=========================================="
echo ""

# Test 11: Get non-existent version
print_test "11" "Get non-existent resume version"
INVALID_ID="00000000-0000-0000-0000-000000000000"
VERSION_INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X GET "$API_URL/resumes/versions/$INVALID_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$VERSION_INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Non-existent version rejected (404)"
else
    print_fail "Expected 404, got $HTTP_STATUS"
fi

# Test 12: Create version with invalid master_resume_id
print_test "12" "Create version with invalid master resume ID"
VERSION_INVALID_MASTER_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$INVALID_ID\",
    \"version_name\": \"Test Version\",
    \"target_role\": \"Test Role\"
  }")

HTTP_STATUS=$(echo "$VERSION_INVALID_MASTER_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Invalid master resume rejected (404)"
else
    print_fail "Expected 404, got $HTTP_STATUS"
fi

# Test 13: Update non-existent version
print_test "13" "Update non-existent version"
VERSION_UPDATE_INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X PUT "$API_URL/resumes/versions/$INVALID_ID" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"version_name\": \"Updated Name\"}")

HTTP_STATUS=$(echo "$VERSION_UPDATE_INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Non-existent version update rejected (404)"
else
    print_fail "Expected 404, got $HTTP_STATUS"
fi

# Test 14: Delete non-existent version
print_test "14" "Delete non-existent version"
VERSION_DELETE_INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$API_URL/resumes/versions/$INVALID_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$VERSION_DELETE_INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Non-existent version deletion rejected (404)"
else
    print_fail "Expected 404, got $HTTP_STATUS"
fi

# ============================================================================
# Cleanup
# ============================================================================

echo ""
echo "=========================================="
echo "Cleanup"
echo "=========================================="
echo ""

print_test "CLEANUP-1" "Deleting master resume"
CLEANUP_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" -X DELETE "$API_URL/resumes/$MASTER_RESUME_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$CLEANUP_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "204" ]; then
    print_pass "Master resume deleted"
else
    print_fail "Failed to delete master resume"
fi

# Clean up test PDF
rm -f "$TEST_PDF"
print_pass "Test PDF cleaned up"

# ============================================================================
# Test Summary
# ============================================================================

echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo "=========================================="

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC} ✓"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC} ✗"
    exit 1
fi
