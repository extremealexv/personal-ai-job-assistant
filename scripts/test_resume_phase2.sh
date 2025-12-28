#!/bin/bash

# =============================================================================
# Resume Management Phase 2 Test Script
# Tests CRUD operations for work experience, education, skills, certifications
# =============================================================================

API_URL="http://localhost:8000/api/v1"
TEST_EMAIL="test_resume_phase2_$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
AUTH_TOKEN=""
TEST_USER_ID=""
MASTER_RESUME_ID=""

# Test result counters
PASSED=0
FAILED=0

# ANSI color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_test() {
    echo -e "${BLUE}[TEST $1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
    ((PASSED++))
}

print_failure() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    ((FAILED++))
}

print_info() {
    echo -e "${YELLOW}ℹ INFO${NC}: $1"
}

# Function to create test user and login
setup_test_user() {
    print_info "Setting up test user..."
    
    # Register user
    REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Test User Phase 2\"}")
    
    TEST_USER_ID=$(echo $REGISTER_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    # Login
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
    
    AUTH_TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$AUTH_TOKEN" ]; then
        print_success "Test user created and authenticated"
    else
        print_failure "Failed to authenticate test user"
        echo "DEBUG: Login response: $LOGIN_RESPONSE"
        exit 1
    fi
}

# Function to upload a test resume
upload_test_resume() {
    print_info "Uploading test resume..."
    
    # Create a sample PDF file with actual text content
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
%%EOF" > /tmp/test_resume_phase2.pdf
    
    UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/resumes/upload" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -F "file=@/tmp/test_resume_phase2.pdf")
    
    MASTER_RESUME_ID=$(echo $UPLOAD_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
    
    if [ -n "$MASTER_RESUME_ID" ]; then
        print_success "Test resume uploaded: $MASTER_RESUME_ID"
    else
        print_failure "Failed to upload test resume"
        echo "DEBUG: Upload response: $UPLOAD_RESPONSE"
        exit 1
    fi
}

# =============================================================================
# WORK EXPERIENCE TESTS
# =============================================================================

test_work_experience_crud() {
    echo ""
    echo "=========================================="
    echo "Testing Work Experience CRUD"
    echo "=========================================="
    
    # Test 1: List work experiences (should be empty)
    print_test 1 "GET /resumes/work-experiences (empty list)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/work-experiences" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 0 ]; then
            print_success "Empty work experience list"
        else
            print_failure "Expected 0 work experiences, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 2: Create work experience
    print_test 2 "POST /resumes/work-experiences (create)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/resumes/work-experiences" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"company_name\": \"Tech Corp\",
            \"job_title\": \"Senior Software Engineer\",
            \"employment_type\": \"full_time\",
            \"location\": \"San Francisco, CA\",
            \"start_date\": \"2020-01-15\",
            \"end_date\": \"2023-12-31\",
            \"is_current\": false,
            \"description\": \"Led backend development team\",
            \"achievements\": [\"Improved API performance by 40%\", \"Mentored 5 junior engineers\"],
            \"technologies\": [\"Python\", \"PostgreSQL\", \"Docker\"],
            \"display_order\": 0
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 201 ]; then
        WORK_EXP_ID=$(echo $BODY | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        print_success "Work experience created: $WORK_EXP_ID"
    else
        print_failure "Expected 201, got $HTTP_CODE"
        echo "DEBUG: Response body: $BODY"
    fi
    
    # Test 3: List work experiences (should have 1)
    print_test 3 "GET /resumes/work-experiences (with data)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/work-experiences" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 1 ]; then
            print_success "Found 1 work experience"
        else
            print_failure "Expected 1 work experience, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 4: Update work experience
    print_test 4 "PUT /resumes/work-experiences/{id} (update)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/resumes/work-experiences/$WORK_EXP_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"job_title\": \"Lead Software Engineer\"}")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        UPDATED_TITLE=$(echo $BODY | grep -o '"job_title":"[^"]*' | cut -d'"' -f4)
        if [ "$UPDATED_TITLE" == "Lead Software Engineer" ]; then
            print_success "Work experience updated"
        else
            print_failure "Title not updated correctly"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 5: Delete work experience
    print_test 5 "DELETE /resumes/work-experiences/{id}"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/resumes/work-experiences/$WORK_EXP_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 204 ]; then
        print_success "Work experience deleted"
    else
        print_failure "Expected 204, got $HTTP_CODE"
    fi
}

