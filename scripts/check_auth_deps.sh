#!/bin/bash
# Check if required dependencies are installed

echo "Checking authentication dependencies..."
echo ""

python3 << 'EOF'
import sys

deps = {
    "jose": "python-jose",
    "passlib": "passlib",
    "bcrypt": "bcrypt"
}

missing = []
for module, package in deps.items():
    try:
        __import__(module)
        print(f"✓ {package} is installed")
    except ImportError:
        print(f"✗ {package} is NOT installed")
        missing.append(package)

if missing:
    print("\n❌ Missing dependencies:")
    print(f"   pip install {' '.join(missing)}")
    sys.exit(1)
else:
    print("\n✅ All authentication dependencies are installed!")
    
    # Test bcrypt specifically
    try:
        import bcrypt
        test_hash = bcrypt.hashpw(b"test", bcrypt.gensalt())
        print(f"✓ bcrypt working correctly")
    except Exception as e:
        print(f"✗ bcrypt error: {e}")
        sys.exit(1)
EOF
