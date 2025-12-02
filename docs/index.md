# MSN Weather Wrapper Documentation

Modern Python wrapper for MSN Weather with Flask API, React frontend, and production-ready containerized deployment.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-77%20passing-success)](../tests/)
[![Coverage](https://img.shields.io/badge/coverage-90%25-success)](TESTING.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../LICENSE)

## 📚 Documentation

### Getting Started
- **[Installation & Quick Start](../README.md#quick-start)** - Get running in 5 minutes
- **[Usage Examples](../README.md#usage)** - Python library and API usage
- **[Requirements](../README.md#requirements)** - Dependencies and prerequisites

### Development
- **[Development Guide](DEVELOPMENT.md)** - Complete development workflow
- **[Container Development](CONTAINER_DEV_SETUP.md)** - Podman-based dev environment
- **[Testing Guide](TESTING.md)** - Test suite, coverage, and best practices
- **[Versioning Guide](VERSIONING.md)** - Semantic versioning and release process

### API & Features
- **[API Reference](API.md)** - Complete REST API documentation
- **[Security](SECURITY.md)** - Security features, testing, and best practices

### Deployment & Operations
- **[Deployment Guide](../README.md#deployment)** - Production deployment with Podman
- **[SBOM Generation](SYFT_GUIDE.md)** - Software Bill of Materials for supply chain security
- **[CI/CD Pipeline](../README.md#cicd-pipeline)** - GitHub Actions workflows

### Project Information
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Reports](reports/index.md)** - Automated CI/CD reports (test, coverage, security)
- **[License](../README.md#license)** - MIT License

---

## Quick Navigation

### 🚀 For Users
Start here if you want to use the weather API:
1. [Quick Start](../README.md#quick-start) - Deploy with Podman in 2 commands
2. [API Examples](API.md) - Learn the REST API
3. [Frontend Usage](../README.md#react-frontend) - Use the web interface

### 👨‍💻 For Developers
Start here if you want to contribute:
1. [Development Setup](DEVELOPMENT.md) - Get your dev environment running
2. [Container Dev](CONTAINER_DEV_SETUP.md) - Recommended containerized workflow
3. [Testing Guide](TESTING.md) - Run and write tests
4. [Contributing](../README.md#contributing) - Contribution guidelines

### 🔒 For Security Teams
Security audit information:
1. [Security Overview](SECURITY.md) - Security features and controls
2. [Security Testing](SECURITY.md#security-testing) - Test methodology and results
3. [SBOM Guide](SYFT_GUIDE.md) - Software bill of materials

### 🏗️ For DevOps
Deployment and operations:
1. [Deployment Guide](../README.md#deployment) - Container orchestration with Podman
2. [CI/CD Pipeline](../README.md#cicd-pipeline) - Automated workflows
3. [Health Checks](API.md#health-checks) - K8s-ready probes

---

## Features at a Glance

| Feature | Description | Documentation |
|---------|-------------|---------------|
| 🐍 **Python Library** | Type-safe weather client with Pydantic | [Usage](../README.md#python-library) |
| 🌐 **REST API** | Flask 3.1+ with comprehensive validation | [API Docs](API.md) |
| ⚛️ **React Frontend** | React 19 + Vite 7 + TypeScript | [Frontend](../README.md#react-frontend) |
| 🐳 **Containerized** | Podman deployment, dev containers | [Container Dev](CONTAINER_DEV_SETUP.md) |
| ✅ **Tested** | 77 tests, 90% coverage | [Testing](TESTING.md) |
| 🔒 **Secure** | Input validation, rate limiting | [Security](SECURITY.md) |
| 📋 **SBOM** | Supply chain security | [SBOM Guide](SYFT_GUIDE.md) |
| 🎨 **Quality** | Ruff, mypy, pre-commit hooks | [Development](DEVELOPMENT.md) |
| 🚀 **Production** | Gunicorn, Nginx, health checks | [Deployment](../README.md#deployment) |

---

## Technology Stack

### Backend
- Python 3.9+, Flask 3.1+, Gunicorn 23.0+
- Pydantic 2.12+, BeautifulSoup4 4.14+, lxml 6.0+
- Structlog, Flask-CORS, Flask-Limiter

### Frontend
- React 19.2, Vite 7.2, TypeScript 5.7+
- Modern CSS, responsive design
- Playwright E2E tests

### DevOps
- Podman containers, multi-stage builds
- pytest 9.0+, mypy 1.19+, ruff 0.14+
- MkDocs Material documentation
- GitHub Actions CI/CD

---

## Support & Resources

- 🐛 [Report Issues](https://github.com/yourusername/msn-weather-wrapper/issues)
- 💬 [Discussions](https://github.com/yourusername/msn-weather-wrapper/discussions)
- 📖 [Source Code](https://github.com/yourusername/msn-weather-wrapper)
- 🎉 [Releases](https://github.com/yourusername/msn-weather-wrapper/releases)

---

## Next Steps

- **New to the project?** Start with [Quick Start](../README.md#quick-start)
- **Want to develop?** Follow [Development Guide](DEVELOPMENT.md)
- **Need API details?** Read [API Reference](API.md)
- **Deploying to production?** Check [Deployment Guide](../README.md#deployment)

---

<div align="center">

**MSN Weather Wrapper** - Modern, Secure, Production-Ready

[Get Started](../README.md#quick-start) · [Docs](.) · [GitHub](https://github.com/yourusername/msn-weather-wrapper)

</div>
