# DevSecOps Monitoring Dashboard

Comprehensive real-time monitoring dashboard for local development environment and GitHub CI/CD workflows with Red-Amber-Green (RAG) status indicators.

---

## Quick Start

```bash
# Generate local reports first
./dev.sh test      # Run tests with coverage
./dev.sh docs      # Generate all reports

# Launch the monitor
./dev.sh monitor
```

The dashboard auto-refreshes every 60 seconds and shows at-a-glance status using RAG indicators.

---

## RAG Status Indicators

### Legend

| Symbol | Color | Status | Meaning |
|--------|-------|--------|---------|
| ✅ | Green | Healthy/Passing | Everything is good |
| ⚠️ | Amber | Warning | Needs attention soon |
| ❌ | Red | Critical | Immediate action required |
| ○ | Grey | Unknown | Data not available |

### Status Thresholds

**Green (✅)** - Healthy/Passing
- Code coverage: 80%+
- All tests passing
- No critical security issues
- Services running and healthy

**Amber (⚠️)** - Warning/Needs Attention

- Code coverage: 60-79%
- Minor issues detected
- Partial services running
- Dependent vulnerabilities detected

**Red (❌)** - Critical/Failing

- Code coverage: <60%
- Failed tests
- Critical security vulnerabilities
- Services down or unhealthy

**Grey (○)** - Unknown/Not Available

- No data available
- Feature disabled
- Not yet scanned

---

## Monitored Items

### 1. Local Development Environment

#### Container Services

**Status**: Running/Stopped/Healthy/Unhealthy

**Checks**:
- API container status and health endpoint
- Frontend container status
- Podman availability

**RAG Thresholds**:
- 🟢 Green: Both services healthy
- 🟡 Amber: Services running but unhealthy, or partial
- 🔴 Red: Services stopped
- ⚪ Grey: Podman not available

#### Python Virtual Environment

**Status**: Active/Inactive/Not Configured

**Checks**:
- Virtual environment directory exists (the check looks for `venv/`; the project uses `.venv/`, so this row is grey until `dev.sh` is updated)
- Environment is currently activated

**RAG Thresholds**:
- 🟢 Green: Environment active
- 🟡 Amber: Environment exists but not activated
- 🔴 Red: Environment not configured

#### Git Working Directory

**Status**: Clean/Dirty

**Checks**:
- Staged changes
- Unstaged modifications
- Untracked files

**RAG Thresholds**:
- 🟢 Green: No uncommitted changes
- 🟡 Amber: Uncommitted changes present

### 2. Code Quality & Testing

#### Test Execution

**Status**: Pass/Fail/No Report

**Checks**:
- JUnit XML test results (`junit.xml`)
- Test pass/fail counts

**RAG Thresholds**:
- 🟢 Green: All tests passing
- 🔴 Red: Any test failures
- ⚪ Grey: No test report available

#### Code Coverage

**Status**: Percentage (0-100%)

**Checks**:
- HTML coverage report (`htmlcov/index.html`)
- Overall coverage percentage

**RAG Thresholds**:
- 🟢 Green: ≥ 80% coverage (Excellent)
- 🟡 Amber: 60-79% coverage (Good)
- 🔴 Red: < 60% coverage (Needs improvement)
- ⚪ Grey: No coverage report

### 3. Security & Compliance

#### SAST Security Scan

**Status**: Clean/Issues/No Report

**Checks**:
- Bandit security scan results
- Critical/High severity issues

**RAG Thresholds**:
- 🟢 Green: No critical vulnerabilities
- 🔴 Red: Critical issues found
- ⚪ Grey: No security report

#### Dependency Scan

**Status**: Clean/Vulnerabilities/Unchecked

**Checks**:
- pip-audit vulnerability scanning
- Known vulnerable packages

**RAG Thresholds**:
- 🟢 Green: No known vulnerabilities
- 🟡 Amber: Vulnerable packages detected
- ⚪ Grey: Not scanned (pip-audit not installed)

#### License Compliance

**Status**: Tracked/Not Available

**Checks**:
- License report (`artifacts/security-reports/licenses.json`)
- Number of dependencies tracked

#### SBOM

**Status**: Count/Not Available

**Checks**:
- Number of `*.json` SBOM files under `sbom_output/` (written by `scripts/generate_sbom.sh` or `scripts/generate_sbom_ci.sh`)

**RAG Thresholds**:
- 🟢 Green: One or more SBOM files present
- ⚪ Grey: No SBOM files

**RAG Thresholds**:
- 🟢 Green: Dependencies tracked
- ⚪ Grey: No license report

