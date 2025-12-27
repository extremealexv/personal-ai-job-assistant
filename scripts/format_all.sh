#!/bin/bash
# Format all code using configured formatters

echo "Formatting all code..."
echo ""

# Backend - Black
echo "Formatting Python code with Black..."
cd src/backend
poetry run black app/ database/ scripts/ || echo "Black formatting completed with changes"
cd ../..
echo ""

# Backend - Ruff auto-fix
echo "Auto-fixing Python issues with Ruff..."
cd src/backend
poetry run ruff check app/ database/ scripts/ --fix || echo "Ruff auto-fix completed"
cd ../..
echo ""

# Frontend - Prettier
echo "Formatting TypeScript/JavaScript with Prettier..."
cd src/frontend
pnpm prettier --write "src/**/*.{ts,tsx,js,jsx,json,css,md}" || echo "Prettier formatting completed"
cd ../..
echo ""

# Root level - Prettier
echo "Formatting root configuration files..."
npx prettier --write "*.{json,md,yaml,yml}" ".*.{json,yaml,yml}" || echo "Root files formatted"
echo ""

echo "✓ All formatting complete!"
echo "Review changes with: git diff"
echo "Commit with: git add . && git commit -m 'style: format code'"
