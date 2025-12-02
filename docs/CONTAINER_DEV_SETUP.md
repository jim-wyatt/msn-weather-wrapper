# Containerized Development

Develop entirely in containers with Podman - consistent environment, easy setup, instant hot reload.

## Quick Start

```bash
./bootstrap-dev.sh setup   # One-time setup
./bootstrap-dev.sh start   # Start development
./bootstrap-dev.sh logs    # View logs
./bootstrap-dev.sh test    # Run all tests
```

**Services available at:**
- Frontend: http://localhost:5173 (Vite HMR)
- API: http://localhost:5000
- Health: http://localhost:5000/api/v1/health/ready

## Prerequisites

### Install Podman & podman-compose

**Linux:**
```bash
sudo apt-get install podman  # Ubuntu/Debian
sudo dnf install podman      # Fedora
pip3 install --user podman-compose
```

**macOS:**
```bash
brew install podman
pip3 install podman-compose
podman machine init && podman machine start
```

## Commands Reference

### Setup & Management
```bash
./bootstrap-dev.sh setup     # Build containers, install dependencies
./bootstrap-dev.sh start     # Start all services
./bootstrap-dev.sh stop      # Stop all services
./bootstrap-dev.sh restart   # Restart services
./bootstrap-dev.sh clean     # Remove everything
./bootstrap-dev.sh rebuild   # Clean rebuild
```

### Development
```bash
./bootstrap-dev.sh logs            # Follow all logs
./bootstrap-dev.sh shell-api       # API container shell
./bootstrap-dev.sh shell-frontend  # Frontend container shell
```

### Testing
```bash
./bootstrap-dev.sh test    # All tests
```

In API container shell:
```bash
pytest tests/test_api.py -v           # Specific tests
pytest --cov=src --cov-report=html    # With coverage
```

In frontend container shell:
```bash
npm run test:e2e          # E2E tests
npm run test:e2e:ui       # Interactive mode
npm run type-check        # TypeScript check
```

## Development Workflow

### Making Changes

**Backend:** Edit files in `src/` or `api.py` → Flask auto-reloads  
**Frontend:** Edit files in `frontend/src/` → Vite HMR updates instantly  
**Tests:** Edit test files → re-run tests

All source code is mounted as volumes - changes reflect immediately.

### Adding Dependencies

**Python:**
1. Edit `pyproject.toml`
2. Run `./bootstrap-dev.sh rebuild`

**Node.js:**
1. Edit `frontend/package.json`
2. Rebuild: `podman-compose -f podman-compose.dev.yml build frontend`

Or install temporarily in container:
```bash
./bootstrap-dev.sh shell-api
pip install package-name

./bootstrap-dev.sh shell-frontend
npm install package-name
```

## Architecture

### Containers
- **API**: Python 3.12 slim + Flask + dev tools (port 5000)
- **Frontend**: Node 20 Alpine + Vite + Playwright (port 5173)
- **Test Runner**: On-demand test execution

### Volume Mounts
```
./src → /app/src                    (API)
./api.py → /app/api.py              (API)
./tests → /app/tests                (API)
./frontend/src → /app/src           (Frontend)
./frontend/tests → /app/tests       (Frontend)
```

All changes immediately reflected in containers (hot reload enabled).

## Troubleshooting

### Containers won't start
```bash
podman ps -a                        # Check status
podman logs msn-weather-api-dev     # View logs
./bootstrap-dev.sh restart          # Try restart
```

### Port conflicts
```bash
lsof -i :5000  # Check what's using port
# Edit podman-compose.dev.yml to change ports
```

### Tests failing
```bash
./bootstrap-dev.sh shell-api
pytest -vv --tb=short              # Verbose output

./bootstrap-dev.sh shell-frontend
npm run test:e2e:headed            # See browser
```

### Clean slate
```bash
./bootstrap-dev.sh clean           # Nuclear option
./bootstrap-dev.sh setup           # Fresh start
```

## Benefits

| Feature | Container Dev | Local Dev |
|---------|--------------|-----------|
| Setup Time | 5-10 minutes | 15-30 minutes |
| Consistency | ✅ Identical everywhere | ❌ System dependent |
| Dependencies | ✅ Isolated | ❌ Can conflict |
| Cleanup | ✅ One command | ❌ Manual |
| Hot Reload | ✅ Works | ✅ Works |
| CI/CD Match | ✅ Same environment | ⚠️ May differ |

## Advanced Usage

### Run specific service
```bash
podman-compose -f podman-compose.dev.yml up api
podman-compose -f podman-compose.dev.yml up frontend
```

### View specific logs
```bash
podman-compose -f podman-compose.dev.yml logs -f api
podman-compose -f podman-compose.dev.yml logs -f frontend
```

### Check resources
```bash
podman stats
podman ps
podman images
```

## See Also

- [Development Guide](DEVELOPMENT.md) - Full development documentation
- [Testing Guide](TESTING.md) - Testing best practices
- [API Documentation](API.md) - API reference

---

Last updated: December 2, 2025