### 4. GitHub CI/CD Workflows

The dashboard fetches the latest completed runs from GitHub's public API (no authentication required), then reads the jobs of the most recent **`CI/CD Pipeline`** run (`.github/workflows/ci.yml`). The reusable workflows `security.yml`, `build.yml`, `performance.yml` and `deploy.yml` are `workflow_call`-only and never appear as runs of their own; they show up as jobs inside the `CI/CD Pipeline` run.

The `CI/CD` row shows four columns:

#### CI

**Source**: Conclusion of the latest completed `CI/CD Pipeline` workflow run

**Status**: `ok` / `fail` / `can` (cancelled) / `n/a`

**RAG Thresholds**:
- 🟢 Green: Latest run succeeded
- 🔴 Red: Latest run failed
- ⚪ Grey: Cancelled or no recent runs

#### Sec

**Source**: Job `Run Security Scans / Basic Security Checks` of that run (the `security.yml` SAST/dependency scans called by `ci.yml`)

**Status**: `ok` / `fail` / `can` / `skip` / `n/a`

**RAG Thresholds**:
- 🟢 Green: Job succeeded
- 🔴 Red: Job failed
- ⚪ Grey: Cancelled, skipped (for example a docs-only change) or not found

#### AutoVer

**Source**: Job `Trigger Auto-Version-Release` of that run (dispatches `auto-version-release.yml`; only present for pushes to `main`)

**Status**: `ok` / `fail` / `can` / `skip` / `n/a`

**RAG Thresholds**:
- 🟢 Green: Job succeeded
- 🔴 Red: Job failed
- ⚪ Grey: Cancelled, skipped or not present (pull request runs)

#### Perf

**Source**: Job `Performance Tests` of that run (`performance.yml`; only present for pushes to `main`)

**Status**: `ok` / `fail` / `can` / `skip` / `n/a`

**RAG Thresholds**:
- 🟢 Green: Job succeeded
- 🔴 Red: Job failed
- ⚪ Grey: Cancelled, skipped or not present (pull request runs)

---

## Usage

### Starting the Monitor

```bash
./dev.sh monitor
```

The dashboard will:
1. Display immediately with current status
2. Auto-refresh every 60 seconds
3. Cache GitHub API responses for 30 seconds to reduce API calls
4. Continue until you press `Ctrl+C`

### Keyboard Controls

- **Ctrl+C** - Exit the monitor

### Update Frequency

- **Local Checks**: Real-time on each refresh (60s)
- **GitHub API**: Cached for 30 seconds, refreshed as needed
- **Display Refresh**: Every 60 seconds

---

## GitHub API Details

The monitor uses GitHub's public REST API to fetch workflow status:

- **Endpoint**: `https://api.github.com/repos/{owner}/{repo}/actions/runs`
- **Authentication**: None required (public API)
- **Rate Limit**: 60 requests/hour for unauthenticated requests
- **Caching**: Responses cached for 30 seconds to minimize API usage
- **Data Fetched**: Latest 5 completed workflow runs

### API Response Handling

- Fetches only completed runs (`status=completed`, latest 5)
- Matches the `CI/CD Pipeline` workflow by name and extracts its conclusion (success/failure/cancelled)
- Fetches `/actions/runs/{run_id}/jobs` for that run (cached for 60 seconds under `~/.cache/msn-weather-wrapper/`) and matches the `Sec`, `AutoVer` and `Perf` jobs by name
- Falls back to "unknown" if the workflow or job is not found

---

## Prerequisites

### Required

- `bash` shell
- `curl` - For GitHub API calls
- `jq` - For JSON parsing
- `git` - For repository status

### Optional (for full functionality)

- `podman` - For container status
- `pip-audit` - For dependency vulnerability scanning
- Generated reports:
  - `htmlcov/index.html` - Coverage report
  - `junit.xml` - Test results
  - `artifacts/security-reports/bandit-report.json` - Security scan
  - `artifacts/security-reports/licenses.json` - License report

---

## Generating Reports

To generate local reports for monitoring:

```bash
# Run tests with coverage
./dev.sh test

# Generate all reports and documentation
./dev.sh docs
```

Security and license rows read `artifacts/security-reports/bandit-report.json` and `licenses.json`; `dev.sh docs` currently writes them to `security-results/` and `license-results/`, so copy them (or download the CI `security-reports` artifact with `gh run download <run-id> -n security-reports`) into `artifacts/security-reports/`:

```bash
mkdir -p artifacts/security-reports
cp security-results/bandit-report.json license-results/licenses.json artifacts/security-reports/
```

