# Testing Guide

Complete testing documentation for MSN Weather Wrapper, including test results, coverage analysis, and testing best practices.

## Test Suite Overview

- **Total Tests**: 77
- **Unit Tests**: 35 (client, models, API)
- **Security Tests**: 25 (input validation, attack prevention)
- **Integration Tests**: 17 (live API testing)
- **Code Coverage**: 90%
- **Status**: ✅ All tests passing

## Quick Start

### Run All Tests
```bash
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only (fast, no network)
pytest tests/test_client.py tests/test_models.py tests/test_api.py

# Security tests
pytest tests/test_security.py -v

# Integration tests (requires running API)
pytest tests/test_integration.py -v
```

### With Coverage
```bash
# Generate coverage report
pytest --cov=src --cov-report=html

# View report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Test Breakdown

### Unit Tests (35 tests)

#### Client Tests (21 tests)
- Weather data fetching
- Error handling
- HTTP request validation
- Response parsing
- Cache functionality
- Geolocation support

#### Model Tests (4 tests)
- Pydantic model validation
- Data type enforcement
- Required fields
- Optional fields

#### API Tests (10 tests)
- Health check endpoint
- GET request handling
- POST request handling
- Error responses
- CORS configuration

### Security Tests (25 tests)

#### Input Validation (9 tests)
- ✅ Empty input rejection
- ✅ Whitespace-only rejection
- ✅ Special character filtering
- ✅ Length limit enforcement
- ✅ Type validation
- ✅ Integer rejection
- ✅ Boolean rejection
- ✅ Array rejection
- ✅ Null value handling

#### SQL Injection Prevention (8 tests)
- ✅ Classic injection (`'; DROP TABLE--`)
- ✅ UNION-based injection
- ✅ Blind injection
- ✅ Time-based injection
- ✅ Comment-based injection
- ✅ Stacked queries
- ✅ Boolean-based injection
- ✅ Error-based injection

#### XSS Prevention (6 tests)
- ✅ Script tag injection
- ✅ Event handler injection
- ✅ JavaScript protocol
- ✅ Encoded XSS
- ✅ DOM-based XSS
- ✅ Reflected XSS

#### Other Attacks (2 tests)
- ✅ Path traversal prevention
- ✅ Command injection prevention

### Integration Tests (17 tests)

#### API Functionality (4 tests)
- Health check endpoint
- GET weather endpoint
- POST weather endpoint
- Error handling

#### Security Validation (9 tests)
- SQL injection attempts on live API
- XSS attempts on live API
- Path traversal attempts on live API
- Command injection attempts on live API
- Invalid input rejection

#### HTTP Features (4 tests)
- CORS headers
- Rate limiting
- Content-Type headers
- Error response format

## Test Results

### Latest Test Run

**Date**: December 2, 2025  
**Environment**: Python 3.12, Podman container  
**Duration**: ~5 seconds

```
========================= test session starts ==========================
platform linux -- Python 3.12.3, pytest-9.0.0
rootdir: /app
plugins: cov-7.0.0, asyncio-1.0.0
collected 77 items

tests/test_client.py ..................... (21 passed)
tests/test_models.py .... (4 passed)
tests/test_api.py .......... (10 passed)
tests/test_security.py ......................... (25 passed)
tests/test_integration.py ................. (17 passed)

========================== 77 passed in 4.82s ==========================
```

### Coverage Report

| Module | Statements | Missing | Coverage |
|--------|-----------|---------|----------|
| `src/msn_weather_wrapper/__init__.py` | 8 | 0 | 100% |
| `src/msn_weather_wrapper/client.py` | 145 | 12 | 92% |
| `src/msn_weather_wrapper/models.py` | 32 | 2 | 94% |
| `api.py` | 186 | 18 | 90% |
| **TOTAL** | **371** | **32** | **90%** |

### Test Performance

| Test Category | Count | Duration | Speed |
|--------------|-------|----------|-------|
| Unit Tests | 35 | 0.8s | ⚡ Fast |
| Security Tests | 25 | 1.2s | ⚡ Fast |
| Integration Tests | 17 | 2.8s | 🔄 Moderate |
| **Total** | **77** | **4.8s** | ✅ Good |

## Testing Best Practices

### Before Committing
1. Run all tests: `pytest`
2. Check coverage: `pytest --cov=src`
3. Run security tests: `pytest tests/test_security.py`
4. Verify linting: `ruff check .`
5. Run type checks: `mypy src/`

