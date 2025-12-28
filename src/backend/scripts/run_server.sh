#!/bin/bash
# Start the FastAPI development server

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting FastAPI Development Server${NC}"
echo ""

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Must run from src/backend directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated. Activating..."
    poetry shell
fi

# Start the server
echo -e "${GREEN}Starting server at http://localhost:8000${NC}"
echo -e "${GREEN}API docs at http://localhost:8000/docs${NC}"
echo ""

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
