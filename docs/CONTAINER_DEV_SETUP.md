# Containerized Development

Develop entirely in containers with Podman for a consistent setup, easier onboarding, and fast hot reload.

## Quick Start

```bash
./dev.sh setup   # One-time setup
./dev.sh start   # Start development
./dev.sh logs    # View logs
./dev.sh test    # Run all tests
```

**Services:**

- Frontend: <http://localhost:3000> (Next.js HMR)
- API: <http://localhost:5000>
- Health: <http://localhost:5000/api/v1/health>

## Prerequisites

### Install Podman and `podman-compose`

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

### Setup and management

```bash
./dev.sh setup              # Build containers, install dependencies
./dev.sh start              # Start all services
./dev.sh stop               # Stop all services
./dev.sh restart            # Restart services
./dev.sh status             # Check service health
./dev.sh clean              # Remove containers and volumes
./dev.sh clean --gitignore  # Also remove gitignored files (with preview)
./dev.sh rebuild            # Clean rebuild
```

### Development

```bash
./dev.sh logs            # Follow all logs
./dev.sh shell-api       # API container shell
./dev.sh shell-frontend  # Frontend container shell
```

### Testing

```bash
./dev.sh test
```

Inside the API container shell:

```bash
pytest tests/test_api.py -v
pytest --cov=src --cov-report=html
```

Inside the frontend container shell:

```bash
npm run test:e2e
npm run test:e2e:ui
npm run type-check
```

## Development Workflow

### Making changes

- **Backend:** edit files in `backend/` or `api.py` and FastAPI reloads automatically.
- **Frontend:** edit files in `frontend/app/` and Next.js HMR updates instantly.
- **Tests:** edit test files and rerun the relevant checks.

All source code is mounted as a volume, so changes appear immediately.

### Adding dependencies

**Python:**

1. Edit `pyproject.toml`.
2. Run `./dev.sh rebuild`.

**Node.js:**

1. Edit `frontend/package.json`.
2. Rebuild with `podman-compose -f infra/compose/podman-compose.dev.yml build frontend`.

Or install temporarily inside a container:

```bash
./dev.sh shell-api
pip install package-name

./dev.sh shell-frontend
npm install package-name
```

## Architecture

### Containers

- **API:** Python 3.12 slim + FastAPI + dev tools on port `5000`
- **Frontend:** Node 22 slim + Next.js + Playwright on port `3000`
- **Test runner:** on-demand checks and browser tests

### Volume mounts

```text
./src            -> /app/src      (API)
./api.py         -> /app/api.py   (API)
./tests          -> /app/tests    (API)
./frontend/app   -> /app/app      (Frontend)
./frontend/tests -> /app/tests    (Frontend)
```

### Networking

- The API is reachable as `api:5000` inside the compose network.
- The frontend proxy uses `API_URL=http://api:5000` in containers.
- Outside containers, browser traffic still uses `localhost`.

**Next.js rewrites example:**

```typescript
// next.config.ts
async rewrites() {
  const apiUrl = process.env.API_URL ?? 'http://localhost:5000';
  return [
    {
      source: '/api/:path*',
      destination: `${apiUrl}/api/:path*`,
    },
  ];
},
```

## Troubleshooting

### Containers will not start

```bash
podman ps -a
podman logs msn-weather-api-dev
./dev.sh restart
```

### Port conflicts

```bash
lsof -i :5000
# Then edit infra/compose/podman-compose.dev.yml if you need different ports
```

### Tests failing

```bash
./dev.sh shell-api
pytest -vv --tb=short

./dev.sh shell-frontend
npm run test:e2e:headed
```

### Clean slate

```bash
./dev.sh clean
./dev.sh clean --gitignore
./dev.sh clean -g
./dev.sh setup
```

**Gitignore cleanup notes:**

- Shows a preview of files to remove with `git clean -ndX`
- Prompts for confirmation before deletion
- Removes only ignored files such as `__pycache__` and `node_modules`
- Useful for clearing build artifacts and caches

## Benefits

| Feature | Container Dev | Local Dev |
| --- | --- | --- |
| Setup Time | 5-10 minutes | 15-30 minutes |
| Consistency | ✅ Identical everywhere | ❌ System dependent |
| Dependencies | ✅ Isolated | ❌ Can conflict |
| Cleanup | ✅ One command | ❌ Manual |
| Hot Reload | ✅ Works | ✅ Works |
| CI/CD Match | ✅ Same environment | ⚠️ May differ |

## Advanced Usage

### Run a specific service

```bash
podman-compose -f infra/compose/podman-compose.dev.yml up api
podman-compose -f infra/compose/podman-compose.dev.yml up frontend
```

### View service logs

```bash
podman-compose -f infra/compose/podman-compose.dev.yml logs -f api
podman-compose -f infra/compose/podman-compose.dev.yml logs -f frontend
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

