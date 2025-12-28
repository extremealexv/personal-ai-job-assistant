#!/bin/bash
# Test script for Resume Management Phase 1 endpoints
# Tests: Upload, Get, Delete resume

set -e  # Exit on error

# Configuration
BASE_URL="http://localhost:8000/api/v1"
TEST_EMAIL="resume_test_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
TEST_USER_NAME="Resume Test User"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test results
PASSED=0
FAILED=0

# Helper function to print test results
print_test() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAIL${NC}: $2"
        ((FAILED++))
    fi
}

echo "=========================================="
echo "Resume Management API Tests - Phase 1"
echo "=========================================="
echo ""

# ==============================================================================
# Setup: Register user and login
# ==============================================================================

echo "Setting up test user..."

# Register
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"${TEST_EMAIL}\",
        \"password\": \"${TEST_PASSWORD}\",
        \"full_name\": \"${TEST_USER_NAME}\"
    }")

REGISTER_STATUS=$?
if [ $REGISTER_STATUS -ne 0 ]; then
    echo -e "${RED}Failed to register user${NC}"
    exit 1
fi

echo "✓ User registered: ${TEST_EMAIL}"

# Login to get token
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"${TEST_EMAIL}\",
        \"password\": \"${TEST_PASSWORD}\"
    }")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}Failed to get access token${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo "✓ User logged in, token obtained"
echo ""

# ==============================================================================
# Test 1: Get master resume (should not exist yet)
# ==============================================================================

echo "Test 1: Get master resume (should return 404)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/resumes/master" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "404" ]; then
    print_test 0 "GET /resumes/master returns 404 when no resume exists"
else
    print_test 1 "GET /resumes/master should return 404, got $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Test 2: Upload resume without file (should fail)
# ==============================================================================

echo "Test 2: Upload resume without file (should return 422)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/resumes/upload" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "422" ]; then
    print_test 0 "POST /resumes/upload without file returns 422"
else
    print_test 1 "POST /resumes/upload should return 422, got $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Test 3: Create sample resume files for testing
# ==============================================================================

echo "Creating sample resume files..."

# Create a sample PDF (simple text file with PDF magic number)
SAMPLE_PDF="/tmp/test_resume.pdf"
echo "%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(John Doe Resume) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000315 00000 n
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
407
%%EOF" > $SAMPLE_PDF

echo "✓ Sample PDF created: $SAMPLE_PDF"

# Note: For a real DOCX, we need a proper zip file with XML
# For now, we'll skip DOCX testing unless you have a real file
echo ""

# ==============================================================================
# Test 4: Upload resume with invalid file type (should fail)
# ==============================================================================

echo "Test 4: Upload invalid file type (should return 400)"
echo "test content" > /tmp/test.txt

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/resumes/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@/tmp/test.txt")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "400" ]; then
    print_test 0 "POST /resumes/upload with .txt file returns 400"
else
    print_test 1 "POST /resumes/upload with .txt should return 400, got $HTTP_CODE"
fi

rm /tmp/test.txt
echo ""

# ==============================================================================
# Test 5: Upload resume with authentication
# ==============================================================================

echo "Test 5: Upload resume with valid PDF"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/resumes/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${SAMPLE_PDF}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "201" ]; then
    RESUME_ID=$(echo $BODY | jq -r '.id')
    print_test 0 "POST /resumes/upload successfully uploads resume (ID: ${RESUME_ID})"
    echo "Response: $BODY" | jq '.'
else
    print_test 1 "POST /resumes/upload failed with status $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# ==============================================================================
# Test 6: Get master resume (should now exist)
# ==============================================================================

echo "Test 6: Get master resume (should return 200)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/resumes/master" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

if [ "$HTTP_CODE" = "200" ]; then
    print_test 0 "GET /resumes/master returns 200"
    RETRIEVED_ID=$(echo $BODY | jq -r '.id')
    if [ "$RETRIEVED_ID" = "$RESUME_ID" ]; then
        print_test 0 "Retrieved resume ID matches uploaded resume ID"
    else
        print_test 1 "Resume ID mismatch (expected: $RESUME_ID, got: $RETRIEVED_ID)"
    fi
    echo "Resume data:"
    echo $BODY | jq '{id, user_id, original_filename, file_size_bytes, mime_type, created_at}'
else
    print_test 1 "GET /resumes/master failed with status $HTTP_CODE"
    echo "Response: $BODY"
fi
echo ""

# ==============================================================================
# Test 7: Try to upload second resume (should fail)
# ==============================================================================

echo "Test 7: Upload second resume (should return 400 - already exists)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${BASE_URL}/resumes/upload" \
    -H "Authorization: Bearer ${TOKEN}" \
    -F "file=@${SAMPLE_PDF}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "400" ]; then
    print_test 0 "POST /resumes/upload returns 400 when resume already exists"
else
    print_test 1 "POST /resumes/upload should return 400, got $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Test 8: Delete master resume
# ==============================================================================

echo "Test 8: Delete master resume"
RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/resumes/master" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "204" ]; then
    print_test 0 "DELETE /resumes/master returns 204"
else
    print_test 1 "DELETE /resumes/master failed with status $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Test 9: Get master resume after deletion (should return 404)
# ==============================================================================

echo "Test 9: Get master resume after deletion (should return 404)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "${BASE_URL}/resumes/master" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "404" ]; then
    print_test 0 "GET /resumes/master returns 404 after deletion"
else
    print_test 1 "GET /resumes/master should return 404 after deletion, got $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Test 10: Delete non-existent resume (should return 404)
# ==============================================================================

echo "Test 10: Delete non-existent resume (should return 404)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "${BASE_URL}/resumes/master" \
    -H "Authorization: Bearer ${TOKEN}")

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "404" ]; then
    print_test 0 "DELETE /resumes/master returns 404 when no resume exists"
else
    print_test 1 "DELETE /resumes/master should return 404, got $HTTP_CODE"
fi
echo ""

# ==============================================================================
# Cleanup
# ==============================================================================

echo "Cleaning up..."
rm -f $SAMPLE_PDF
echo "✓ Test files removed"
echo ""

# ==============================================================================
# Summary
# ==============================================================================

echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All tests passed! ✓${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed ✗${NC}"
    exit 1
fi
