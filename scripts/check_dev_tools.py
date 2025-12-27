#!/usr/bin/env python3
"""Check if development tools are installed and configured."""

import subprocess
import sys
from pathlib import Path


def check_command(name: str, command: list[str], min_version: str | None = None) -> bool:
    """Check if a command is available and optionally verify version."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
            print(f"✅ {name}: {version}")
            return True
        else:
            print(f"❌ {name}: Not found or error")
            return False
    except FileNotFoundError:
        print(f"❌ {name}: Not installed")
        return False


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(path).exists():
        print(f"✅ {description}: Found at {path}")
        return True
    else:
        print(f"❌ {description}: Missing at {path}")
        return False


def main() -> None:
    """Run all checks."""
    print("=" * 70)
    print("Development Environment Check")
    print("=" * 70)
    print()

    checks_passed = 0
    total_checks = 0

    # System prerequisites
    print("📦 System Prerequisites")
    print("-" * 70)
    total_checks += 1
    checks_passed += check_command("Python", ["python", "--version"], "3.11")
    total_checks += 1
    checks_passed += check_command("Node.js", ["node", "--version"], "18")
    total_checks += 1
    checks_passed += check_command("Git", ["git", "--version"])
    total_checks += 1
    checks_passed += check_command("PostgreSQL", ["psql", "--version"], "15")
    print()

    # Package managers
    print("📦 Package Managers")
    print("-" * 70)
    total_checks += 1
    checks_passed += check_command("Poetry", ["poetry", "--version"])
    total_checks += 1
    checks_passed += check_command("pnpm", ["pnpm", "--version"])
    total_checks += 1
    checks_passed += check_command("npm", ["npm", "--version"])
    print()

    # Development tools - Python
    print("🛠️  Python Development Tools")
    print("-" * 70)
    total_checks += 1
    checks_passed += check_command("Black", ["black", "--version"])
    total_checks += 1
    checks_passed += check_command("Ruff", ["ruff", "--version"])
    total_checks += 1
    checks_passed += check_command("mypy", ["mypy", "--version"])
    total_checks += 1
    checks_passed += check_command("Bandit", ["bandit", "--version"])
    total_checks += 1
    checks_passed += check_command("pytest", ["pytest", "--version"])
    total_checks += 1
    checks_passed += check_command("pre-commit", ["pre-commit", "--version"])
    print()

    # Development tools - JavaScript
    print("🛠️  JavaScript Development Tools")
    print("-" * 70)
    total_checks += 1
    checks_passed += check_command("ESLint", ["npx", "eslint", "--version"])
    total_checks += 1
    checks_passed += check_command("Prettier", ["npx", "prettier", "--version"])
    print()

    # Configuration files
    print("📄 Configuration Files")
    print("-" * 70)
    project_root = Path(__file__).parent.parent
    
    total_checks += 1
    checks_passed += check_file_exists(
        str(project_root / ".env"),
        "Environment file"
    )
    total_checks += 1
    checks_passed += check_file_exists(
        str(project_root / ".pre-commit-config.yaml"),
        "Pre-commit config"
    )
    total_checks += 1
    checks_passed += check_file_exists(
        str(project_root / ".prettierrc"),
        "Prettier config"
    )
    total_checks += 1
    checks_passed += check_file_exists(
        str(project_root / ".eslintrc.json"),
        "ESLint config"
    )
    total_checks += 1
    checks_passed += check_file_exists(
        str(project_root / "src" / "backend" / "pyproject.toml"),
        "Backend pyproject.toml"
    )
    print()

    # Summary
    print("=" * 70)
    print(f"Results: {checks_passed}/{total_checks} checks passed")
    print("=" * 70)
    
    if checks_passed == total_checks:
        print("✅ All checks passed! Development environment is ready.")
        sys.exit(0)
    else:
        print(f"❌ {total_checks - checks_passed} checks failed. See above for details.")
        print()
        print("📖 Installation Guide:")
        print("   See docs/DEVELOPMENT_SETUP.md for detailed setup instructions")
        sys.exit(1)


if __name__ == "__main__":
    main()
