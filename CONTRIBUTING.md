# Contributing to Personal AI Job Assistant

Thank you for your interest in contributing to the Personal AI Job Assistant! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How Can I Contribute?

### Reporting Bugs

If you find a bug, please create an issue using the Bug Report template. Include:
- A clear description of the bug
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (OS, browser, version)
- Screenshots if applicable

### Suggesting Features

Feature requests are welcome! Please use the Feature Request template and include:
- A clear description of the feature
- The problem it solves
- Potential implementation approach
- Any alternatives you've considered

### Submitting Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for your changes if applicable
4. **Update documentation** as needed
5. **Ensure all tests pass** before submitting
6. **Submit a pull request** using the PR template

## Development Setup

### Prerequisites

- Node.js (version TBD)
- npm or yarn
- Git

### Getting Started

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/personal-ai-job-assistant.git

# Navigate to the project directory
cd personal-ai-job-assistant

# Install dependencies
npm install

# Run tests
npm test

# Start development server
npm run dev
```

## Coding Standards

### General Guidelines

- Write clear, self-documenting code
- Add comments for complex logic
- Follow the existing code style
- Keep functions small and focused
- Use meaningful variable and function names

### JavaScript/TypeScript

- Use ES6+ features
- Prefer `const` over `let`, avoid `var`
- Use async/await over promises when possible
- Follow Prettier formatting rules

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters
- Reference issues and pull requests when relevant

Example:
```
Add resume parsing functionality

- Implement PDF parsing
- Add text extraction
- Create data structure for parsed content

Fixes #123
```

### Branch Naming

- Feature branches: `feature/description`
- Bug fixes: `fix/description`
- Documentation: `docs/description`
- Refactoring: `refactor/description`

## Testing

- Write unit tests for new functionality
- Ensure all existing tests pass
- Aim for high code coverage
- Test edge cases and error conditions

## Documentation

- Update README.md if you change functionality
- Document new features in the appropriate docs/ directory
- Add JSDoc comments for public APIs
- Update CHANGELOG.md with your changes

## Review Process

1. A maintainer will review your pull request
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be included in the next release

## Project Structure

```
personal-ai-job-assistant/
├── .github/          # GitHub templates and workflows
├── docs/             # Documentation
├── src/              # Source code
│   ├── backend/      # Backend services
│   ├── frontend/     # Frontend application
│   ├── extension/    # Browser extension
│   └── shared/       # Shared utilities
├── tests/            # Test files
└── ...
```

## Getting Help

- Check existing issues and documentation
- Ask questions in issue comments
- Reach out to maintainers if needed

## Recognition

Contributors will be acknowledged in the project README and release notes.

## License

By contributing to this project, you agree that your contributions will be licensed under the project's license.

Thank you for contributing to Personal AI Job Assistant!
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
