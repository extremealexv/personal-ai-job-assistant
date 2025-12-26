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
