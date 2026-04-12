# MSN Weather Wrapper Documentation

Modern Python wrapper for MSN Weather with a FastAPI backend, React frontend, and production-ready containerized deployment.

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-168%20passing-success)](TESTING.md)
[![Coverage](https://img.shields.io/badge/coverage-97%25-success)](TESTING.md)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/jim-wyatt/msn-weather-wrapper/blob/main/LICENSE)

---

## Quick Navigation

### 🚀 Getting Started
- **[Installation & Setup](DEVELOPMENT.md)** - Get up and running
- **[Quick Start Guide](DEVELOPMENT.md#quick-start)** - Deploy in minutes
- **[Usage Examples](API.md)** - Python library and API usage

### 👨‍💻 Development
- **[Development Guide](DEVELOPMENT.md)** - Complete development workflow
- **[Container Development](CONTAINER_DEV_SETUP.md)** - Podman-based dev environment
- **[Testing Guide](TESTING.md)** - Test suite, coverage, and best practices
- **[Versioning Guide](VERSIONING.md)** - Semantic versioning and release process
- **[DevSecOps Monitor](MONITOR_DASHBOARD.md)** - Local + CI/CD RAG dashboard

### 📚 API & Features
- **[API Reference](API.md)** - Complete REST API documentation
- **[Interactive API Docs](API.md#interactive-api-documentation)** - Swagger UI for live API exploration
- **[Security](SECURITY.md)** - Security features, testing, and best practices

### 🚀 Deployment & Operations

- **[Container Setup](CONTAINER_DEV_SETUP.md)** - Production deployment
- **[SBOM Generation](SYFT_GUIDE.md)** - Software bill of materials
- **[PyPI Setup](PYPI_SETUP.md)** - Automated PyPI publishing

### 📊 Project Information
- **[Changelog](CHANGELOG.md)** - Version history and updates
- **[Reports](reports/index.md)** - Automated CI/CD reports
- **[Contributing](DEVELOPMENT.md#contributing-guidelines)** - Contribution guidelines

---

## Documentation Structure

### Core Documentation
| Document | Purpose | Audience |
|----------|---------|----------|
| [index.md](index.md) | Documentation hub & navigation | Everyone |
| [API.md](API.md) | REST API reference | API Users |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Development workflow | Contributors |
| [SECURITY.md](SECURITY.md) | Security features & testing | Security Teams |
| [TESTING.md](TESTING.md) | Test suite documentation | Developers |

### Specialized Guides

| Document | Purpose | Audience |
|----------|---------|----------|
| [CONTAINER_DEV_SETUP.md](CONTAINER_DEV_SETUP.md) | Containerized development | Developers |
| [MONITOR_DASHBOARD.md](MONITOR_DASHBOARD.md) | DevSecOps monitor & RAG thresholds | DevSecOps/Developers |
| [SYFT_GUIDE.md](SYFT_GUIDE.md) | SBOM generation | DevOps/Security |
| [VERSIONING.md](VERSIONING.md) | Release process | Maintainers |
| [PYPI_SETUP.md](PYPI_SETUP.md) | PyPI publishing configuration | Maintainers |

### Reports & Logs
| Document | Purpose | Audience |
|----------|---------|----------|
| [reports/index.md](reports/index.md) | CI/CD reports hub | DevOps |
| [CHANGELOG.md](CHANGELOG.md) | Version history | Everyone |

---

## Features at a Glance

| Feature | Description | Documentation |
|---------|-------------|---------------|
| 🐍 **Python Library** | Type-safe weather client | [Usage](API.md) |
| 🌐 **REST API** | FastAPI with typed validation and OpenAPI docs | [API Docs](API.md) |
| 📖 **Swagger UI** | Interactive API documentation | [Interactive Docs](API.md#interactive-api-documentation) |
| ⚛️ **React Frontend** | Next.js 16, React 19 + TypeScript 6 | [Frontend](API.md) |
| 🐳 **Containerized** | Podman deployment | [Container Dev](CONTAINER_DEV_SETUP.md) |
| ✅ **Tested** | 168 tests (128 backend, 40 frontend), 97% coverage | [Testing](TESTING.md) |
| 🔒 **Secure** | Enhanced security scanning | [Security](SECURITY.md) |
| 📋 **SBOM** | Supply chain security | [SBOM Guide](SYFT_GUIDE.md) |

---

## Technology Stack

- **Backend**: Python 3.10+, FastAPI, Pydantic 2.12+, Uvicorn, Gunicorn 23.0+
- **Frontend**: Next.js 16, React 19.2, TypeScript 6+
- **Testing**: pytest 9.0+, Playwright, 168 tests
- **Quality**: ruff 0.14+, mypy 1.19+, pre-commit hooks
- **Deployment**: Podman/Docker, Nginx, multi-stage builds

---

## Support & Resources

- 🐛 [Report Issues](https://github.com/jim-wyatt/msn-weather-wrapper/issues)
- 💬 [Discussions](https://github.com/jim-wyatt/msn-weather-wrapper/discussions)
- 📖 [Source Code](https://github.com/jim-wyatt/msn-weather-wrapper)
- 🎉 [Releases](https://github.com/jim-wyatt/msn-weather-wrapper/releases)

---
