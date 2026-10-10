# GitHub Actions CI/CD Pipeline

This directory contains the GitHub Actions workflows for automated testing, building, and deployment of the MSN Weather Wrapper project.

## Workflows

### 1. `ci.yml` - Main CI/CD Pipeline

**Triggers:**
- Push to `main` branch
- Version tags (`v*.*.*`)
- Pull requests to `main` (when backend, tests, scripts, infra, frontend, `pyproject.toml`, or workflow files change)
- Manual workflow dispatch

**Jobs:**

`ci.yml` is an orchestrator; each job calls a reusable workflow in this directory:

1. **test** - Calls `test.yml`: smoke tests, code quality (Ruff, mypy), unit and security tests on Python 3.10-3.12 (3.12 only on PRs), coverage with Codecov upload
2. **security** - Calls `security.yml`: Bandit, Semgrep, pip-audit, pip-licenses; on `main` and tags also a Trivy/Grype container scan
3. **build** - Calls `build.yml`: builds the container images, generates the source SBOM with Syft, builds the MkDocs documentation
4. **integration-tests** - Calls `test.yml` again with integration tests enabled (runs against the built container)
5. **performance** - Calls `performance.yml` (push to `main` only)
6. **deploy** - Calls `deploy.yml`: generates report pages and deploys documentation to GitHub Pages (push to `main` only)
7. **trigger-auto-version** - Dispatches `auto-version-release.yml` (push to `main` only)

**Artifacts:**
- `security-reports` - Bandit, Semgrep, pip-audit, and license reports
- `container-security-reports` - Trivy and Grype results
- `coverage-reports` - Coverage XML and markdown summary
- `sbom-reports` - SBOM files in multiple formats
- `documentation` - Built MkDocs site

### 2. `build.yml` - Container Build & Push

**Triggers:**
- Called by `ci.yml` (reusable workflow; no triggers of its own)

**Jobs:**

1. **docker-build** - Builds the unified container image
   - Unified image: Built from root infra/containers/Containerfile (includes API + Frontend + Nginx)
   - On `main` and version tags: pushes to GitHub Container Registry (ghcr.io) with provenance and SBOM attestations
   - On pull requests: builds the app, frontend, and Playwright images and smoke-tests the unified container
   - Tags: `latest`, `sha-{sha}`, branch name, version tags

2. **sbom** - Generates the source SBOM with Syft (SPDX and CycloneDX)

3. **docs** - Builds the MkDocs documentation with `mkdocs build --strict`

Container vulnerability scanning (Trivy with SARIF output, Grype) lives in the `container-scan` job of `security.yml`.

**Container Registry:**
- `ghcr.io/{owner}/{repo}:latest` (unified container with API + Frontend + Nginx)

### 3. `dependencies.yml` - Dependency Updates

**Triggers:**
- Scheduled: Every Monday at 9:00 AM UTC
- Manual workflow dispatch

**Jobs:**

1. **update-dependencies** - Updates Python dependencies
   - Runs `pip install --upgrade` for all packages
   - Runs the unit and security tests
   - Creates pull request with update summary

2. **update-frontend** - Updates frontend dependencies
   - Runs `npm update`
   - Builds frontend to verify changes
   - Creates pull request with outdated packages list

3. **security-audit** - Runs security audits
   - Python: pip-audit
   - Frontend: npm audit
   - Uploads audit reports as artifacts

**Pull Request Labels:**
- `dependencies` - All dependency updates
- `frontend` - Frontend-specific updates
- `automated` - Automated PRs

### 4. `performance.yml` - Performance Testing

**Triggers:**
- Called by `ci.yml` on pushes to `main` (reusable workflow; no triggers of its own)

**Jobs:**

1. **load-test** - Load testing with Locust
   - Simulates 20 concurrent users
   - 1-minute test duration
   - Tests weather endpoint and health check
   - Generates HTML report and CSV results

2. **benchmark** - Benchmark tests with pytest-benchmark
   - Runs performance benchmarks
   - Alerts on 150%+ performance regression

**Artifacts:**
- `load-test-results` - Locust HTML report and CSV files
- `benchmark-results` - JSON benchmark data