# =============================================================================
# EDUCATION TESTS
# =============================================================================

test_education_crud() {
    echo ""
    echo "=========================================="
    echo "Testing Education CRUD"
    echo "=========================================="
    
    # Test 6: List education (should be empty)
    print_test 6 "GET /resumes/education (empty list)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/education" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 0 ]; then
            print_success "Empty education list"
        else
            print_failure "Expected 0 education entries, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 7: Create education
    print_test 7 "POST /resumes/education (create)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/resumes/education" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"institution\": \"Stanford University\",
            \"degree_type\": \"bachelor\",
            \"field_of_study\": \"Computer Science\",
            \"location\": \"Stanford, CA\",
            \"start_date\": \"2012-09-01\",
            \"end_date\": \"2016-06-15\",
            \"gpa\": 3.85,
            \"honors\": [\"Summa Cum Laude\", \"Dean's List\"],
            \"activities\": [\"ACM President\", \"Hackathon Winner\"],
            \"display_order\": 0
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 201 ]; then
        EDUCATION_ID=$(echo $BODY | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        print_success "Education created: $EDUCATION_ID"
    else
        print_failure "Expected 201, got $HTTP_CODE"
    fi
    
    # Test 8: Update education
    print_test 8 "PUT /resumes/education/{id} (update)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/resumes/education/$EDUCATION_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"gpa\": 3.90}")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Education updated"
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 9: Delete education
    print_test 9 "DELETE /resumes/education/{id}"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/resumes/education/$EDUCATION_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 204 ]; then
        print_success "Education deleted"
    else
        print_failure "Expected 204, got $HTTP_CODE"
    fi
}

# =============================================================================
# SKILLS TESTS
# =============================================================================

test_skills_crud() {
    echo ""
    echo "=========================================="
    echo "Testing Skills CRUD"
    echo "=========================================="
    
    # Test 10: List skills (should be empty)
    print_test 10 "GET /resumes/skills (empty list)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/skills" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 0 ]; then
            print_success "Empty skills list"
        else
            print_failure "Expected 0 skills, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 11: Create skill
    print_test 11 "POST /resumes/skills (create)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/resumes/skills" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"skill_name\": \"Python\",
            \"category\": \"programming_language\",
            \"proficiency_level\": \"Expert\",
            \"years_of_experience\": 8,
            \"display_order\": 0
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 201 ]; then
        SKILL_ID=$(echo $BODY | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        print_success "Skill created: $SKILL_ID"
    else
        print_failure "Expected 201, got $HTTP_CODE"
    fi
    
    # Test 12: Create multiple skills
    print_test 12 "POST /resumes/skills (create multiple)"
    curl -s -X POST "$API_URL/resumes/skills" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"skill_name\": \"PostgreSQL\",
            \"category\": \"tool\",
            \"proficiency_level\": \"Advanced\",
            \"years_of_experience\": 5,
            \"display_order\": 1
        }" > /dev/null
    
    curl -s -X POST "$API_URL/resumes/skills" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"skill_name\": \"Docker\",
            \"category\": \"tool\",
            \"proficiency_level\": \"Intermediate\",
            \"years_of_experience\": 3,
            \"display_order\": 2
        }" > /dev/null
    
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/skills" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 3 ]; then
            print_success "Created multiple skills (total: 3)"
        else
            print_failure "Expected 3 skills, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 13: Update skill
    print_test 13 "PUT /resumes/skills/{id} (update)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/resumes/skills/$SKILL_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"proficiency_level\": \"Master\"}")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Skill updated"
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 14: Delete skill
    print_test 14 "DELETE /resumes/skills/{id}"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/resumes/skills/$SKILL_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 204 ]; then
        print_success "Skill deleted"
    else
        print_failure "Expected 204, got $HTTP_CODE"
    fi
}

# =============================================================================
# CERTIFICATIONS TESTS
# =============================================================================

