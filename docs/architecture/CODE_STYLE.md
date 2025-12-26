# Code Style & Quality Standards

**Project:** Personal AI Job Assistant  
**Date:** December 26, 2025

---

## Python (Backend)

### Tools

- **Formatter:** Black
- **Linter:** Ruff
- **Type Checker:** mypy
- **Security Scanner:** Bandit

### Configuration: `pyproject.toml`

```toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | venv
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"

# Enable specific rule sets
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "N",    # pep8-naming
    "ANN",  # flake8-annotations
    "S",    # flake8-bandit (security)
    "B",    # flake8-bugbear
    "C4",   # flake8-comprehensions
    "DTZ",  # flake8-datetimez
    "T10",  # flake8-debugger
    "EM",   # flake8-errmsg
    "ISC",  # flake8-implicit-str-concat
    "ICN",  # flake8-import-conventions
    "PIE",  # flake8-pie
    "PT",   # flake8-pytest-style
    "Q",    # flake8-quotes
    "RSE",  # flake8-raise
    "RET",  # flake8-return
    "SIM",  # flake8-simplify
    "TID",  # flake8-tidy-imports
    "ARG",  # flake8-unused-arguments
    "ERA",  # eradicate (commented code)
    "PL",   # pylint
    "RUF",  # ruff-specific rules
]

ignore = [
    "ANN101",  # Missing type annotation for self
    "ANN102",  # Missing type annotation for cls
    "ANN401",  # Dynamically typed expressions (Any)
]

[tool.ruff.per-file-ignores]
"__init__.py" = ["F401"]  # Allow unused imports in __init__
"tests/*" = ["S101", "ANN"]  # Allow assert in tests, skip annotations

[tool.ruff.isort]
known-first-party = ["app"]
combine-as-imports = true

[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true
warn_no_return = true
warn_unreachable = true
strict_equality = true

# Per-module options
[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false

[tool.bandit]
exclude_dirs = ["tests", "venv"]
skips = ["B101"]  # Skip assert_used (needed in tests)
```

### Pre-commit Hooks: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
        args: [--strict]

  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.5
    hooks:
      - id: bandit
        args: [-c, pyproject.toml]
        additional_dependencies: ["bandit[toml]"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-json
      - id: check-merge-conflict
      - id: detect-private-key
```

### Example Code Style

```python
"""Module for resume parsing functionality."""
from typing import Optional
from pathlib import Path

from app.schemas.resume import Resume, WorkExperience
from app.core.exceptions import InvalidFileTypeError


class ResumeParser:
    """Parse resumes from PDF and DOCX files."""

    SUPPORTED_EXTENSIONS = {".pdf", ".docx"}

    def __init__(self, *, max_file_size_mb: int = 10) -> None:
        """Initialize resume parser.

        Args:
            max_file_size_mb: Maximum file size in megabytes.
        """
        self.max_file_size = max_file_size_mb * 1024 * 1024

    def parse(self, file_path: Path) -> Resume:
        """Parse resume from file.

        Args:
            file_path: Path to resume file.

        Returns:
            Parsed resume object.

        Raises:
            InvalidFileTypeError: If file type is not supported.
            FileSizeError: If file exceeds maximum size.
        """
        if file_path.suffix.lower() not in self.SUPPORTED_EXTENSIONS:
            raise InvalidFileTypeError(
                f"Unsupported file type: {file_path.suffix}"
            )

        # Implementation...
        return self._parse_pdf(file_path)

    def _parse_pdf(self, file_path: Path) -> Resume:
        """Parse PDF resume."""
        # Implementation...
        pass
```

---

## TypeScript/JavaScript (Frontend & Extension)

### Tools

- **Formatter:** Prettier
- **Linter:** ESLint
- **Type Checker:** TypeScript compiler

### ESLint Configuration: `.eslintrc.json`

```json
{
  "root": true,
  "env": {
    "browser": true,
    "es2022": true,
    "node": true
  },
  "extends": [
    "airbnb",
    "airbnb-typescript",
    "airbnb/hooks",
    "plugin:@typescript-eslint/recommended",
    "plugin:@typescript-eslint/recommended-requiring-type-checking",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2022,
    "sourceType": "module",
    "project": "./tsconfig.json",
    "ecmaFeatures": {
      "jsx": true
    }
  },
  "plugins": [
    "react",
    "react-hooks",
    "@typescript-eslint",
    "import"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react/jsx-props-no-spreading": "off",
    "import/prefer-default-export": "off",
    "import/order": [
      "error",
      {
        "groups": [
          "builtin",
          "external",
          "internal",
          "parent",
          "sibling",
          "index"
        ],
        "newlines-between": "always",
        "alphabetize": {
          "order": "asc",
          "caseInsensitive": true
        }
      }
    ],
    "@typescript-eslint/explicit-function-return-type": [
      "error",
      {
        "allowExpressions": true
      }
    ],
    "@typescript-eslint/no-unused-vars": [
      "error",
      {
        "argsIgnorePattern": "^_"
      }
    ],
    "@typescript-eslint/naming-convention": [
      "error",
      {
        "selector": "interface",
        "format": ["PascalCase"],
        "prefix": ["I"]
      },
      {
        "selector": "typeAlias",
        "format": ["PascalCase"]
      }
    ]
  },
  "settings": {
    "react": {
      "version": "detect"
    }
  }
}
```

### Prettier Configuration: `.prettierrc`

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "useTabs": false,
  "arrowParens": "always",
  "endOfLine": "lf",
  "bracketSpacing": true,
  "jsxSingleQuote": false,
  "jsxBracketSameLine": false
}
```

### TypeScript Configuration: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "allowJs": false,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "allowSyntheticDefaultImports": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "types": ["vite/client", "@testing-library/jest-dom"],
    
    /* Strict Type-Checking Options */
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist", "build"]
}
```

### Example Code Style

```typescript
/**
 * Hook for managing resume data and operations.
 */
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { resumeApi } from '@/api/resume';
import type { IResume, IResumeVersion } from '@/types/resume';

