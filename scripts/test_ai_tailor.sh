#!/bin/bash

# Test AI Resume Tailoring Endpoint
# Run this on your VPS where the backend server is running

echo "🔍 Setting up test data..."

# Set the job ID from your database query
JOB_ID="33176128-a18c-4675-95fd-607e1f7b6e5d"

# Get the resume ID from database (use default peer authentication)
RESUME_ID=$(psql -d ai_job_assistant -t -c "SELECT id FROM master_resumes WHERE deleted_at IS NULL LIMIT 1;" | xargs)

if [ -z "$RESUME_ID" ]; then
    echo "❌ No resume found in database"
    exit 1
fi

echo "✅ Resume ID: $RESUME_ID"
echo "✅ Job ID: $JOB_ID"

# Get auth token (assuming you have test user credentials)
if [ -z "$TOKEN" ]; then
    echo "🔐 Getting auth token..."
    TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"email": "user@example.com", "password": "securepassword123"}' | jq -r '.access_token')
    
    if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
        echo "❌ Failed to get auth token"
        exit 1
    fi
    echo "✅ Auth token obtained"
fi

echo ""
echo "🤖 Testing AI Resume Tailoring Endpoint..."
echo "================================================"
echo ""

# Call the AI tailoring endpoint
curl -X POST "http://localhost:8000/api/v1/ai/resume/tailor" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"master_resume_id\": \"$RESUME_ID\",
    \"job_posting_id\": \"$JOB_ID\",
    \"version_name\": \"AI Tailored - TechCorp Backend Engineer\"
  }" | jq '.'

echo ""
echo "================================================"

# Verify the resume version was created
echo ""
echo "📋 Checking created resume versions..."
curl -s "http://localhost:8000/api/v1/resumes/versions?master_resume_id=$RESUME_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data[] | {id: .id, version_name: .version_name, created_at: .created_at}'
