# Semantic Versioning Guide

This project follows [Semantic Versioning 2.0.0](https://semver.org/).

## Automated Versioning (Primary Method)

**The project uses automated PR-based versioning** where every merged pull request automatically increments the version and publishes to PyPI. See [AUTOMATED_VERSIONING.md](AUTOMATED_VERSIONING.md) for the complete guide.

**Quick summary:**
- The merged PR's title determines version bump type
- Major (breaking changes): `feat!:` title
- Minor (new features): `feat:` title
- Patch (bug fixes): `fix:` title (default)

## Manual Release Process (Alternative)

If you need to release manually without the automated system:

## Version Format

```
MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
```

- **MAJOR**: Breaking API changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)
- **PRERELEASE**: alpha, beta, rc (optional)
- **BUILD**: Build metadata (optional)

## Release Process

### Automated Release (Primary Method)

The project uses automated PR-based versioning. When a PR is merged to main:

1. **Auto-Version Workflow Triggers**
   - `ci.yml` dispatches `auto-version-release.yml` after a successful run on main
   - Determines version bump from the PR title

2. **Version Bump PR Created**
   - The workflow creates a PR with version updates
   - Updates `pyproject.toml` and `backend/__init__.py`
   - Auto-merge is enabled

3. **Automatic Tag Creation**
   - When the version bump PR merges, a git tag is created (e.g., `v1.2.3`)

4. **Publish Workflow Runs Automatically** (`publish-release.yml`)
   - Build Python package
   - Publish to PyPI
   - Create GitHub Release with artifacts

See [AUTOMATED_VERSIONING.md](AUTOMATED_VERSIONING.md) for complete details.

### Manual Release Process

If you need to release manually:

### 1. Update Version

Edit `pyproject.toml`:

```toml
[project]
version = "1.2.3"  # Update this line
```

Also update `__version__` in `backend/__init__.py` to the same value.

### 2. Update Changelog

Edit `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com/):

```markdown
## [1.2.3] - 2024-01-15

### Added
- New feature descriptions

### Changed
- Modified behavior descriptions

### Fixed
- Bug fix descriptions

### Security
- Security fix descriptions
```

### 3. Commit Changes

```bash
git add pyproject.toml backend/__init__.py CHANGELOG.md
git commit -m "chore: bump version to 1.2.3"
git push origin main
```

### 4. Create Release Tag (Manual Process Only)

**Note**: This step is automated when using the Automated Release workflow.

```bash
# Create annotated tag
git tag -a v1.2.3 -m "Release version 1.2.3"

# Push tag to trigger release
git push origin v1.2.3
```

### 5. Automated CI/CD Pipeline

Pushing the tag triggers two workflows:

1. **`publish-release.yml`**
   - **Set version** - Writes the tag version into `pyproject.toml` for the build
   - **Build package** - Creates wheel and source distribution
   - **Check package** - Runs `twine check`
   - **Publish to PyPI** - Uploads package automatically (trusted publishing)
   - **Create GitHub Release** - Publishes release with artifacts
2. **`ci.yml`**
   - **Run tests** - Tests and security scans
   - **Build containers** - Pushes the image with semantic version tags:
     - `ghcr.io/owner/repo:1.2.3` (exact version)
     - `ghcr.io/owner/repo:1.2` (minor version)
     - `ghcr.io/owner/repo:1` (major version)

## Version Increment Guidelines

### MAJOR Version (X.0.0)

Increment when making **breaking changes**:

- Removing endpoints or parameters
- Changing response formats
- Renaming models or fields
- Changing error codes
- Removing deprecated features
- Changing authentication methods

**Example:**

```python
# Before (v1.x.x)
@router.get("/weather/{city}")
def get_weather(city: str):
    return {"city": city, "temp": 20}


# After (v2.0.0) - Breaking change: response format changed
@router.get("/weather/{city}")
def get_weather(city: str):
    return {"location": {"name": city}, "current": {"temperature": 20}}
```

### MINOR Version (0.X.0)

Increment when adding **new features** (backward compatible):

- Adding new endpoints
- Adding optional parameters
- Adding new response fields (without removing old ones)
- Adding new models
- Deprecating features (but not removing)
- Performance improvements

**Example:**

```python
# v1.1.0 - Added new optional parameter
@router.get("/weather/{city}")
def get_weather(city: str, units: str = "metric"):  # New optional parameter
    return {"city": city, "temp": 20, "units": units}
```

### PATCH Version (0.0.X)

Increment when fixing **bugs** (backward compatible):

- Bug fixes
- Documentation fixes
- Internal refactoring
- Security patches
- Dependency updates (patch level)

**Example:**

```python
# v1.0.1 - Bug fix
@router.get("/weather/{city}")
def get_weather(city: str):
    city = city.strip()  # Fix: handle whitespace in city names
    return {"city": city, "temp": 20}