interface UseResumeOptions {
  onSuccess?: (data: IResume) => void;
  onError?: (error: Error) => void;
}

export const useResume = (
  resumeId: string,
  options?: UseResumeOptions
): UseResumeResult => {
  const queryClient = useQueryClient();

  const { data, isLoading, error } = useQuery({
    queryKey: ['resume', resumeId],
    queryFn: () => resumeApi.getById(resumeId),
    enabled: Boolean(resumeId),
  });

  const { mutateAsync: tailorResume } = useMutation({
    mutationFn: (jobId: string) => resumeApi.tailor(resumeId, jobId),
    onSuccess: (newVersion) => {
      queryClient.invalidateQueries({ queryKey: ['resume', resumeId] });
      options?.onSuccess?.(newVersion);
    },
    onError: options?.onError,
  });

  return {
    resume: data,
    isLoading,
    error,
    tailorResume,
  };
};

interface UseResumeResult {
  resume: IResume | undefined;
  isLoading: boolean;
  error: Error | null;
  tailorResume: (jobId: string) => Promise<IResumeVersion>;
}
```

---

## Git Commit Convention

### Conventional Commits

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring (no functional change)
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `build`: Build system or dependencies
- `ci`: CI/CD configuration changes
- `chore`: Other changes (maintenance, etc.)

### Examples

```
feat(resume): add PDF parsing support

Implement PDF text extraction using PyPDF2.
Supports multi-column layouts and handles embedded images.

Closes #42

---

fix(auth): prevent session timeout during active use

Update session expiry logic to extend timeout on user activity.

Fixes #103

---

docs(api): update resume API endpoint documentation

Add examples for resume tailoring endpoint.
Include error response formats.

---

test(backend): add unit tests for resume parser

- Test PDF parsing
- Test DOCX parsing
- Test date extraction
- Test email validation

Coverage increased to 87% (+5%)
```

---

## VS Code Settings

### `.vscode/settings.json`

```json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true,
    "source.organizeImports": true
  },
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": false,
  "python.linting.mypyEnabled": true,
  "python.linting.banditEnabled": true,
  "python.testing.pytestEnabled": true,
  "python.testing.unittestEnabled": false,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[json]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

### `.vscode/extensions.json`

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.mypy-type-checker",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss",
    "dsznajder.es7-react-js-snippets"
  ]
}
```

---

## Documentation Standards

### Python Docstrings

Use **Google Style** docstrings:

```python
def process_resume(
    file_path: Path,
    *,
    parse_images: bool = False,
    extract_skills: bool = True
) -> Resume:
    """Process and parse a resume file.

    Args:
        file_path: Path to the resume file.
        parse_images: Whether to extract images from the resume.
        extract_skills: Whether to extract skills section.

    Returns:
        Parsed resume object with structured data.

    Raises:
        InvalidFileTypeError: If the file type is not supported.
        FileSizeError: If the file exceeds maximum size limit.

    Example:
        >>> resume = process_resume(Path("resume.pdf"))
        >>> print(resume.full_name)
        'John Doe'
    """
```

### TypeScript JSDoc

```typescript
/**
 * Tailor a resume for a specific job posting.
 *
 * @param resumeId - The ID of the master resume
 * @param jobId - The ID of the job posting
 * @param options - Optional configuration for tailoring
 * @returns A promise that resolves to the tailored resume version
 * @throws {APIError} If the API request fails
 *
 * @example
 * ```typescript
 * const tailored = await tailorResume('resume-123', 'job-456');
 * console.log(tailored.version_name);
 * ```
 */
export async function tailorResume(
  resumeId: string,
  jobId: string,
  options?: TailorOptions
): Promise<ResumeVersion> {
  // Implementation...
}
```

---

## Code Review Checklist

### General

- [ ] Code follows style guide (Black/Prettier formatted)
- [ ] No linting errors or warnings
- [ ] Type hints/annotations present
- [ ] Meaningful variable and function names
- [ ] No commented-out code
- [ ] No debug print statements

### Testing

- [ ] Unit tests added for new functionality
- [ ] All tests passing locally
- [ ] Coverage maintained above 80%
- [ ] Edge cases tested

### Security

- [ ] No hardcoded credentials or secrets
- [ ] Input validation implemented
- [ ] SQL injection prevention (parameterized queries)
- [ ] XSS prevention (sanitized outputs)
- [ ] CSRF protection (for forms)

### Documentation

- [ ] Public APIs documented
- [ ] README updated if needed
- [ ] CHANGELOG updated
- [ ] Complex logic explained with comments

---

## Setup Instructions

### Backend Setup

```bash
cd src/backend

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Run checks manually
black .
ruff . --fix
mypy app/
bandit -r app/

# Run tests
pytest
```

### Frontend Setup

```bash
cd src/frontend

# Install dependencies
npm install

# Run linting
npm run lint
npm run lint:fix

# Run type checking
npm run type-check

# Run formatting
npm run format
```

---

## Continuous Integration

All checks run automatically on push/PR via GitHub Actions:

1. **Linting** - Black, Ruff, ESLint
2. **Type Checking** - mypy, tsc
3. **Security** - Bandit, npm audit
4. **Tests** - pytest, vitest
5. **Coverage** - Codecov (80% minimum)

PRs cannot be merged until all checks pass.

---

## Next Steps

1. ✅ Review code style standards
2. ⏳ Install pre-commit hooks
3. ⏳ Configure IDE settings
4. ⏳ Set up linting in CI/CD
5. ⏳ Create code review template
