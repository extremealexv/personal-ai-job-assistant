#!/bin/bash
# Test AI Cover Letter Generation Endpoint

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 Setting up test data...${NC}"

# Get user token
if [ -z "$TOKEN" ]; then
    echo "Getting authentication token..."
    TOKEN=$(curl -s -X POST 'http://localhost:8000/api/v1/auth/login' \
      -H 'Content-Type: application/json' \
      -d '{
        "email": "user@example.com",
        "password": "password123"
      }' | jq -r '.access_token')
    export TOKEN
fi

echo -e "${GREEN}✅ Using existing TOKEN${NC}"

# Get resume ID
RESUME_ID=$(curl -s 'http://localhost:8000/api/v1/resumes' \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id // empty')

if [ -z "$RESUME_ID" ] || [ "$RESUME_ID" = "null" ]; then
    echo -e "${RED}❌ No resume found. Please create a master resume first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Resume ID: $RESUME_ID${NC}"

# Get job ID
JOB_ID=$(curl -s 'http://localhost:8000/api/v1/jobs?limit=1' \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id // empty')

if [ -z "$JOB_ID" ] || [ "$JOB_ID" = "null" ]; then
    echo -e "${RED}❌ No job found. Please create a job posting first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Job ID: $JOB_ID${NC}"

# Check if application exists
APPLICATION_ID=$(curl -s "http://localhost:8000/api/v1/applications?job_id=$JOB_ID" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.items[0].id // empty')

if [ -z "$APPLICATION_ID" ] || [ "$APPLICATION_ID" = "null" ]; then
    echo -e "${BLUE}📝 Creating application...${NC}"
    
    # First, create a tailored resume version
    echo "Creating tailored resume version..."
    RESUME_VERSION_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/v1/ai/resume/tailor' \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "{
        \"master_resume_id\": \"$RESUME_ID\",
        \"job_posting_id\": \"$JOB_ID\",
        \"version_name\": \"AI Tailored for Cover Letter Test\"
      }")
    
    RESUME_VERSION=$(echo "$RESUME_VERSION_RESPONSE" | jq -r '.id // empty')
    
    if [ -z "$RESUME_VERSION" ] || [ "$RESUME_VERSION" = "null" ]; then
        echo -e "${RED}❌ Failed to create resume version${NC}"
        echo "Response: $RESUME_VERSION_RESPONSE"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Created resume version: $RESUME_VERSION${NC}"
    
    # Wait for resume version to be committed
    sleep 2
    
    # Create application
    echo "Creating application..."
    APPLICATION_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/v1/applications' \
      -H "Authorization: Bearer $TOKEN" \
      -H 'Content-Type: application/json' \
      -d "{
        \"job_posting_id\": \"$JOB_ID\",
        \"resume_version_id\": \"$RESUME_VERSION\",
        \"status\": \"draft\"
      }")
    
    APPLICATION_ID=$(echo "$APPLICATION_RESPONSE" | jq -r '.id // empty')
    
    if [ -z "$APPLICATION_ID" ] || [ "$APPLICATION_ID" = "null" ]; then
        echo -e "${RED}❌ Failed to create application${NC}"
        echo "Response: $APPLICATION_RESPONSE"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Created application: $APPLICATION_ID${NC}"
else
    echo -e "${GREEN}✅ Using existing application: $APPLICATION_ID${NC}"
fi

echo ""
echo -e "${BLUE}🤖 Testing AI Cover Letter Generation Endpoint...${NC}"
echo "================================================"

# Test cover letter generation
curl -X POST 'http://localhost:8000/api/v1/ai/cover-letter/generate' \
  -H "Authorization: Bearer $TOKEN" \
  -H 'Content-Type: application/json' \
  -d "{
    \"application_id\": \"$APPLICATION_ID\"
  }" | jq '.'

echo ""
echo "================================================"
echo ""
echo -e "${BLUE}📋 Checking created cover letters...${NC}"

curl -s "http://localhost:8000/api/v1/cover-letters?application_id=$APPLICATION_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.items[] | {
    id: .id,
    version: .version_number,
    is_active: .is_active,
    ai_model: .ai_model_used,
    generation_timestamp: .generation_timestamp,
    content_preview: .content[:200]
  }'