The `SBOM` column counts JSON files under `sbom_output/`; run `./scripts/generate_sbom.sh` or `./scripts/generate_sbom_ci.sh` to populate it.

---

## Example Output

The dashboard is a single 80x24 screen. The output below is illustrative (values vary):

```
================================================================================
 ⚡ DevSecOps • jim-wyatt/msn-weather-wrapper • 2026-04-20 14:30:45
 Branch main @ 634f1f7 • Refresh 60s • Ctrl+C to exit
--------------------------------------------------------------------------------
 Local  Ctnr ✅ ok | PyEnv ○ none | Git ✅ clean | PC ✅ on
 Quality Test ✅ pass | Cov ✅ 97% | mypy ✅ yes | ruff ✅ yes
 Security SAST ✅ ok | Deps ✅ clean | Lic ✅ 142 | SBOM ✅ 2
 CI/CD  CI ✅ ok | Sec ✅ ok | AutoVer ✅ ok | Perf ✅ ok
================================================================================
```

Row by row:

- **Local**: container status (`Ctnr`), virtual environment (`PyEnv`), git working tree (`Git`, dirty trees show `staged/unstaged/untracked` counts) and pre-commit hook installation (`PC`).
- **Quality**: test result from `junit.xml`, coverage from `htmlcov/index.html`, and whether `mypy` and `ruff` are available.
- **Security**: Bandit result (`SAST`), pip-audit (`Deps`), license report package count (`Lic`) and SBOM file count (`SBOM`).
- **CI/CD**: `CI | Sec | AutoVer | Perf` from the latest `CI/CD Pipeline` run, as described above.

---

## Troubleshooting

### No data available for local checks

Generate reports first:

```bash
./dev.sh test      # Generates junit.xml and htmlcov/
./dev.sh docs      # Generates all reports
```

### GitHub API rate limit

The public API allows 60 requests/hour. With 30-second caching, you can run the monitor continuously for hours without hitting the limit.

### jq not found

Install jq for JSON parsing:

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# Fedora
sudo dnf install jq
```

### Container status shows "disabled"

Ensure Podman is installed:

```bash
# Ubuntu/Debian
sudo apt-get install podman

# macOS
brew install podman

# Fedora
sudo dnf install podman
```

### No GitHub data

Check internet connectivity and verify API endpoint:

```bash
curl -s https://api.github.com/repos/jim-wyatt/msn-weather-wrapper/actions/runs | jq '.workflow_runs[0]'
```

---

## Integration with CI/CD

The monitor dashboard is designed for local development but aligns with CI/CD workflows:

1. **Local Testing** - Run tests and generate reports locally
2. **Monitor Status** - Use dashboard to verify everything is green
3. **Push Changes** - Commit and push to GitHub
4. **Watch Workflows** - Monitor dashboard shows GitHub workflow status
5. **Iterate** - Fix any red/amber items and repeat

---

## Development Workflow

### Pre-Push Checklist

```bash
# 1. Generate latest reports
./dev.sh test
./dev.sh docs

# 2. Launch monitor
./dev.sh monitor

# 3. Check for green indicators
# - All local environment items green?
# - Code coverage above 80%?
# - No critical security issues?

# 4. If all green, push changes
git push

# 5. Monitor continues showing GitHub workflow status
```

### Continuous Development

Leave the monitor running in a dedicated terminal window during development for continuous visibility into:
- Container health
- Test results after each run
- Security scan results
- GitHub workflow status after push

---

## Performance Considerations

### API Rate Limiting

- GitHub public API: 60 requests/hour
- Caching: 30-second cache reduces API calls to ~2 per minute
- With caching: Can run continuously for many hours without hitting limit

### Local Performance

- Minimal CPU usage (mostly sleep)
- Quick status checks (<1 second per refresh)
- File-based caching for GitHub data

---

## Future Enhancements

Potential improvements for future versions:

- Docker support (in addition to Podman)
- Configurable refresh intervals
- Historical trend visualization
- Alert notifications for status changes
- GitHub Actions running status (not just completed)
- Support for GitHub authentication to increase API rate limits
- Export status to JSON/HTML report
- Custom threshold configuration
- Integration with other CI/CD platforms (GitLab, CircleCI, etc.)

---

## See Also

- [Development Guide](DEVELOPMENT.md) - Local development setup
- [Testing Documentation](TESTING.md) - Test suite and coverage
- [Security Documentation](SECURITY.md) - Security features and scanning
- [Container Development Setup](CONTAINER_DEV_SETUP.md) - Podman/Docker deployment
- [CI/CD Workflows](WORKFLOW_DIAGRAM.md) - GitHub Actions automation