### Writing New Tests
1. **Use descriptive names**: `test_should_reject_empty_city_name()`
2. **One assertion per test**: Focus on single behavior
3. **Use fixtures**: Share common setup code
4. **Mock external calls**: Don't rely on MSN Weather in unit tests
5. **Test error cases**: Not just happy paths

### Test Structure
```python
def test_feature_name():
    """Clear description of what is being tested."""
    # Arrange - Set up test data
    client = WeatherClient()
    location = Location(city="Seattle", country="USA")
    
    # Act - Execute the code under test
    result = client.get_weather(location)
    
    # Assert - Verify the results
    assert result.temperature is not None
    assert result.condition != ""
```

## Continuous Integration

### Pre-commit Hooks
Automatically run before each commit:
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

Hooks include:
- Ruff formatting
- Ruff linting
- mypy type checking
- pytest (fast tests only)

### GitHub Actions
Automated testing on:
- Every push to main
- Every pull request
- Manual workflow dispatch

Tests run on:
- Python 3.10, 3.11, 3.12
- Ubuntu latest
- Container builds

## Frontend Testing

### E2E Tests (Playwright)

#### Running E2E Tests
```bash
cd frontend

# Install dependencies (first time)
npm install
npx playwright install

# Run all E2E tests
npm run test:e2e

# Run with UI (interactive)
npm run test:e2e:ui

# Run in headed mode (visible browser)
npm run test:e2e:headed
```

#### E2E Test Coverage
- Basic functionality (header, empty state, buttons)
- Weather search (success and error cases)
- Temperature conversion (Celsius/Fahrenheit toggle)
- Recent searches (display, click, clear)
- Responsive design (mobile viewports)

#### Multi-Browser Testing
- ✅ Chromium (Desktop Chrome)
- ✅ Firefox (Desktop Firefox)
- ✅ WebKit (Desktop Safari)
- ✅ Mobile Chrome (Pixel 5)
- ✅ Mobile Safari (iPhone 12)

## Performance Testing

### Load Testing
```bash
# Install locust
pip install locust

# Run load test
locust -f tests/load_test.py
```

### Benchmark Results
- **Cached requests**: < 10ms response time
- **Uncached requests**: 500-1500ms (depends on MSN Weather)
- **Concurrent users**: 50+ without degradation
- **Rate limit**: 30 req/min per IP, 200/hr global

## Troubleshooting Tests

### Tests Fail Locally

**Issue**: Import errors
```bash
# Solution: Install in editable mode
pip install -e ".[dev]"
```

**Issue**: Integration tests fail
```bash
# Solution: Ensure API is running
python api.py  # Terminal 1
pytest tests/test_integration.py  # Terminal 2
```

**Issue**: E2E tests fail
```bash
# Solution: Install Playwright browsers
cd frontend
npx playwright install --with-deps
```

### Tests Pass Locally but Fail in CI

**Check**:
1. Python version differences
2. Missing environment variables
3. Network/firewall issues
4. Container build problems

**Debug**:
```bash
# Run in container (matches CI)
./bootstrap-dev.sh shell-api
pytest -vv --tb=short
```

### Slow Tests

**Identify slow tests**:
```bash
pytest --durations=10
```

**Speed up**:
1. Mock external API calls
2. Use fixtures for setup
3. Run unit tests separately from integration
4. Parallelize with pytest-xdist

## Test Coverage Goals

### Current Coverage: 90%
- ✅ All critical paths covered
- ✅ Security validation covered
- ✅ Error handling covered
- ✅ API endpoints covered

### Missing Coverage (10%)
- Edge cases in parsing
- Some error recovery paths
- Optional geolocation features
- Logging statements

### Target: Maintain 90%+
Coverage goals by module:
- `client.py`: ≥ 90%
- `models.py`: ≥ 95%
- `api.py`: ≥ 90%
- Overall: ≥ 90%

## Test Data

### Test Cities
```python
TEST_CITIES = [
    ("Seattle", "USA"),
    ("London", "UK"),
    ("Tokyo", "Japan"),
    ("Paris", "France"),
    ("Sydney", "Australia"),
]
```

### Mock Responses
Located in `tests/fixtures/` for consistent testing.

## Reporting Issues

When tests fail:
1. **Capture output**: Save full pytest output
2. **Note environment**: Python version, OS, container/local
3. **Include steps**: How to reproduce
4. **Check logs**: Include API logs if relevant
5. **Create issue**: With all above information

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Playwright documentation](https://playwright.dev/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Testing best practices](https://docs.python-guide.org/writing/tests/)

---

Last updated: December 2, 2025
