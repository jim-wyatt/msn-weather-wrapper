# MSN Weather Wrapper

> A modern, production-ready Python wrapper for MSN Weather with Flask REST API, React frontend, and comprehensive security.

[![PyPI version](https://img.shields.io/pypi/v/msn-weather-wrapper.svg)](https://pypi.org/project/msn-weather-wrapper/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-67%20passing-success)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-89%25-success)](tests/)
[![CI/CD](https://img.shields.io/github/actions/workflow/status/jim-wyatt/msn-weather-wrapper/ci.yml?branch=main&label=CI%2FCD)](https://github.com/jim-wyatt/msn-weather-wrapper/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://jim-wyatt.github.io/msn-weather-wrapper/)
[![Container](https://img.shields.io/badge/container-ghcr.io-blue)](https://github.com/jim-wyatt/msn-weather-wrapper/pkgs/container/msn-weather-wrapper)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Development](#development)
- [Testing](#testing)
- [CI/CD Pipeline](#cicd-pipeline)
- [Deployment](#deployment)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

MSN Weather Wrapper is a comprehensive weather data solution featuring:
- **Python Library**: Type-safe weather client with Pydantic models
- **REST API**: Production-ready Flask API with Gunicorn
- **Web Frontend**: Modern React 19 + Vite 7 interface
- **Security**: Comprehensive input validation and attack prevention
- **DevOps**: Podman containers, SBOM generation, CI/CD ready

---

## Features

### Core Functionality
- 🌤️ **Weather Data Extraction** - Scrapes MSN Weather embedded JSON data
- 🌍 **International Support** - 406+ cities worldwide with autocomplete
- 📡 **REST API** - Flask 3.1+ with CORS and comprehensive validation
- ⚛️ **Modern Frontend** - React 19 + TypeScript 5.7+ with Vite 7
- 🚀 **Performance** - 5-minute response caching, 90%+ faster repeated requests
- 🔒 **Rate Limiting** - 30 requests/minute per IP, 200/hour total
- 📊 **Structured Logging** - JSON logging with request tracking

### Development & Quality
- 🐍 **Python 3.9+** - Full type hints and annotations
- 📘 **TypeScript** - Strict type safety for frontend code
- 📦 **Modern Packaging** - pyproject.toml with hatchling
- 🔒 **Type Safety** - Pydantic 2.12+ models
- ✅ **Comprehensive Testing** - 77 tests (90% coverage)
- 🎨 **Code Quality** - Ruff 0.14+ formatting/linting
- 🔍 **Static Analysis** - mypy 1.19+ type checking
- 🪝 **Pre-commit Hooks** - Automated quality checks

### Security & Production
- 🛡️ **Security Hardened** - Blocks SQL injection, XSS, path traversal, command injection
- 🏭 **Production Ready** - Gunicorn 23.0+ WSGI server (4 workers, 120s timeout)
- 📋 **SBOM Generation** - Syft integration for supply chain security
- 🐳 **Containerized** - Podman container orchestration
- 🔐 **Input Validation** - Comprehensive sanitization and filtering

### Technology Stack
- **Backend**: Python 3.9+, Flask 3.1+, BeautifulSoup4 4.14+, lxml 6.0+
- **Frontend**: React 19.2, Vite 7.2, Modern CSS
- **Testing**: pytest 9.0+, pytest-cov 7.0+, 77 tests
- **Quality**: Ruff 0.14+, mypy 1.19+, pre-commit 4.5+
- **Deployment**: Podman, Gunicorn 23.0+, Nginx

---

## Quick Start

### 🚀 Containerized Development (Recommended)

Get a complete development environment with all dependencies in containers:

```bash
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper

# One-command setup
./bootstrap-dev.sh setup

# Start development environment
./bootstrap-dev.sh start
```

**Access the application:**
- 🌐 Frontend: http://localhost:5173 (Vite dev server with HMR)
- 📡 API: http://localhost:5000
- 💚 Health Check: http://localhost:5000/api/v1/health/ready

See [Container Development Setup](docs/CONTAINER_DEV_SETUP.md) for full documentation.

### 📦 Production Deployment

```bash
# Using podman-compose
podman-compose up -d

# Access at http://localhost:8080
```

### 🧪 Automated Testing

Run complete deployment test with container builds:

```bash
./tools/test_deployment.sh
```

---

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 20+ (for frontend development)
- Podman (for containerized deployment)

### Single Container Deployment (Recommended)

The entire stack (Flask API + React frontend + nginx) runs in a unified container:

```bash
# Clone repository
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper

# Build and start the unified container
podman build -t msn-weather-wrapper .
podman run -d --name msn-weather -p 8080:80 msn-weather-wrapper

# View logs
podman logs -f msn-weather

# Stop service
podman stop msn-weather && podman rm msn-weather
```

The application will be available at:
- **Frontend**: http://localhost:8080
- **API**: http://localhost:8080/api

### Quick Start with Test Script

Run the complete deployment test (builds container and runs integration tests):

```bash
# Clone and run automated test
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper
./tools/test_deployment.sh
```

This script will:
1. Check prerequisites (podman, python3)
2. Clean up existing containers
3. Set up Python virtual environment
4. Install dependencies
5. Build container from scratch
6. Start service
7. Wait for API readiness
8. Run 17 integration tests

### Option 2: From Source (Development)

```bash
# Clone repository
git clone https://github.com/jim-wyatt/msn-weather-wrapper.git
cd msn-weather-wrapper

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

---

## Usage

### Python Library

Use the weather client in your Python applications:

```python
from msn_weather_wrapper import WeatherClient, Location

# Create a weather client
with WeatherClient() as client:
    # Define a location
    location = Location(city="London", country="UK")
    
    # Get weather data
    weather = client.get_weather(location)
    
    print(f"Temperature: {weather.temperature}°C")
    print(f"Condition: {weather.condition}")
    print(f"Humidity: {weather.humidity}%")
    print(f"Wind Speed: {weather.wind_speed} km/h")
```

### Flask REST API

#### Start the API Server

**Development Mode:**
```bash
python api.py
```

**Production Mode with Gunicorn:**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 api:app
```

**Podman Deployment:**
```bash
# API automatically runs with Gunicorn in production mode
podman-compose up -d
```

📖 **See [API.md](docs/API.md) for complete API documentation.**

#### API Examples

**GET Request:**
```bash
curl "http://localhost:5000/api/weather?city=Seattle&country=USA"
```

**POST Request:**
```bash
curl -X POST http://localhost:5000/api/weather \
  -H "Content-Type: application/json" \
  -d '{"city": "London", "country": "UK"}'
```

**React/TypeScript:**
```typescript
const weather = await fetch(
  `http://localhost:5000/api/weather?city=Seattle&country=USA`
).then(res => res.json());

console.log(`Temperature: ${weather.temperature}°C`);
```

---

### React Frontend

Modern web interface with TypeScript type safety, city autocomplete, temperature unit toggle, and beautiful UI.

#### Local Development

```bash
cd frontend
npm install
npm run dev  # Starts dev server on http://localhost:8080
```

#### Type Checking & Building

```bash
cd frontend
npm run lint   # TypeScript type checking
npm run build  # TypeScript compilation + Vite build → frontend/dist/
```

#### Features
- 📘 **TypeScript 5.7+** - Full type safety with strict mode
- 🔍 City autocomplete with 406+ cities worldwide
- 🌡️ **Temperature unit toggle** - Switch between Celsius and Fahrenheit
- 🔄 **Automatic retry** - Retries failed requests with exponential backoff
- 💾 **Persistent preferences** - Remembers your temperature unit choice
- 🎨 Modern gradient UI with smooth animations
- 📱 Fully responsive design
- ⚡ Vite-powered hot module replacement
- 🌐 API proxy configuration for development
- 💨 Real-time weather updates
- ⚠️ Error handling with user-friendly messages

---

## Documentation

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Main documentation (this file) |
| [API.md](docs/API.md) | Complete REST API reference |
| [CONTAINER_DEV_SETUP.md](docs/CONTAINER_DEV_SETUP.md) | Containerized development guide |
| [DOCS_GENERATION_GUIDE.md](docs/DOCS_GENERATION_GUIDE.md) | Report generation & documentation |
| [NEW_FEATURES.md](docs/NEW_FEATURES.md) | New features documentation |
| [SECURITY.md](docs/SECURITY.md) | Security testing and validation results |
| [SYFT_GUIDE.md](docs/SYFT_GUIDE.md) | SBOM generation guide |
| [TEST_RESULTS.md](docs/TEST_RESULTS.md) | Test coverage and results |
| [CHANGELOG.md](docs/CHANGELOG.md) | Version history and updates |

---

## Development

### Containerized Development (Recommended)

For a fully isolated development environment with all dependencies in containers:

```bash
# Initial setup - builds containers and installs all dependencies
./bootstrap-dev.sh setup

# Start development environment (API + Frontend in containers)
./bootstrap-dev.sh start

# View logs from all containers
./bootstrap-dev.sh logs

# Run all tests (backend + frontend E2E)
./bootstrap-dev.sh test

# Generate reports and serve documentation site
./bootstrap-dev.sh docs

# Open shell in API container for debugging
./bootstrap-dev.sh shell-api

# Open shell in frontend container
./bootstrap-dev.sh shell-frontend

# Stop containers
./bootstrap-dev.sh stop

# Clean up everything (remove containers, images, volumes)
./bootstrap-dev.sh clean
```

**Benefits:**
- ✅ Consistent environment across all machines
- ✅ No local dependency installation needed
- ✅ Isolated from system packages
- ✅ Hot reload for both backend and frontend
- ✅ All tests run in containers
- ✅ Easy cleanup and reset

📖 Full documentation: [Container Development Setup](docs/CONTAINER_DEV_SETUP.md)

### Setup Development Environment (Local)

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Code Quality Tools

**Format code:**
```bash
ruff format .
```

**Lint code:**
```bash
ruff check .
```

**Type checking:**
```bash
mypy src/msn_weather_wrapper
```

**Run all pre-commit hooks:**
```bash
pre-commit run --all-files
```

---

## Testing

### Test Suite Overview

- **77 total tests** - Comprehensive coverage
- **90% code coverage** - High-quality validation
- **3 test categories** - Unit, security, integration
- ✅ **All tests passing**

### Run Tests

**All tests:**
```bash
pytest
```

**Unit tests only (fast, no containers):**
```bash
pytest tests/test_client.py tests/test_models.py tests/test_api.py
```

**Security tests:**
```bash
pytest tests/test_security.py -v
```

**Integration tests (requires running containers):**
```bash
podman-compose up -d
pytest tests/test_integration.py -v
```

**With coverage report:**
```bash
pytest --cov=src --cov-report=html
```

### Test Statistics

| Category | Count | Description |
|----------|-------|-------------|
| Unit | 35 | Fast tests, no network required |
| Security | 25 | Input validation and attack prevention |
| Integration | 17 | Live API testing with containers |
| **Total** | **77** | **90% code coverage** |

📖 **See [TEST_RESULTS.md](docs/TEST_RESULTS.md) for detailed results.**

---

## Deployment

### Podman Compose (Recommended)

Production-ready single-container deployment:

```bash
# Build and start
podman-compose up -d

# View logs
podman-compose logs -f

# Restart service
podman-compose restart

# Stop service
podman-compose down

# Rebuild after changes
podman-compose up -d --build
```

### Standalone Podman Container

**Single unified container (API + Frontend):**
```bash
podman build -t msn-weather-app .
podman run -p 8080:80 msn-weather-app
```

Access the application at `http://localhost:8080`

### Architecture

**Unified Container:**
- Base: Python 3.12 slim
- Frontend: React 19 + Vite 7 (built with Node.js 20)
- Web Server: Nginx (reverse proxy + static files)
- API Server: Gunicorn 23.0+ WSGI (4 workers, 120s timeout)
- Process Manager: Supervisor (manages nginx + gunicorn)
- Port: 80 (nginx serves frontend and proxies /api/ to gunicorn)
- Health checks: Enabled
- Restart policy: Unless stopped

**Multi-stage Build:**
1. Stage 1: Build React frontend with Node.js
2. Stage 2: Python + Nginx, copy built frontend, run both services

---

## CI/CD Pipeline

### 🚀 GitHub Actions Workflows

Comprehensive CI/CD pipeline with 4 workflows, 17 jobs, and full automation.

#### Workflows Overview

| Workflow | Triggers | Jobs | Purpose |
|----------|----------|------|---------|
| **ci.yml** | Push, PR, Manual | 10 | Main testing & deployment |
| **container.yml** | Push, Tags, PR | 2 | Multi-platform container builds |
| **dependencies.yml** | Weekly, Manual | 3 | Automated dependency updates |
| **performance.yml** | PR, Manual | 2 | Load testing & benchmarking |

#### Key Features

- ✅ **Matrix Testing**: Python 3.9, 3.10, 3.11, 3.12
- ✅ **Security Scanning**: Bandit, Safety, Grype, Trivy
- ✅ **Container Builds**: Multi-arch (amd64, arm64)
- ✅ **SBOM Generation**: Syft with vulnerability scanning
- ✅ **Auto Documentation**: Deploy to GitHub Pages
- ✅ **Dependency Updates**: Weekly automated PRs
- ✅ **Performance Testing**: Load tests + benchmarks

#### Quick Start

```bash
# 1. Enable GitHub Actions (Settings → Actions)
# 2. Enable GitHub Pages (Settings → Pages → gh-pages branch)
# 3. Push workflows
git add .github/
git commit -m "ci: add CI/CD pipeline"
git push origin main
```

**See**: [CI/CD Quick Start Guide](.github/QUICKSTART.md) for detailed setup.

#### Pipeline Jobs

**Main CI/CD (`ci.yml`)**:
- `code-quality` - Ruff + mypy checks
- `security` - Security scanning
- `unit-tests` - Tests on 4 Python versions
- `coverage` - 90% coverage with Codecov
- `container-build` - Build & test unified Podman container
- `integration-tests` - Full stack testing
- `sbom` - Generate SBOMs with Syft
- `docs` - Build MkDocs documentation
- `deploy-docs` - Deploy to GitHub Pages (main only)
- `release` - Create releases with attachments (tags only)

**Container Build (`container.yml`)**:
- Multi-platform builds (amd64, arm64)
- Push to GitHub Container Registry
- Vulnerability scanning with Trivy

**Dependencies (`dependencies.yml`)**:
- Weekly Python/npm updates
- Automated PR creation
- Security audits

**Performance (`performance.yml`)**:
- Locust load testing (50 users)
- pytest-benchmark performance tracking

#### Documentation

- **Workflows**: [.github/workflows/README.md](.github/workflows/README.md)
- **Quick Start**: [.github/QUICKSTART.md](.github/QUICKSTART.md)

---

## SBOM Generation

Generate Software Bill of Materials for supply chain security:

```bash
# Generate all SBOMs (containers, source, packages)
./tools/generate_sbom.sh

# CI/CD optimized
./tools/generate_sbom_ci.sh

# View summary
cat sbom_output/SBOM_SUMMARY_*.md
```

📖 **See [SYFT_GUIDE.md](docs/SYFT_GUIDE.md) for complete SBOM documentation.**

---

## Security

### Security Features

✅ **Input Validation** - Blocks all dangerous characters  
✅ **SQL Injection Protection** - Prevents database attacks  
✅ **XSS Prevention** - Blocks script injection  
✅ **Path Traversal Protection** - Prevents file system access  
✅ **Command Injection Prevention** - Blocks shell commands  
✅ **Length Limits** - 100 character maximum  
✅ **Type Checking** - Enforces string types  
✅ **Comprehensive Testing** - 25 dedicated security tests  

📖 **See [SECURITY.md](docs/SECURITY.md) for security testing details.**

---

## Project Structure

```
msn-weather-wrapper/
├── src/msn_weather_wrapper/    # Python package
│   ├── __init__.py
│   ├── client.py             # Weather client
│   ├── models.py             # Pydantic models
│   └── py.typed              # Type marker
├── tests/                    # Test suite
│   ├── test_api.py           # API tests
│   ├── test_client.py        # Client tests
│   ├── test_models.py        # Model tests
│   ├── test_security.py      # Security tests
│   └── test_integration.py   # Integration tests
├── frontend/                 # React application
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── data/             # City database
│   │   ├── App.tsx           # Main app (TypeScript)
│   │   └── main.tsx          # Entry point (TypeScript)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── Containerfile
│   └── nginx.conf
├── api.py                    # Flask REST API
├── config/                   # Configuration files
│   ├── nginx.conf            # Nginx reverse proxy config
│   └── supervisord.conf      # Process manager config
├── tools/                    # Shell scripts
│   ├── generate_sbom.sh      # SBOM generation
│   ├── generate_sbom_ci.sh   # CI/CD SBOM
│   └── test_deployment.sh    # Deployment test
├── Containerfile             # Unified container (API + Frontend)
├── podman-compose.yml        # Podman Compose orchestration
├── pyproject.toml            # Python config
├── .pre-commit-config.yaml   # Pre-commit hooks
└── docs/                     # Documentation
    ├── README.md
    ├── API.md
    ├── SECURITY.md
    ├── SYFT_GUIDE.md
    ├── TEST_RESULTS.md
    └── CHANGELOG.md
```

---

## Requirements

### Python Dependencies

**Production:**
- Python 3.9+
- requests ≥ 2.32.0
- pydantic ≥ 2.12.0
- beautifulsoup4 ≥ 4.14.0
- lxml ≥ 6.0.0
- flask ≥ 3.1.0
- flask-cors ≥ 6.0.0
- gunicorn ≥ 23.0.0

**Development:**
- pytest ≥ 9.0.0
- pytest-cov ≥ 7.0.0
- pytest-asyncio ≥ 1.0.0
- ruff ≥ 0.14.0
- mypy ≥ 1.19.0
- pre-commit ≥ 4.5.0
- types-requests ≥ 2.32.0
- types-beautifulsoup4 ≥ 4.14.0

📘 **See [pyproject.toml](pyproject.toml) for complete dependency list.**

---

## Documentation Site

📚 **[View Full Documentation](https://jim-wyatt.github.io/msn-weather-wrapper/)**

This project includes a beautiful documentation site built with MkDocs Material. To build and deploy:

```bash
# Install MkDocs Material
pip install mkdocs-material

# Preview locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

See [DOCUMENTATION_SITE_GUIDE.md](DOCUMENTATION_SITE_GUIDE.md) for detailed setup instructions.

---

## Troubleshooting

### Common Issues

**Frontend TypeScript Errors**
```bash
# Error: Cannot find module 'react' or its corresponding type declarations
cd frontend
npm install  # Install dependencies
```

**Node.js Version**
```bash
# This project requires Node.js 20+
node --version  # Check your version

# Use nvm (recommended)
nvm use  # Uses version from .nvmrc
nvm install 20
```

**Slow API Response**
- First request to a city may be slow (fetching from MSN)
- Subsequent requests are cached for 5 minutes
- Check network connectivity if consistently slow

**Container Build Issues**
```bash
# Clean rebuild
podman system prune -a
podman-compose build --no-cache
podman-compose up -d
```

**Port Already in Use**
```bash
# Check what's using port 8080
sudo lsof -i :8080

# Stop existing containers
podman-compose down
```

**API Returns 500 Error**
```bash
# Check container logs
podman-compose logs -f

# Check if MSN Weather is accessible
curl -I https://www.msn.com/en-us/weather/
```

---

## Contributing

Contributions are welcome! Please ensure:

1. ✅ All tests pass (`pytest`)
2. 🎨 Code is formatted (`ruff format .`)
3. 🔍 Type checks pass (`mypy src/`)
4. 🪝 Pre-commit hooks pass
5. 📝 Documentation is updated

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Links

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/jim-wyatt/msn-weather-wrapper/issues)
- 💬 [Discussions](https://github.com/jim-wyatt/msn-weather-wrapper/discussions)
- 🎉 [Releases](https://github.com/jim-wyatt/msn-weather-wrapper/releases)

---

<div align="center">

**Built with ❤️ using Python, Flask, and React**

[Report Bug](https://github.com/jim-wyatt/msn-weather-wrapper/issues) ·
[Request Feature](https://github.com/jim-wyatt/msn-weather-wrapper/issues) ·
[Documentation](docs/)

</div>

---

## Disclaimer

This project is an unofficial wrapper for MSN Weather data and is provided for educational and personal use only. This software is not affiliated with, endorsed by, or officially connected to Microsoft Corporation or MSN Weather in any way.

**Important Notes:**
- This tool scrapes publicly available weather data from MSN Weather
- Usage should comply with Microsoft's Terms of Service and robots.txt
- This is not intended for commercial use or high-volume automated requests
- Weather data accuracy and availability are subject to MSN Weather's service
- The maintainers are not responsible for any misuse or violations of terms of service

For production weather data needs, please use official weather APIs with proper licensing.
