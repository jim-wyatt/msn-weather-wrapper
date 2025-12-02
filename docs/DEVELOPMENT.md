# Development Guide

Complete guide for developing, testing, and contributing to MSN Weather Wrapper.

## Quick Start

### Containerized Development (Recommended)

Get a complete development environment in containers:

```bash
# Clone and setup
git clone https://github.com/yourusername/msn-weather-wrapper.git
cd msn-weather-wrapper
./bootstrap-dev.sh setup

# Start development
./bootstrap-dev.sh start

# View logs
./bootstrap-dev.sh logs

# Run tests
./bootstrap-dev.sh test
```

**Services available at:**
- Frontend: http://localhost:5173 (Vite dev server with HMR)
- Backend API: http://localhost:5000
- Health Check: http://localhost:5000/api/v1/health/ready

### Local Development

For direct local development without containers:

```bash
# Clone repository
git clone https://github.com/yourusername/msn-weather-wrapper.git
cd msn-weather-wrapper

# Backend setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pre-commit install

# Start backend
python api.py

# Frontend setup (separate terminal)
cd frontend
npm install
npm run dev
```

## Development Workflow

### Container Development Commands

```bash
# Daily workflow
./bootstrap-dev.sh start    # Start all services
./bootstrap-dev.sh logs     # Watch logs
./bootstrap-dev.sh stop     # Stop all services
./bootstrap-dev.sh restart  # Restart services

# Testing
./bootstrap-dev.sh test     # Run all tests
./bootstrap-dev.sh shell-api      # Backend shell
./bootstrap-dev.sh shell-frontend # Frontend shell

# Maintenance
./bootstrap-dev.sh rebuild  # Rebuild from scratch
./bootstrap-dev.sh clean    # Remove everything
```

### Making Code Changes

#### Backend Changes
1. Edit files in `src/msn_weather_wrapper/` or `api.py`
2. Flask auto-reloads automatically
3. Test your changes: `pytest tests/test_*.py`
4. Check types: `mypy src/`
5. Format code: `ruff format .`

#### Frontend Changes
1. Edit files in `frontend/src/`
2. Vite HMR updates instantly in browser
3. Test your changes: `npm run test:e2e`
4. Type check: `npm run type-check`
5. Build: `npm run build`

### Code Quality Tools

#### Python Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .
ruff check . --fix  # Auto-fix issues

# Type checking
mypy src/msn_weather_wrapper

# Run all quality checks
pre-commit run --all-files
```

#### TypeScript Code Quality

```bash
cd frontend

# Type checking
npm run type-check

# Build (includes type checking)
npm run build

# Lint (via ESLint/TypeScript compiler)
npm run type-check
```

## Project Structure

```
msn-weather-wrapper/
├── src/msn_weather_wrapper/    # Python package
│   ├── __init__.py             # Package exports
│   ├── client.py               # Weather client
│   ├── models.py               # Pydantic models
│   └── py.typed                # Type marker
├── tests/                      # Test suite
│   ├── test_api.py             # API tests
│   ├── test_client.py          # Client tests
│   ├── test_models.py          # Model tests
│   ├── test_security.py        # Security tests
│   └── test_integration.py     # Integration tests
├── frontend/                   # React application
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── data/               # City database
│   │   ├── App.tsx             # Main app
│   │   └── main.tsx            # Entry point
│   ├── tests/e2e/              # Playwright tests
│   ├── Containerfile           # Production container
│   └── Containerfile.dev       # Dev container
├── api.py                      # Flask REST API
├── bootstrap-dev.sh            # Dev environment script
├── Containerfile               # Production container
├── Containerfile.dev           # Dev container
├── podman-compose.yml          # Production compose
├── pyproject.toml              # Python config
└── docs/                       # Documentation
```

## Testing

### Backend Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_api.py -v

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_api.py::test_health_check -v

# Run security tests only
pytest tests/test_security.py -v
```

### Frontend Testing

```bash
cd frontend

# Install Playwright (first time)
npx playwright install

# Run E2E tests
npm run test:e2e

# Run with UI (interactive)
npm run test:e2e:ui

# Run in headed mode (see browser)
npm run test:e2e:headed

# Run specific test
npx playwright test tests/e2e/weather.spec.ts
```

### Integration Testing

```bash
# Start the API first
python api.py  # or ./bootstrap-dev.sh start

# Run integration tests
pytest tests/test_integration.py -v
```

## Adding Features

### Adding a Backend Feature

1. **Write the code**
   ```python
   # src/msn_weather_wrapper/client.py
   def new_feature(self):
       """New feature implementation."""
       pass
   ```

2. **Add tests**
   ```python
   # tests/test_client.py
   def test_new_feature():
       client = WeatherClient()
       result = client.new_feature()
       assert result is not None
   ```

3. **Update types**
   ```python
   # src/msn_weather_wrapper/models.py
   class NewModel(BaseModel):
       field: str
   ```

4. **Add API endpoint** (if needed)
   ```python
   # api.py
   @app.route('/api/v1/new-endpoint')
   def new_endpoint():
       return jsonify({"status": "ok"})
   ```

5. **Update documentation**
   - Update `docs/API.md` for new endpoints
   - Update `README.md` with usage examples
   - Update `CHANGELOG.md`

### Adding a Frontend Feature

1. **Create component**
   ```typescript
   // frontend/src/components/NewComponent.tsx
   export function NewComponent() {
       return <div>New Feature</div>;
   }
   ```

2. **Add types**
   ```typescript
   // frontend/src/types.ts
   export interface NewType {
       field: string;
   }
   ```

