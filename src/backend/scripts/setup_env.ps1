# PowerShell Setup Script for Environment Configuration
# Run this after cloning the repository

$ErrorActionPreference = "Stop"

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Personal AI Job Assistant - Environment Setup" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env already exists
$envPath = "..\..\..\.env"
if (Test-Path $envPath) {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
    $response = Read-Host "Do you want to overwrite it? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Keeping existing .env file"
        exit 0
    }
}

# Copy template
Write-Host "📝 Creating .env file from template..." -ForegroundColor Green
Copy-Item "..\..\..\.env.example" $envPath

# Generate SECRET_KEY
Write-Host "🔐 Generating SECRET_KEY..." -ForegroundColor Green
$secretKey = python -c "import secrets; print(secrets.token_urlsafe(32))"
(Get-Content $envPath) -replace "generate-with-python-secrets-token-urlsafe-32", $secretKey | Set-Content $envPath

# Generate ENCRYPTION_KEY
Write-Host "🔐 Generating ENCRYPTION_KEY..." -ForegroundColor Green
$encryptionKey = python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
(Get-Content $envPath) -replace "generate-with-fernet-generate-key", $encryptionKey | Set-Content $envPath

Write-Host ""
Write-Host "✅ Environment file created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "⚠️  IMPORTANT: You still need to configure:" -ForegroundColor Yellow
Write-Host "   1. Database credentials (DATABASE_URL)"
Write-Host "   2. OpenAI API key (OPENAI_API_KEY)"
Write-Host "   3. Gmail/Calendar OAuth credentials (optional)"
Write-Host ""
Write-Host "Edit .env file to add your credentials:"
Write-Host "   notepad $envPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Then test your configuration:"
Write-Host "   cd src\backend" -ForegroundColor Cyan
Write-Host "   python scripts\test_config.py" -ForegroundColor Cyan
