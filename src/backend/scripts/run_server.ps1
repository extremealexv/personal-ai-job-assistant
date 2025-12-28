# Start the FastAPI development server
# PowerShell script for Windows

Write-Host "🚀 Starting FastAPI Development Server" -ForegroundColor Blue
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "app\main.py")) {
    Write-Host "❌ Error: Must run from src\backend directory" -ForegroundColor Red
    exit 1
}

# Start the server
Write-Host "Starting server at http://localhost:8000" -ForegroundColor Green
Write-Host "API docs at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""

poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
