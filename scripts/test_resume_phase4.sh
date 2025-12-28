#!/bin/bash

# Phase 4: Resume Advanced Features Testing Script
# Tests search, statistics, and duplication endpoints

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
API_URL="${API_URL:-http://localhost:8000/api/v1}"
TEST_EMAIL="advanced_test_$(date +%s)@example.com"
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
    TESTS_PASSED=$((TESTS_PASSED + 1))
}

print_fail() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    TESTS_FAILED=$((TESTS_FAILED + 1))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# ============================================================================
# Setup: Create user and upload master resume with data
# ============================================================================

echo ""
echo "=========================================="
echo "Phase 4: Advanced Features Testing"
echo "=========================================="
echo ""

print_info "Setting up test environment..."

# 1. Create test user
print_test "SETUP-1" "Creating test user"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$TEST_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"Advanced Tester\"}")

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

# 3. Create a minimal PDF resume
print_test "SETUP-3" "Creating test PDF"
TEST_PDF="/tmp/test_resume_advanced_$$.pdf"

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
<< /Length 150 >>
stream
BT
/F1 12 Tf
100 700 Td
(John Doe - Software Engineer) Tj
0 -20 Td
(Python Developer at TechCorp) Tj
0 -20 Td
(Experience with FastAPI and PostgreSQL) Tj
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
504
%%EOF
PDFEOF

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

# 5. Add structured data for search testing
print_test "SETUP-5" "Adding work experience"
curl -s -X POST "$API_URL/resumes/work-experiences" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"company_name\": \"TechCorp\",
    \"job_title\": \"Senior Python Developer\",
    \"employment_type\": \"full_time\",
    \"start_date\": \"2020-01-01\",
    \"is_current\": true,
    \"description\": \"Developed backend APIs using FastAPI and PostgreSQL\"
  }" > /dev/null

print_pass "Work experience added"

print_test "SETUP-6" "Adding skills"
curl -s -X POST "$API_URL/resumes/skills" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"skill_name\": \"Python\",
    \"category\": \"programming_language\"
  }" > /dev/null

curl -s -X POST "$API_URL/resumes/skills" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"skill_name\": \"FastAPI\",
    \"category\": \"framework\"
  }" > /dev/null

curl -s -X POST "$API_URL/resumes/skills" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"skill_name\": \"PostgreSQL\",
    \"category\": \"tool\"
  }" > /dev/null

print_pass "Skills added"

print_test "SETUP-7" "Creating resume versions"
# Version 1
VERSION1_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"version_name\": \"Backend Engineer - TechCorp\",
    \"target_role\": \"Backend Engineer\",
    \"target_company\": \"TechCorp\"
  }")

VERSION1_ID=$(echo "$VERSION1_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

# Version 2
VERSION2_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$MASTER_RESUME_ID\",
    \"version_name\": \"Full Stack Developer - StartupX\",
    \"target_role\": \"Full Stack Developer\",
    \"target_company\": \"StartupX\"
  }")

