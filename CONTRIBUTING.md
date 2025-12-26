# Contributing to Personal AI Job Search Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 🎯 Project Goals

This is a **personal project** focused on building an intelligent job search assistant. While it's designed for single-user use, we welcome contributions that:

- Improve code quality and maintainability
- Add new ATS platform support
- Enhance AI prompt engineering
- Fix bugs and security issues
- Improve documentation

## 📋 Before You Start

1. **Check existing issues** - Look for related issues or discussions
2. **Create an issue** - Describe your proposed change before starting work
3. **Wait for feedback** - Get alignment before investing significant effort
4. **Follow conventions** - Adhere to code style and architectural patterns

## 🔧 Development Setup

### Prerequisites

- Node.js >= 18.x
- Python >= 3.11
- PostgreSQL >= 15
- Git

### Local Environment

```bash
# Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/personal-ai-job-assistant.git
cd personal-ai-job-assistant

# Create a feature branch
git checkout -b feature/your-feature-name

# Install dependencies
# (See README.md for detailed instructions)

# Set up pre-commit hooks
pip install pre-commit
pre-commit install
```

## 📝 Development Workflow

### 1. Create an Issue

Before starting work, create an issue describing:
- **Problem**: What issue are you solving?
- **Solution**: How do you propose to solve it?
- **Alternatives**: What other approaches did you consider?

### 2. Branch Naming

Use descriptive branch names:
- `feature/add-workday-support` - New features
- `fix/resume-parser-crash` - Bug fixes
- `docs/api-documentation` - Documentation
- `refactor/auth-module` - Code refactoring

### 3. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Workday ATS detection
fix: resolve resume parser encoding issue
docs: update API documentation
refactor: simplify authentication flow
test: add cover letter generation tests
```

### 4. Code Style

**Python (Backend)**
- Follow PEP 8
- Use type hints
- Maximum line length: 100 characters
- Format with `black`
- Lint with `ruff`

**TypeScript/JavaScript (Frontend & Extension)**
- Use ESLint configuration
- Format with Prettier
- Use TypeScript strict mode
- Follow Airbnb style guide

### 5. Testing

All changes must include tests:

**Backend**
```bash
cd src/backend
pytest tests/
```

**Frontend**
```bash
cd src/frontend
npm run test
```

**Extension**
```bash
cd src/extension
npm run test
```

### 6. Documentation

Update documentation for:
- New features
- API changes
- Configuration options
- Breaking changes

### 7. Pull Request Process

1. **Update your branch**
   ```bash
   git fetch origin
   git rebase origin/develop
   ```

2. **Run tests locally**
   ```bash
   # Run all test suites
   ./scripts/run-tests.sh
   ```

3. **Create Pull Request**
   - Use the PR template
   - Link related issues
   - Provide clear description
   - Include screenshots (if UI change)
   - Mark as draft if work in progress

4. **Code Review**
   - Address feedback promptly
   - Keep discussions professional
   - Update PR as needed

5. **Merge**
   - Squash commits for clean history
   - Delete branch after merge

## 🏷️ Issue Labels

- `bug` - Something isn't working
- `feature` - New functionality
- `enhancement` - Improvement to existing feature
- `documentation` - Documentation improvements
- `security` - Security-related issues
- `ats-support` - ATS platform integration
- `ai-prompts` - AI prompt engineering
- `good-first-issue` - Good for newcomers
- `help-wanted` - Extra attention needed

## 🔒 Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead:
1. Email: security@example.com
2. Include:
   - Description of vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

## 📋 Functional Requirements

All contributions must align with [REQUIREMENTS.md](./REQUIREMENTS.md). If your change requires modifying requirements:

1. Propose requirement change in an issue first
2. Get approval before implementation
3. Update REQUIREMENTS.md in the same PR

## ✅ Checklist for PRs

- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
- [ ] Linked to related issue(s)

## 🎨 Component-Specific Guidelines

### Backend API
- Use FastAPI/Flask best practices
- Implement proper error handling
- Add OpenAPI documentation
- Validate all inputs
- Use async where appropriate

### Frontend
- Follow React best practices
- Implement responsive design
- Add accessibility features
- Optimize bundle size
- Use proper state management

### Browser Extension
- Minimize permissions requested
- Handle CSP restrictions
- Support both Chrome and Edge
- Test on multiple ATS platforms
- Maintain manifest v3 compatibility

## 🤝 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome diverse perspectives
- Accept constructive criticism
- Focus on what's best for the project
- Show empathy towards others

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information
- Other unprofessional conduct

## 📞 Questions?

- **General**: Create a [Discussion](../../discussions)
- **Bugs**: Create an [Issue](../../issues)
- **Security**: Email security@example.com

## 🙏 Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort!

---

**Happy Coding!** 🚀