```

## Prerelease Versions

Use prerelease identifiers for testing:

### Alpha (Early Testing)

```bash
# First alpha of v1.2.0
git tag -a v1.2.0-alpha.1 -m "Alpha release 1 for v1.2.0"
```

- Unstable, may have missing features
- For internal testing only
- Not recommended for production

### Beta (Feature Complete)

```bash
# First beta of v1.2.0
git tag -a v1.2.0-beta.1 -m "Beta release 1 for v1.2.0"
```

- Feature complete but may have bugs
- For wider testing
- Not recommended for production

### Release Candidate (Final Testing)

```bash
# First release candidate for v1.2.0
git tag -a v1.2.0-rc.1 -m "Release candidate 1 for v1.2.0"
```

- Nearly production-ready
- Only critical bug fixes
- Ready for production testing

## Container Image Tags

The build workflow (`build.yml`) creates multiple tags:

| Tag Pattern | Example | Purpose |
|-------------|---------|---------|
| `X.Y.Z` | `1.2.3` | Exact version (immutable) |
| `X.Y` | `1.2` | Latest patch in minor version |
| `X` | `1` | Latest minor in major version |
| `latest` | `latest` | Latest build from `main` |
| `X.Y.Z-alpha.N` | `1.2.0-alpha.1` | Alpha prerelease |
| `X.Y.Z-beta.N` | `1.2.0-beta.1` | Beta prerelease |
| `X.Y.Z-rc.N` | `1.2.0-rc.1` | Release candidate |

### Usage Examples

```bash
# Pin to exact version (recommended for production)
docker pull ghcr.io/owner/msn-weather-wrapper:1.2.3

# Use latest patch version (auto-updates with patches)
docker pull ghcr.io/owner/msn-weather-wrapper:1.2

# Use latest minor version (auto-updates with new features)
docker pull ghcr.io/owner/msn-weather-wrapper:1

# Use latest build from main (not recommended for production)
docker pull ghcr.io/owner/msn-weather-wrapper:latest

# Test prerelease
docker pull ghcr.io/owner/msn-weather-wrapper:1.2.0-rc.1
```

## PyPI Publishing

Packages are automatically published to PyPI on tagged releases.

### Trusted Publishing

Publishing uses PyPI trusted publishing (OIDC) through the `pypi` environment in `publish-release.yml`. No `PYPI_TOKEN` secret is used. See [PYPI_SETUP.md](PYPI_SETUP.md) for how to configure the trusted publisher.

### First Release Setup

For the first release, you need to manually upload a package to claim the project name:

```bash
# Build package
python -m build

# Upload to PyPI (you'll be prompted for credentials)
python -m twine upload dist/*
```

After the first manual upload, all subsequent releases will be automated.

## Version Validation

The release workflows rely on:

1. **Tag format** - `publish-release.yml` and `ci.yml` trigger on tags matching `v*.*.*`
2. **Version from tag** - The package version is taken from the tag, not validated against `pyproject.toml`
3. **Package check** - `twine check` must pass
4. **Unique version** - PyPI rejects a version that already exists

## Troubleshooting

### Version Mismatch

The publish workflow overwrites the version in `pyproject.toml` with the tag version at build time, so a mismatch does not abort the release. `__version__` in `backend/__init__.py` is not rewritten, so keep it in sync with the tag when releasing manually.

### PyPI Upload Fails

**Check:**

1. Is the PyPI trusted publisher configured correctly?
2. Does the version already exist on PyPI?
3. Is the package name available?

**Test locally:**

```bash
# Build package
python -m build

# Check package validity
python -m twine check dist/*

# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*
```

### Container Build Fails

**Check:**

1. Does the infra/containers/Containerfile exist?
2. Are there syntax errors in the infra/containers/Containerfile?
3. Check the `build.yml` job logs for details

## Best Practices

1. **Never reuse versions** - Once published, a version is immutable
2. **Test prereleases** - Use alpha/beta/rc for testing
3. **Update changelog** - Document all changes before releasing
4. **Pin dependencies** - Use exact versions in production
5. **Automate everything** - Let CI/CD handle releases
6. **Validate locally** - Test builds before pushing tags
7. **Communicate changes** - Write clear release notes

## Examples

### Patch Release (Bug Fix)

```bash
# 1. Fix the bug
vim backend/client.py

# 2. Update version
vim pyproject.toml  # 1.0.0 → 1.0.1

# 3. Update changelog
vim CHANGELOG.md
# Add:
# ## [1.0.1] - 2024-01-15
# ### Fixed
# - Fixed city name whitespace handling

# 4. Commit and tag
git add .
git commit -m "fix: handle whitespace in city names"
git push origin main
git tag -a v1.0.1 -m "Release version 1.0.1"
git push origin v1.0.1
```

### Minor Release (New Feature)

```bash
# 1. Implement feature
vim backend/client.py

# 2. Update version
vim pyproject.toml  # 1.0.1 → 1.1.0

# 3. Update changelog
vim CHANGELOG.md
# Add:
# ## [1.1.0] - 2024-01-20
# ### Added
# - Added forecast endpoint with 7-day predictions

# 4. Commit and tag
git add .
git commit -m "feat: add 7-day weather forecast endpoint"
git push origin main
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### Major Release (Breaking Change)

```bash
# 1. Implement breaking changes
vim backend/client.py

# 2. Update version
vim pyproject.toml  # 1.1.0 → 2.0.0

# 3. Update changelog
vim CHANGELOG.md
# Add:
# ## [2.0.0] - 2024-02-01
# ### Changed
# - **BREAKING**: Changed response format for weather endpoints
# - **BREAKING**: Renamed `temp` field to `temperature`
# - See MIGRATION.md for upgrade guide

# 4. Create migration guide
vim docs/MIGRATION.md

# 5. Commit and tag
git add .
git commit -m "feat!: redesign API response format"
git push origin main
git tag -a v2.0.0 -m "Release version 2.0.0"
git push origin v2.0.0
```

## References

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [PyPI Publishing Guide](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