### 5. `auto-version-release.yml` and `publish-release.yml` - Versioning & Release

See [WORKFLOWS.md](./WORKFLOWS.md) for the automated versioning and release flow.

## Setup Instructions

### Prerequisites

1. **Enable GitHub Actions** in repository settings
2. **Enable GitHub Pages** (Settings → Pages → Source: Deploy from branch `gh-pages`)
3. **Enable Container Registry** (automatic with GitHub Actions)

### Optional: Codecov Integration

1. Sign up at [codecov.io](https://codecov.io)
2. Add repository to Codecov

The coverage job uploads with `fail_ci_if_error: false`; the workflow does not currently pass an upload token.

### Secrets Required

**Auto-configured (no action needed):**
- `GITHUB_TOKEN` - Automatically provided by GitHub Actions

**Not required:**
- PyPI publishing uses trusted publishing (OIDC) through the `pypi` environment, so no PyPI token is stored

### Branch Protection Rules

Recommended settings for `main` branch:

- ✅ Require pull request reviews (1 approver)
- ✅ Require status checks to pass:
  - `Run Tests / Code Quality`
  - `Run Tests / Unit Tests (Python 3.12)`
  - `Run Tests / Test Coverage`
  - `Build Artifacts / Build Docker Images`
  - `Integration Tests / Integration Tests`
- ✅ Require branches to be up to date
- ✅ Require linear history
- ✅ Include administrators

## Usage

### Running Workflows Manually

1. Go to **Actions** tab in GitHub
2. Select workflow from left sidebar
3. Click **Run workflow** button
4. Choose branch and click **Run workflow**

### Creating Releases

Releases are normally created automatically after a PR is merged (see [WORKFLOWS.md](./WORKFLOWS.md)). To trigger a release manually:

```bash
# Tag the commit
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0
```

This will:
- Run `publish-release.yml`: build the Python package, publish it to PyPI, and create a GitHub release with the package attached
- Run `ci.yml` for the tag: tests, security scans, and container image build and push

### Viewing Results

- **Test Results**: Actions → CI/CD Pipeline → Summary
- **Coverage**: Download `coverage-reports` artifact
- **Podman Images**: Packages tab in repository
- **Documentation**: https://jim-wyatt.github.io/msn-weather-wrapper/
- **SBOMs**: Release attachments or artifact downloads

## Workflow Dependencies

```
test ──────┐
           ├──> build ──┬──> integration-tests ──┐
security ──┘            │                        ├──> deploy ──> trigger-auto-version
                        └──> performance ────────┘
```

`performance`, `deploy`, and `trigger-auto-version` run only on pushes to `main`.

## Maintenance

### Updating Workflow Versions

Check for updates to GitHub Actions periodically:

```bash
# Check for action updates
gh extensions install mheap/gh-action-update
gh action-update --dry-run
```

### Monitoring Workflow Performance

- Monitor workflow run times in Actions tab
- Optimize slow jobs with caching or parallelization
- Use matrix strategies for multiple configurations

### Troubleshooting

**Podman container build failures:**
- Check infra/containers/Containerfile syntax
- Verify base image availability (python:3.12-slim-trixie, node:24-trixie-slim)
- Review multi-stage build logs in Actions
- Ensure frontend build completes successfully

**Test failures:**
- Check test logs in job output
- Download `coverage-reports` artifact
- Run tests locally: `pytest -v`

**Documentation deployment issues:**
- Verify GitHub Pages is enabled
- Check `gh-pages` branch exists
- Review MkDocs build logs

**Dependency update failures:**
- Check compatibility between packages
- Review test failures in PR
- Manually test updates locally

## Best Practices

1. **Keep workflows fast**: Use caching, parallelize jobs
2. **Fail fast**: Run quick checks (linting) before slow tests
3. **Use matrix builds**: Test multiple Python/Node versions
4. **Monitor costs**: Review Actions usage in billing
5. **Secure workflows**: Never commit secrets, use `GITHUB_TOKEN`
6. **Document changes**: Update this README when modifying workflows

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [GitHub Actions Marketplace](https://github.com/marketplace?type=actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