3. **Add E2E test**
   ```typescript
   // frontend/tests/e2e/new-feature.spec.ts
   test('new feature works', async ({ page }) => {
       await page.goto('/');
       // Test implementation
   });
   ```

4. **Update styles**
   ```css
   /* frontend/src/components/NewComponent.css */
   .new-component {
       /* Styles */
   }
   ```

## Dependency Management

### Python Dependencies

**Add production dependency:**
```bash
# Edit pyproject.toml, add to dependencies = [...]
pip install -e .

# Or install directly
pip install package-name
```

**Add development dependency:**
```bash
# Edit pyproject.toml, add to [project.optional-dependencies] dev = [...]
pip install -e ".[dev]"
```

### Node.js Dependencies

**Add production dependency:**
```bash
cd frontend
npm install package-name
```

**Add development dependency:**
```bash
cd frontend
npm install --save-dev package-name
```

## Debugging

### Backend Debugging

**Using print statements:**
```python
print(f"Debug: {variable}")
```

**Using logging:**
```python
import structlog
logger = structlog.get_logger()
logger.info("debug message", variable=value)
```

**Using ipdb:**
```python
import ipdb; ipdb.set_trace()
```

**In container:**
```bash
./bootstrap-dev.sh shell-api
ipython  # Interactive Python
```

### Frontend Debugging

**Browser DevTools:**
- Open DevTools (F12)
- Console tab for logs
- Network tab for API calls
- React DevTools extension

**TypeScript errors:**
```bash
npm run type-check
```

**Vite issues:**
```bash
# Clear Vite cache
rm -rf frontend/node_modules/.vite
npm run dev
```

## Common Tasks

### Update Dependencies

**Python:**
```bash
# Update all dependencies
pip install --upgrade -e ".[dev]"

# Update specific package
pip install --upgrade package-name
```

**Node.js:**
```bash
cd frontend
npm update
```

### Add Pre-commit Hook

```bash
# Install pre-commit hooks
pre-commit install

# Update hooks
pre-commit autoupdate

# Run manually
pre-commit run --all-files
```

### Generate Documentation

```bash
# Install MkDocs
pip install mkdocs-material

# Serve locally
mkdocs serve

# Build static site
mkdocs build

# Deploy to GitHub Pages
mkdocs gh-deploy
```

### Generate SBOM

```bash
# Generate all SBOMs
./tools/generate_sbom.sh

# View summary
cat sbom_output/SBOM_SUMMARY_*.md
```

## Containerized Development Details

### Container Architecture

**API Container:**
- Base: Python 3.12 slim
- Port: 5000
- Includes: Flask, pytest, ipython, all dev tools
- Volume: `./src` mounted to `/app/src`

**Frontend Container:**
- Base: Node 20 Alpine
- Port: 5173
- Includes: Vite, React, Playwright
- Volume: `./frontend/src` mounted to `/app/src`

### Volume Mounts

All source code is mounted for hot reload:
```
./src → /app/src
./api.py → /app/api.py
./tests → /app/tests
./frontend/src → /app/src (frontend)
./frontend/tests → /app/tests (frontend)
```

### Environment Variables

**API Container:**
- `FLASK_ENV=development`
- `FLASK_DEBUG=1`
- `PYTHONUNBUFFERED=1`

**Frontend Container:**
- `NODE_ENV=development`

## Troubleshooting

### Common Issues

**Issue: Tests fail with import errors**
```bash
# Solution: Reinstall in editable mode
pip install -e ".[dev]"
```

**Issue: Frontend won't start**
```bash
# Solution: Reinstall dependencies
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue: Container won't build**
```bash
# Solution: Clean rebuild
./bootstrap-dev.sh clean
./bootstrap-dev.sh setup
```

**Issue: Port already in use**
```bash
# Find process using port
lsof -i :5000  # or :5173

# Kill process
kill -9 <PID>

# Or change port in podman-compose.dev.yml
```

**Issue: Changes not reflected**
```bash
# Container dev: Check volume mounts
podman inspect msn-weather-api-dev | grep Mounts

# Local dev: Restart servers
# Ctrl+C and restart python api.py or npm run dev
```

## Contributing

### Before Submitting PR

1. ✅ All tests pass: `pytest`
2. ✅ Code formatted: `ruff format .`
3. ✅ No lint errors: `ruff check .`
4. ✅ Types valid: `mypy src/`
5. ✅ Coverage maintained: `pytest --cov=src`
6. ✅ Frontend tests pass: `npm run test:e2e`
7. ✅ Documentation updated
8. ✅ CHANGELOG.md updated

### PR Guidelines

- Clear title describing the change
- Description explaining what and why
- Link related issues
- Include tests for new features
- Update documentation
- Keep commits focused and atomic

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Max line length: 100 characters
- Use ruff for formatting and linting

**TypeScript:**
- Follow TypeScript best practices
- Use strict type checking
- Use functional components
- Prefer named exports

## Resources

- [Project README](../README.md)
- [API Documentation](API.md)
- [Testing Guide](TESTING.md)
- [Security Guide](SECURITY.md)
- [SBOM Guide](SYFT_GUIDE.md)
- [Changelog](CHANGELOG.md)

## Getting Help

- 🐛 [Report Issues](https://github.com/yourusername/msn-weather-wrapper/issues)
- 💬 [Discussions](https://github.com/yourusername/msn-weather-wrapper/discussions)
- 📖 [Full Documentation](https://yourusername.github.io/msn-weather-wrapper/)

---

Last updated: December 2, 2025
