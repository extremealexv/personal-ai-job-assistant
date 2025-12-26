# Security Policy

## 🔒 Overview

The Personal AI Job Search Assistant handles sensitive personal information including:
- Resume data and work history
- Personal identification information
- Job board credentials
- Email content
- Calendar data

We take security seriously and appreciate your help in keeping this project secure.

## 🛡️ Security Principles

### Data Protection
- **Encryption at Rest**: All sensitive data is encrypted in the database
- **Encryption in Transit**: All API communication uses HTTPS/TLS
- **Credential Management**: Job board credentials stored with encryption
- **Data Isolation**: Resume data isolated from logs and analytics

### Access Control
- **Single-User System**: Designed for personal use only
- **Authentication Required**: All endpoints require authentication
- **Session Management**: Secure session handling with timeout
- **API Security**: Rate limiting and input validation

### Privacy
- **Data Minimization**: Only collect necessary information
- **No Data Sharing**: No third-party data sharing
- **Local Processing**: AI processing respects privacy boundaries
- **Audit Logging**: System actions logged (excluding sensitive content)

## 📋 Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.x     | :white_check_mark: |

**Note**: This project is currently in active development (0.x versions). Security updates will be provided for the latest development version.

## 🚨 Reporting a Vulnerability

### Please DO NOT Report Security Vulnerabilities Publicly

If you discover a security vulnerability, please follow responsible disclosure:

### How to Report

1. **Email**: Send details to `security@example.com`
2. **Subject Line**: `[SECURITY] Brief description`
3. **Include**:
   - Type of vulnerability
   - Location in code (file path, line number)
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)
   - Your contact information

### What to Expect

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Status Updates**: Weekly until resolved
- **Resolution Timeline**: Varies by severity
  - Critical: 7 days
  - High: 30 days
  - Medium: 60 days
  - Low: 90 days

### Disclosure Policy

- We will coordinate disclosure timing with you
- Public disclosure only after fix is deployed
- Credit given to security researchers (unless you prefer anonymity)

## 🔍 Security Best Practices for Users

### Deployment

1. **Environment Variables**
   - Never commit `.env` files
   - Use strong, unique passwords
   - Rotate API keys regularly

2. **Database Security**
   - Use strong database passwords
   - Enable SSL/TLS for database connections
   - Regular backups with encryption

3. **API Security**
   - Use HTTPS only (no HTTP)
   - Implement rate limiting
   - Enable CORS restrictions

4. **Browser Extension**
   - Only install from trusted sources
   - Review permissions carefully
   - Keep extension updated

### Configuration

```bash
# Example secure configuration
# .env file (NEVER commit this file)

# Use strong random passwords
DATABASE_PASSWORD=<generate-strong-password>
SECRET_KEY=<generate-strong-secret>

# Enable security features
HTTPS_ONLY=true
SECURE_COOKIES=true
SESSION_TIMEOUT=3600

# API keys (never expose these)
OPENAI_API_KEY=<your-key>
GMAIL_CLIENT_SECRET=<your-secret>
```

### Monitoring

- Review application logs regularly
- Monitor for unusual access patterns
- Set up alerts for authentication failures
- Track API usage for anomalies

## 🔐 Security Features

### Authentication
- Password-based authentication (required)
- Optional WebAuthn/2FA support
- Session management with timeout
- Secure password storage (bcrypt/argon2)

### Data Protection
- Database encryption at rest
- TLS for all network communication
- Secure credential storage
- Sensitive data masking in logs

### Browser Extension
- Minimal permissions requested
- Content Security Policy compliance
- Secure message passing
- No sensitive data in extension storage

### API Security
- Input validation on all endpoints
- SQL injection prevention
- XSS protection
- CSRF protection
- Rate limiting

## 🚫 Known Limitations

As a single-user application, some enterprise security features are not implemented:

- Multi-factor authentication (optional, not required)
- Advanced threat detection
- Audit log retention policies
- Compliance certifications

These are acceptable trade-offs for a personal-use application but should be considered if adapting for other uses.

## 📚 Security Resources

### Dependencies
- Regularly update dependencies: `npm audit`, `pip-audit`
- Monitor security advisories
- Use Dependabot for automated updates

### Development Tools
- **SAST**: Static application security testing
- **Dependency Scanning**: Automated vulnerability detection
- **Secret Scanning**: Prevent credential leaks

### References
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [CWE Top 25](https://cwe.mitre.org/top25/)

## ✅ Security Checklist for Contributors

Before submitting code that handles sensitive data:

- [ ] Input validation implemented
- [ ] Output encoding applied
- [ ] SQL injection prevented (parameterized queries)
- [ ] XSS protection in place
- [ ] Authentication/authorization checked
- [ ] Sensitive data not logged
- [ ] Secrets not hardcoded
- [ ] Dependencies up to date
- [ ] Error messages don't leak sensitive info
- [ ] Tests include security scenarios

## 📞 Contact

- **Security Issues**: security@example.com
- **General Questions**: Create a [Discussion](../../discussions)

## 🙏 Acknowledgments

We appreciate security researchers who help keep this project secure. Recognition will be given in release notes (with permission).

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!