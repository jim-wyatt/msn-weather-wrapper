# GitHub Actions Workflows

This directory contains the automated CI/CD workflows for the MSN Weather Wrapper project.

## 🚀 Auto-Versioning & Release Workflow

### How It Works

The project uses **automatic semantic versioning** that triggers on every merged PR:

1. **PR Merged to Main** → `ci.yml` runs on the push; once it succeeds it dispatches `auto-version-release.yml`
2. **Version Bump Determined** → Based on the merged PR's title
3. **Version Bump PR Created** → Automated PR updates version files (`pyproject.toml`, `backend/__init__.py`)
4. **CI Gate Awaited and PR Merged** → the workflow waits for `CI Gate` on the bump PR (a maintainer must approve the run unless a `RELEASE_TOKEN` secret exists), then squash-merges it
5. **Tag Created** → Git tag `vX.Y.Z` is automatically created
6. **Release Published** → `publish-release.yml` builds and publishes to PyPI and GitHub Releases (container images are pushed by `ci.yml` on pushes to main)

### Version Bump Rules

The bump type is determined by the merged PR's title (Conventional Commits):

- `feat!:`, `feature!:`, or `breaking!:` → Major (X.0.0)
- `feat:` or `feature:` → Minor (0.X.0)
- `fix:`, `bugfix:`, `chore:`, `refactor:`, `perf:`, `docs:` → Patch (0.0.X - default)

PR labels and branch names are not consulted.

**Default**: If no indicators are found, defaults to **patch** version bump.

### Example PR Titles

```text
feat: add weather alerts feature          → 0.X.0 (minor)
fix: correct temperature parsing          → 0.0.X (patch)
feat!: redesign API endpoints             → X.0.0 (major)
chore: update dependencies                → 0.0.X (patch)
docs: improve README                      → 0.0.X (patch)
refactor: simplify client logic           → 0.0.X (patch)
```

## 📋 Workflow Files

### Core Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **`auto-version-release.yml`** | Dispatched by `ci.yml` after a successful run on main | Automatic version bumping and tagging |
| **`publish-release.yml`** | Tag push (v*.*.*) | Build package, publish to PyPI, create GitHub Release |
| **`ci.yml`** | Push to main, tags, PR | Full CI/CD pipeline (test, security, build, docs) |
| **`test.yml`**, **`security.yml`**, **`build.yml`**, **`deploy.yml`** | Called by `ci.yml` | Reusable pipeline stages |

### Supplementary Workflows

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **`dependencies.yml`** | Weekly schedule | Dependency update pull requests and audits |
| **`performance.yml`** | Called by `ci.yml` on push to main | Performance benchmarking and load testing |

## 🔄 CI/CD Pipeline (`ci.yml`)

The main CI/CD pipeline runs on:

- **Push to `main`** and version tags
- **Pull Requests to `main`**

### Pipeline Stages

1. **Detect Changes** - Classifies the diff; documentation-only PRs skip the heavy stages
2. **Smoke Tests** - Fast syntax and import validation
3. **Code Quality** - Ruff formatting and linting, mypy type checking
4. **Security** - Bandit, Semgrep, pip-audit, pip-licenses, plus the container image build with Trivy/Grype fixable-vulnerability gates
5. **Unit Tests** - Pytest across Python 3.10-3.15 (matrix on main, 3.15 only on PRs)
6. **Coverage** - Test coverage reporting with Codecov
7. **Docker Build** - Build and test container images
8. **SBOM Generation** - Software bill of materials (Syft, SPDX and CycloneDX)
9. **Build Documentation** - Build the MkDocs site
10. **Integration Tests** - API testing against the built container
11. **CI Gate** - Aggregates the results above; the only status check required by the `main` ruleset
12. **Performance Tests** - Load test and benchmarks (on main only)
13. **Deploy Documentation** - Generate reports and publish docs to GitHub Pages (on main only)

**Note**: Release jobs (build package, publish to PyPI, create GitHub Release) have been moved to `publish-release.yml` which triggers on tag push. This keeps the CI pipeline focused on testing and building documentation.

## 📦 Release Publishing (`publish-release.yml`)

Automatically triggered when a version tag (`v*.*.*`) is created:

1. **Build Package** - Create wheel and source distribution
2. **Publish to PyPI** - Upload to PyPI with trusted publishing (OIDC)
3. **Create GitHub Release** - Create release with package artifacts attached

This workflow runs **independently** from CI to keep release operations separate from the main test/build pipeline.

## 🛡️ Security Workflows

### `security.yml`

Called by `ci.yml` on push to main, tags, and pull requests:

- **Bandit**: Python security linting
- **Semgrep**: Static application security testing (SAST)
- **pip-audit**: Dependency vulnerability scanning
- **Trivy**: image scan on every run, fails on fixable CRITICAL/HIGH; SARIF upload on main/tags only
- **Grype**: image scan on every run, fails on fixable CRITICAL; SBOM-based report on main/tags only
- **License Report**: pip-licenses dependency license report

## 📊 Performance Testing (`performance.yml`)

Runs on pushes to main (called by `ci.yml`):

- Benchmarks with pytest-benchmark
- Regression alerting
- Load testing with Locust

## 🔄 Dependency Management (`dependencies.yml`)

Weekly automated updates:

- Frontend dependencies (npm)
- Python dependencies (pip)
- Security audits (pip-audit, npm audit)

GitHub Actions versions are updated by Dependabot (`.github/dependabot.yml`), and container base-image digests (docker ecosystem for `/infra/containers` and `/frontend`, weekly on Mondays, digest/patch only).

## 🎯 Best Practices

### For Contributors

1. **Use Conventional Commits**: Start PR titles with `feat:`, `fix:`, etc.
2. **Add Labels**: Label PRs with `feature`, `bugfix`, `breaking` for clarity (labels do not affect the version bump)
3. **Review Auto-Generated PRs**: Version bump PRs are automated but reviewable
4. **Monitor CI/CD**: Check workflow runs for any failures

### For Maintainers

1. **Branch Protection**: `main` ruleset: required `CI Gate` check, CodeQL results, squash merges only
2. **Secrets Management**:
   - No required secrets; optional `RELEASE_TOKEN` makes releases hands-off (see docs/AUTOMATED_VERSIONING.md)
   - PyPI uses trusted publishing (OIDC), no token storage required
3. **Bump PR Merge**: Version bump PRs are merged by the release workflow once `CI Gate` passes; set `RELEASE_TOKEN` to avoid the manual 'Approve and run workflows' step.
4. **Monitoring**: Watch workflow runs for any failures or issues

## ✨ Fully Automated Release Flow

The complete release process is now **fully automated** end-to-end:

```bash
1. Developer creates PR with code changes
   ↓
2. PR merged to main
   ↓
3. ci.yml passes on main and dispatches auto-version-release.yml:
   - Determines version bump (major/minor/patch)
   - Creates version bump PR
   - Waits for CI Gate on the bump PR
   ↓
4. Workflow squash-merges the bump PR
   ↓
5. Git tag (v1.2.3) created automatically
   ↓
6. publish-release.yml is dispatched for the tag:
   - Builds Python package
   - Publishes to PyPI
   - Creates GitHub Release with artifacts
   ↓
7. Release complete ✅
   - Package available on PyPI
   - Release notes on GitHub
   - No manual steps once RELEASE_TOKEN is configured; without it a
     maintainer approves the bump PR's workflow run
```

**Key Advantages:**

- ✅ No manual `gh workflow run` commands needed (a maintainer only approves the bump PR's workflow run when `RELEASE_TOKEN` is not configured)
- ✅ Separation of concerns: CI tests/builds, separate workflow handles releases
- ✅ Reduced complexity and fewer moving parts
- ✅ Consistent versioning across all releases

## 🐛 Troubleshooting

### Release not published automatically

**Check:**

1. Verify the tag exists: `git tag -l | grep v1.3.2`
2. Verify tag is on GitHub: `gh release list`
3. Check `publish-release.yml` workflow run: `gh run list --workflow publish-release.yml`

**If missing**: Tag may not have been created. Check `auto-version-release.yml` logs for version bump PR.

Is the bump PR showing **Approve and run workflows**? Approve it; the workflow resumes (re-run it if it timed out).

### Version bump PR not created

**Check:**

1. Did `ci.yml` finish successfully on `main`? The `trigger-auto-version` job only runs after the other jobs pass
2. Was the last merged PR itself a version bump (`chore: bump version to ...`)? Those are skipped
3. Are there any GITHUB_TOKEN permission issues?

**Solution**: Manually create a version bump PR or trigger `auto-version-release.yml` via workflow_dispatch

### PyPI publishing fails

**Check:**

1. Version already exists on PyPI → Versions are immutable
2. Token expired → Verify trusted publishing (OIDC) is configured
3. Package name conflicts → Ensure unique package name

**Solution**: The workflow logs will show the exact error

## 📚 Additional Documentation

- [CI/CD Pipeline Details](./README.md)
- [Security Scanning Guide](../../docs/SECURITY.md)
- [Contributing Guidelines](../../CONTRIBUTING.md)
- [Versioning Guide](../../docs/VERSIONING.md)

## 🔗 Useful Links

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [Python Semantic Release](https://python-semantic-release.readthedocs.io/)