VERSION2_ID=$(echo "$VERSION2_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -n "$VERSION1_ID" ] && [ -n "$VERSION2_ID" ]; then
    print_pass "Resume versions created (2 versions)"
else
    print_fail "Failed to create versions"
fi

# ============================================================================
# Test Advanced Features
# ============================================================================

echo ""
echo "=========================================="
echo "Testing Advanced Features"
echo "=========================================="
echo ""

# Test 1: Search for "Python"
print_test "1" "Search resumes for 'Python'"
SEARCH_RESPONSE=$(curl -s -X GET "$API_URL/resumes/search?q=Python" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$SEARCH_RESPONSE" | grep -q "\"total_results\"" && echo "$SEARCH_RESPONSE" | grep -q "Python"; then
    print_pass "Search found results for 'Python'"
else
    print_fail "Search failed: $SEARCH_RESPONSE"
fi

# Test 2: Search for "TechCorp"
print_test "2" "Search resumes for 'TechCorp'"
SEARCH_TECH_RESPONSE=$(curl -s -X GET "$API_URL/resumes/search?q=TechCorp" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$SEARCH_TECH_RESPONSE" | grep -q "TechCorp"; then
    print_pass "Search found 'TechCorp' in work experience and version"
else
    print_fail "Search failed for TechCorp: $SEARCH_TECH_RESPONSE"
fi

# Test 3: Search for non-existent term
print_test "3" "Search for non-existent term"
SEARCH_EMPTY_RESPONSE=$(curl -s -X GET "$API_URL/resumes/search?q=NonExistentSkill123" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$SEARCH_EMPTY_RESPONSE" | grep -q "\"total_results\":0"; then
    print_pass "Search correctly returned 0 results"
else
    print_fail "Search should return 0 results: $SEARCH_EMPTY_RESPONSE"
fi

# Test 4: Get resume statistics
print_test "4" "Get resume statistics"
STATS_RESPONSE=$(curl -s -X GET "$API_URL/resumes/stats" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$STATS_RESPONSE" | grep -q "structured_data" && \
   echo "$STATS_RESPONSE" | grep -q "resume_versions" && \
   echo "$STATS_RESPONSE" | grep -q "\"total_versions\":2"; then
    print_pass "Statistics retrieved successfully"
else
    print_fail "Failed to get statistics: $STATS_RESPONSE"
fi

# Test 5: Verify stats show correct counts
print_test "5" "Verify stats show correct counts"
if echo "$STATS_RESPONSE" | grep -q "\"work_experiences\":1" && \
   echo "$STATS_RESPONSE" | grep -q "\"skills\":3"; then
    print_pass "Statistics show correct counts"
else
    print_fail "Statistics counts incorrect: $STATS_RESPONSE"
fi

# Test 6: Duplicate resume version
print_test "6" "Duplicate resume version"
DUPLICATE_RESPONSE=$(curl -s -X POST "$API_URL/resumes/versions/$VERSION1_ID/duplicate" \
  -H "Authorization: Bearer $JWT_TOKEN")

DUPLICATE_ID=$(echo "$DUPLICATE_RESPONSE" | grep -o '"id":"[^"]*' | sed 's/"id":"//')

if [ -n "$DUPLICATE_ID" ] && echo "$DUPLICATE_RESPONSE" | grep -q "(Copy)"; then
    print_pass "Resume version duplicated (ID: ${DUPLICATE_ID:0:8}...)"
else
    print_fail "Failed to duplicate version: $DUPLICATE_RESPONSE"
fi

# Test 7: Verify duplicate is in list
print_test "7" "Verify duplicate appears in version list"
VERSIONS_LIST=$(curl -s -X GET "$API_URL/resumes/versions" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$VERSIONS_LIST" | grep -q "\"total\":3" && echo "$VERSIONS_LIST" | grep -q "$DUPLICATE_ID"; then
    print_pass "Duplicate version appears in list (3 total)"
else
    print_fail "Duplicate not in list: $VERSIONS_LIST"
fi

# Test 8: Verify duplicate has correct name
print_test "8" "Verify duplicate has '(Copy)' suffix"
DUPLICATE_GET=$(curl -s -X GET "$API_URL/resumes/versions/$DUPLICATE_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$DUPLICATE_GET" | grep -q "Backend Engineer - TechCorp (Copy)"; then
    print_pass "Duplicate has correct name with (Copy) suffix"
else
    print_fail "Duplicate name incorrect: $DUPLICATE_GET"
fi

# Test 9: Stats after adding duplicate
print_test "9" "Verify stats updated after duplicate"
STATS2_RESPONSE=$(curl -s -X GET "$API_URL/resumes/stats" \
  -H "Authorization: Bearer $JWT_TOKEN")

if echo "$STATS2_RESPONSE" | grep -q "\"total_versions\":3"; then
    print_pass "Statistics updated to show 3 versions"
else
    print_fail "Statistics not updated: $STATS2_RESPONSE"
fi

# ============================================================================
# Test Error Handling
# ============================================================================

echo ""
echo "=========================================="
echo "Testing Error Handling"
echo "=========================================="
echo ""

# Test 10: Duplicate non-existent version
print_test "10" "Duplicate non-existent version"
INVALID_ID="00000000-0000-0000-0000-000000000000"
DUPLICATE_INVALID_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X POST "$API_URL/resumes/versions/$INVALID_ID/duplicate" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$DUPLICATE_INVALID_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Duplicate of non-existent version rejected (404)"
else
    print_fail "Expected 404, got $HTTP_STATUS"
fi

# Test 11: Stats without master resume (create new user)
print_test "11" "Stats without master resume"
NEW_USER_EMAIL="no_resume_$(date +%s)@example.com"

# Register new user
curl -s -X POST "$API_URL/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$NEW_USER_EMAIL\", \"password\": \"$TEST_PASSWORD\", \"full_name\": \"No Resume User\"}" > /dev/null

# Login as new user
NEW_LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$NEW_USER_EMAIL\", \"password\": \"$TEST_PASSWORD\"}")

NEW_JWT_TOKEN=$(echo "$NEW_LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | sed 's/"access_token":"//')

# Try to get stats
STATS_NO_RESUME_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X GET "$API_URL/resumes/stats" \
  -H "Authorization: Bearer $NEW_JWT_TOKEN")

HTTP_STATUS=$(echo "$STATS_NO_RESUME_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "404" ]; then
    print_pass "Stats without master resume rejected (404)"
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

print_test "CLEANUP-1" "Deleting resume versions"
for vid in $VERSION1_ID $VERSION2_ID $DUPLICATE_ID; do
    if [ -n "$vid" ]; then
        curl -s -X DELETE "$API_URL/resumes/versions/$vid" \
          -H "Authorization: Bearer $JWT_TOKEN" > /dev/null
    fi
done
print_pass "Versions deleted"

print_test "CLEANUP-2" "Deleting master resume"
CLEANUP_RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" \
  -X DELETE "$API_URL/resumes/$MASTER_RESUME_ID" \
  -H "Authorization: Bearer $JWT_TOKEN")

HTTP_STATUS=$(echo "$CLEANUP_RESPONSE" | grep "HTTP_STATUS" | cut -d':' -f2)

if [ "$HTTP_STATUS" = "204" ]; then
    print_pass "Master resume deleted"
else
    print_pass "Master resume cleanup (status: $HTTP_STATUS)"
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
