# Project Improvement Roadmap

This document tracks remaining optimization opportunities and future enhancements for MSN Weather Wrapper.

## ✅ Completed Phases

### Phase 1: CI/CD Optimizations (Completed)
- ✅ Composite action for Python environment setup
- ✅ Path-based workflow triggers
- ✅ Conditional test matrices (PR: 3.12 only, push: 3.10-3.12)
- ✅ Smoke tests for fast-fail validation
- ✅ Docker layer caching improvements

### Phase 2: Advanced CI/CD & Documentation (Completed)
- ✅ Docker image artifact sharing between workflows
- ✅ Consolidated security scanning workflow
- ✅ Optimized artifact retention policies (40% cost reduction)
- ✅ OpenAPI/Swagger documentation integration
- ✅ Comprehensive documentation updates

### Quick Wins (Completed)
- ✅ Fix pre-commit check-yaml hook for mkdocs.yml
- ✅ GitHub issue templates (bug report, feature request)
- ✅ CODEOWNERS file for automatic review assignments
- ✅ Dependabot configuration for automated updates

---

## 📋 Phase 3: Testing & Quality Enhancements

**Priority:** Medium
**Estimated Effort:** 2-3 days
**Goal:** Increase code coverage to 95%+ and strengthen test suite effectiveness

### 3.1 Coverage Improvements
**Estimated Time:** 4-6 hours

- [ ] **Cache Edge Cases** (lines in api.py: cache implementation)
  - Add tests for cache eviction scenarios
  - Test concurrent cache access patterns
  - Verify cache invalidation behavior
  - Test cache with various TTL configurations
  - **Files:** `tests/test_api.py`, `api.py`
  - **Current Coverage:** 85% → Target: 95%

- [ ] **Error Handler Edge Cases** (lines in api.py: error handlers)
  - Test rare HTTP status codes (429, 502, 503, 504)
  - Test malformed request body scenarios
  - Test invalid content-type headers
  - Test oversized request bodies
  - **Files:** `tests/test_api.py`, `tests/test_security.py`
  - **Current Coverage:** 88% → Target: 95%

- [ ] **Remove or Implement Dead Code**
  - Lines 287-290, 301-305 in api.py (future features placeholder)
  - **Options:**
    - A) Remove if not planned for immediate release
    - B) Implement and add tests
    - C) Mark with `# pragma: no cover` if intentionally untested
  - **Impact:** Immediate coverage increase of ~2-3%

### 3.2 Mutation Testing
**Estimated Time:** 3-4 hours

- [ ] **Install and Configure mutmut**
  ```bash
  pip install mutmut
  ```
  - Add mutmut configuration to `pyproject.toml`
  - Establish baseline mutation score

- [ ] **Run Mutation Tests**
  ```bash
  mutmut run
  mutmut results
  mutmut html  # Generate report
  ```
  - Identify weak test cases (survived mutants)
  - **Target:** 85%+ mutation score

- [ ] **Strengthen Test Suite**
  - Add assertions for survived mutants
  - Improve test specificity
  - Add boundary condition tests
  - **Files:** All test files based on mutation report

### 3.3 E2E Test Enhancements
**Estimated Time:** 2-3 hours

- [ ] **Visual Regression Testing**
  - Install Playwright Percy or similar
  - Add screenshot comparison tests
  - Test UI across different viewports
  - **Files:** `frontend/tests/e2e/`, new `visual.spec.ts`

- [ ] **Accessibility Testing**
  - Install `@axe-core/playwright`
  - Add automated WCAG 2.1 Level AA tests
  - Test keyboard navigation flows
  - Test screen reader compatibility
  - **Files:** `frontend/tests/e2e/accessibility.spec.ts` (new)

**Phase 3 Exit Criteria:**
- Code coverage ≥ 95%
- Mutation score ≥ 85%
- All E2E tests include accessibility checks
- No uncovered dead code

---

## 🚀 Phase 4: Feature Additions

**Priority:** Low (Future Enhancements)
**Estimated Effort:** 2-4 weeks (varies by feature)
**Goal:** Add high-value features from CHANGELOG planned section

### 4.1 Multi-Day Forecasts
**Estimated Time:** 1 week

- [ ] **Backend Implementation**
  - Extend `WeatherClient` to fetch forecast data
  - Add `Forecast` Pydantic model with daily/hourly data
  - Add forecast endpoint: `GET /api/v1/weather/forecast`
  - Implement 7-day caching for forecast data
  - **Files:** `src/msn_weather_wrapper/client.py`, `models.py`, `api.py`

- [ ] **Frontend Implementation**
  - Add forecast display component
  - Add daily/hourly toggle
  - Add forecast chart visualization (Chart.js or similar)
  - **Files:** `frontend/src/components/WeatherForecast.tsx` (new)

- [ ] **Testing**
  - Unit tests for forecast parsing
  - API integration tests
  - E2E tests for forecast display
  - **Files:** `tests/test_client.py`, `tests/test_api.py`, `frontend/tests/e2e/`

- [ ] **Documentation**
  - Update API.md with forecast endpoints
  - Add Swagger docs for forecast
  - Update README with forecast feature
  - **Files:** `docs/API.md`, `docs/SWAGGER.md`, `README.md`

### 4.2 Weather Alerts & Notifications
**Estimated Time:** 1 week

- [ ] **Backend Implementation**
  - Parse weather alerts from MSN Weather
  - Add `WeatherAlert` Pydantic model
  - Add alerts endpoint: `GET /api/v1/weather/alerts`
  - Implement severity filtering (low, medium, high, extreme)
  - **Files:** `src/msn_weather_wrapper/client.py`, `models.py`, `api.py`

