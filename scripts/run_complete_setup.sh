#!/bin/bash
# Run this on your Linux server to execute all setup steps in order

set -e

echo "================================================================"
echo "Personal AI Job Assistant - Complete Setup Script"
echo "================================================================"
echo ""
echo "This script will guide you through the complete setup process."
echo "Press Ctrl+C at any time to cancel."
echo ""

read -p "Have you edited the .env file with your database credentials? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Please run: ./src/backend/scripts/setup_env.sh"
    echo "Then edit .env and run this script again."
    exit 1
fi

echo ""
echo "Step 1/5: Installing Development Tools"
echo "----------------------------------------------------------------"
./scripts/install_dev_tools.sh

echo ""
echo "Step 2/5: Setting up Pre-commit Hooks"
echo "----------------------------------------------------------------"
./scripts/setup_pre_commit.sh

echo ""
echo "Step 3/5: Initializing Database"
echo "----------------------------------------------------------------"
cd src/backend
poetry run python database/init_db.py --drop --seed
cd ../..

echo ""
echo "Step 4/5: Running Quick Check"
echo "----------------------------------------------------------------"
./scripts/quick_check.sh

echo ""
echo "Step 5/5: Testing Pre-commit Hooks"
echo "----------------------------------------------------------------"
pre-commit run --all-files || echo "Some hooks made changes - this is normal"

echo ""
echo "================================================================"
echo "✓ Setup Complete!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "  1. Review the changes made by pre-commit"
echo "  2. Run: ./scripts/test_dev_tools.sh"
echo "  3. Test a commit to verify hooks work automatically"
echo ""
echo "Start development:"
echo "  Backend:  cd src/backend && poetry shell && uvicorn app.main:app --reload"
echo "  Frontend: cd src/frontend && pnpm dev"
echo ""