test_certifications_crud() {
    echo ""
    echo "=========================================="
    echo "Testing Certifications CRUD"
    echo "=========================================="
    
    # Test 15: List certifications (should be empty)
    print_test 15 "GET /resumes/certifications (empty list)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/certifications" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        TOTAL=$(echo $BODY | grep -o '"total":[0-9]*' | cut -d':' -f2)
        if [ "$TOTAL" -eq 0 ]; then
            print_success "Empty certifications list"
        else
            print_failure "Expected 0 certifications, got $TOTAL"
        fi
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 16: Create certification
    print_test 16 "POST /resumes/certifications (create)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/resumes/certifications" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"$MASTER_RESUME_ID\",
            \"certification_name\": \"AWS Certified Solutions Architect\",
            \"issuing_organization\": \"Amazon Web Services\",
            \"issue_date\": \"2022-05-15\",
            \"expiration_date\": \"2025-05-15\",
            \"credential_id\": \"AWS-12345\",
            \"credential_url\": \"https://aws.amazon.com/verify/12345\",
            \"display_order\": 0
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    BODY=$(echo "$RESPONSE" | sed '$d')
    
    if [ "$HTTP_CODE" -eq 201 ]; then
        CERT_ID=$(echo $BODY | grep -o '"id":"[^"]*' | cut -d'"' -f4)
        print_success "Certification created: $CERT_ID"
    else
        print_failure "Expected 201, got $HTTP_CODE"
    fi
    
    # Test 17: Update certification
    print_test 17 "PUT /resumes/certifications/{id} (update)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT "$API_URL/resumes/certifications/$CERT_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{\"expiration_date\": \"2026-05-15\"}")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 200 ]; then
        print_success "Certification updated"
    else
        print_failure "Expected 200, got $HTTP_CODE"
    fi
    
    # Test 18: Delete certification
    print_test 18 "DELETE /resumes/certifications/{id}"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$API_URL/resumes/certifications/$CERT_ID" \
        -H "Authorization: Bearer $AUTH_TOKEN")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 204 ]; then
        print_success "Certification deleted"
    else
        print_failure "Expected 204, got $HTTP_CODE"
    fi
}

# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

test_error_handling() {
    echo ""
    echo "=========================================="
    echo "Testing Error Handling"
    echo "=========================================="
    
    # Test 19: Try to create work experience with invalid master_resume_id
    print_test 19 "POST /resumes/work-experiences (invalid master_resume_id)"
    RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_URL/resumes/work-experiences" \
        -H "Authorization: Bearer $AUTH_TOKEN" \
        -H "Content-Type: application/json" \
        -d "{
            \"master_resume_id\": \"00000000-0000-0000-0000-000000000000\",
            \"company_name\": \"Test Corp\",
            \"job_title\": \"Engineer\",
            \"start_date\": \"2020-01-01\"
        }")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 404 ]; then
        print_success "Rejected invalid master_resume_id (404)"
    else
        print_failure "Expected 404, got $HTTP_CODE"
    fi
    
    # Test 20: Try to access another user's work experience (create second user)
    print_test 20 "Access control test (different user)"
    
    # Create second user
    TEST_EMAIL2="test_resume_phase2_other_$(date +%s)@example.com"
    curl -s -X POST "$API_URL/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL2\",\"password\":\"$TEST_PASSWORD\",\"full_name\":\"Other User\"}" > /dev/null
    
    LOGIN_RESPONSE2=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL2\",\"password\":\"$TEST_PASSWORD\"}")
    AUTH_TOKEN2=$(echo $LOGIN_RESPONSE2 | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    
    # Try to access first user's work experiences
    RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_URL/resumes/work-experiences" \
        -H "Authorization: Bearer $AUTH_TOKEN2")
    HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
    
    if [ "$HTTP_CODE" -eq 404 ]; then
        print_success "Correctly blocked access to other user's data (404)"
    else
        print_failure "Expected 404, got $HTTP_CODE"
    fi
}

# =============================================================================
# CLEANUP
# =============================================================================

cleanup() {
    print_info "Cleaning up test data..."
    rm -f /tmp/test_resume_phase2.pdf
    print_success "Cleanup completed"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

echo "=========================================="
echo "Resume Management Phase 2 Tests"
echo "=========================================="
echo "Testing CRUD operations for:"
echo "  - Work Experiences"
echo "  - Education"
echo "  - Skills"
echo "  - Certifications"
echo "=========================================="
echo ""

# Run tests
setup_test_user
upload_test_resume
test_work_experience_crud
test_education_crud
test_skills_crud
test_certifications_crud
test_error_handling
cleanup

# Print summary
echo ""
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