- [ ] **Frontend Implementation**
  - Add alert banner component
  - Add alert severity icons and colors
  - Add alert details modal
  - Add browser notification support (optional)
  - **Files:** `frontend/src/components/WeatherAlerts.tsx` (new)

- [ ] **Testing & Documentation**
  - Unit and integration tests
  - E2E tests for alert display
  - Update documentation
  - **Files:** Various test and doc files

### 4.3 User Accounts & Saved Locations
**Estimated Time:** 2 weeks

**Prerequisites:** Database (PostgreSQL/SQLite), authentication system

- [ ] **Database Setup**
  - Choose database (PostgreSQL recommended)
  - Design schema (users, locations, preferences)
  - Add SQLAlchemy ORM
  - Add Alembic for migrations
  - **Files:** `src/msn_weather_wrapper/db/` (new), `alembic/` (new)

- [ ] **Authentication**
  - Add JWT-based authentication
  - Add user registration/login endpoints
  - Add password hashing (bcrypt)
  - Add session management
  - **Files:** `src/msn_weather_wrapper/auth.py` (new), `api.py`

- [ ] **Saved Locations Feature**
  - Add CRUD endpoints for saved locations
  - Add default location preference
  - Add location groups/favorites
  - **Files:** `api.py`, `src/msn_weather_wrapper/db/models.py`

- [ ] **Frontend Implementation**
  - Add login/register forms
  - Add saved locations manager
  - Add user profile page
  - Add authentication state management
  - **Files:** `frontend/src/components/Auth/` (new), `frontend/src/components/SavedLocations/` (new)

- [ ] **Security & Testing**
  - Add authentication middleware
  - Add rate limiting per user
  - Add security tests for auth flows
  - Update integration tests with auth
  - **Files:** `tests/test_auth.py` (new), various test files

### 4.4 GraphQL API Support
**Estimated Time:** 1 week

- [ ] **GraphQL Setup**
  - Install Graphene-Python or Strawberry
  - Design GraphQL schema
  - Add GraphQL endpoint: `/graphql`
  - Add GraphiQL playground: `/graphiql`
  - **Files:** `src/msn_weather_wrapper/graphql/` (new), `api.py`

- [ ] **Implement Resolvers**
  - Weather by location resolver
  - Forecast resolver
  - Alerts resolver
  - Saved locations resolver (if implemented)
  - **Files:** `src/msn_weather_wrapper/graphql/resolvers.py`

- [ ] **Testing & Documentation**
  - GraphQL query/mutation tests
  - Update API documentation
  - Add GraphQL examples
  - **Files:** `tests/test_graphql.py` (new), `docs/API.md`

### 4.5 WebSocket Real-Time Updates
**Estimated Time:** 1 week

- [ ] **WebSocket Backend**
  - Add Flask-SocketIO or similar
  - Implement weather update events
  - Add alert notification events
  - Add connection management
  - **Files:** `api.py`, `src/msn_weather_wrapper/websocket.py` (new)

- [ ] **Frontend WebSocket Client**
  - Add WebSocket connection manager
  - Add real-time weather updates
  - Add reconnection logic
  - Add connection status indicator
  - **Files:** `frontend/src/websocket.ts` (new), `frontend/src/App.tsx`

- [ ] **Testing & Documentation**
  - WebSocket integration tests
  - E2E tests for real-time updates
  - Update documentation
  - **Files:** `tests/test_websocket.py` (new), `docs/API.md`

---

## 📊 Success Metrics

### Phase 3 (Testing & Quality)
- **Coverage:** 90% → 95%+
- **Mutation Score:** N/A → 85%+
- **Accessibility Score:** 100% (WCAG 2.1 Level AA)
- **E2E Tests:** 17 → 25+

### Phase 4 (Features)
- **API Endpoints:** 11 → 20+ (varies by implemented features)
- **Frontend Components:** 2 → 10+ (varies by implemented features)
- **Test Coverage:** Maintained at 95%+
- **Documentation:** All new features fully documented

---

## 🎯 Prioritization Guidelines

### High Priority (Do First)
- Phase 3: Testing & Quality Enhancements
  - Directly improves code reliability
  - Reduces bug risk
  - Enables safer feature development

### Medium Priority (Consider)
- Feature 4.1: Multi-Day Forecasts
  - High user value
  - Relatively low complexity
  - No breaking changes

### Low Priority (Future)
- Features 4.2-4.5
  - Nice-to-have enhancements
  - Higher complexity
  - May require infrastructure changes

---

## 📝 Notes

### Out of Scope (Performance Optimizations Excluded)
The following performance optimizations are intentionally **NOT** included as they require infrastructure changes:
- ❌ Redis for distributed caching
- ❌ Database for persistent recent searches
- ❌ APM/monitoring (Prometheus, Grafana)
- ❌ OpenTelemetry request tracing
- ❌ CDN for static assets

**Rationale:** Current performance is acceptable. These optimizations should be considered only if:
- Application experiences scale issues (>1000 req/min)
- Response times exceed acceptable thresholds (>500ms p95)
- Hosting costs become significant

### Version Planning
- **v1.1.0:** Phase 3 (Testing & Quality) + Feature 4.1 (Forecasts)
- **v1.2.0:** Features 4.2-4.3 (Alerts & User Accounts)
- **v2.0.0:** Features 4.4-4.5 (GraphQL & WebSocket) - Breaking changes

---

**Last Updated:** December 2, 2025
**Status:** Active Planning Document
**Owner:** @jim-wyatt
