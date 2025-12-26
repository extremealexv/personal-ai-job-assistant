# Personal AI Job Search Assistant

> An intelligent job application management system with AI-powered resume tailoring and browser automation

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: In Development](https://img.shields.io/badge/Status-In%20Development-blue)]()

## 📋 Overview

The Personal AI Job Search Assistant is a comprehensive system designed to streamline the job application process for software engineers. It combines AI-powered content generation with browser automation to help you:

- **Manage** job postings and applications in one place
- **Optimize** resumes and cover letters for specific roles
- **Automate** form filling and application submission
- **Track** application status and interview scheduling
- **Analyze** performance metrics to improve success rates

## 🎯 Key Features

- **Smart Resume Tailoring** - AI-powered resume optimization for each job posting
- **Cover Letter Generation** - Customized, executive-level cover letters
- **Browser Extension** - Autofill and submit applications on major ATS platforms
- **Email Integration** - Automatic tracking via Gmail integration
- **Calendar Sync** - Interview scheduling with Google Calendar
- **Analytics Dashboard** - Track metrics and optimize your approach

## 🏗️ Architecture

This project consists of three main components:

1. **Backend API** - Core business logic, AI integration, data management
2. **Web Application** - Desktop interface for job and application management
3. **Browser Extension** - Chrome/Edge extension for ATS integration

## 📚 Documentation

- **[Functional Requirements](./FUNCTIONAL_REQUIREMENTS.md)** - Detailed system specifications (FR-1 through FR-18)
- **[Non-Functional Requirements](./NON_FUNCTIONAL_REQUIREMENTS.md)** - Performance, security, and quality requirements
- [Architecture Documentation](./docs/architecture/) - System design and diagrams
- [API Documentation](./docs/api/) - API endpoints and integration guides
- [Contributing Guidelines](./CONTRIBUTING.md) - How to contribute to the project

## 🚀 Getting Started

### Prerequisites

- Node.js >= 18.x
- Python >= 3.11
- PostgreSQL >= 15
- Docker (optional, for containerized development)

### Installation

```bash
# Clone the repository
git clone https://github.com/extremealexv/personal-ai-job-assistant.git
cd personal-ai-job-assistant

# Install backend dependencies
cd src/backend
pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend
npm install

# Install extension dependencies
cd ../extension
npm install
```

### Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit configuration
# Add your API keys, database credentials, etc.
```

### Running Locally

```bash
# Start backend
cd src/backend
python manage.py runserver

# Start frontend (in new terminal)
cd src/frontend
npm run dev

# Load extension
# 1. Open Chrome/Edge
# 2. Navigate to chrome://extensions
# 3. Enable Developer Mode
# 4. Click "Load unpacked"
# 5. Select src/extension directory
```

## 🗺️ Roadmap

See our [Project Board](../../projects) for current development status.

### Phase 1: Foundation (Current)
- [ ] Core backend API
- [ ] Database schema
- [ ] Authentication system
- [ ] Resume parser

### Phase 2: AI Integration
- [ ] Resume tailoring engine
- [ ] Cover letter generation
- [ ] Prompt management system

### Phase 3: Browser Extension
- [ ] ATS detection
- [ ] Form autofill
- [ ] Submission automation

### Phase 4: Integrations
- [ ] Gmail integration
- [ ] Google Calendar sync
- [ ] Email classification

### Phase 5: Analytics & Optimization
- [ ] Performance metrics
- [ ] AI learning feedback loop
- [ ] Resume version optimization

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 🔒 Security

This application handles sensitive personal information. Please review our [Security Policy](./SECURITY.md) before contributing or deploying.

For security concerns, please email: security@example.com

## 📞 Support

- **Issues**: [GitHub Issues](../../issues)
- **Discussions**: [GitHub Discussions](../../discussions)

## 🙏 Acknowledgments

- Built with modern AI technologies
- Inspired by the need for efficient job search tools
- Community-driven development

---

**Note**: This is a single-user system designed for personal use. It is not intended as a multi-tenant SaaS platform.
