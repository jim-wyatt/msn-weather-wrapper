# PyPI Publishing Setup Guide

Complete guide to setting up automated PyPI publishing for the MSN Weather Wrapper package.

---

## Overview

The project uses **GitHub's trusted publishing** (OIDC) for secure PyPI uploads with no stored secrets. The first release requires manual setup, but subsequent releases are fully automated.

---

## Quick Setup (First Release)

### Step 1: Create PyPI Account

1. Go to [PyPI.org](https://pypi.org/account/register/)
2. Register a new account
3. Verify your email address

### Step 2: Upload First Release Manually

The first release must be uploaded manually to claim the package name on PyPI.

```bash
# Install build tools
pip install build twine

# Build package
python -m build

# Upload to PyPI (interactive)
python -m twine upload dist/*
```

You'll be prompted for your PyPI username and password.

### Step 3: Configure Trusted Publishing (OIDC)

After the first manual upload:

1. Open the project's **Publishing** settings (Manage → Settings → Publishing, <https://pypi.org/manage/project/msn-weather-wrapper/settings/publishing/>)
2. Add a trusted publisher:
   - **Owner**: `jim-wyatt`
   - **Repository name**: `msn-weather-wrapper`
   - **Workflow name**: `publish-release.yml`
   - **Environment name**: `pypi` (the environment used by `publish-release.yml`)
3. Click **Add**

The publisher is active immediately. (Alternatively, skip the manual first upload: add a *pending* publisher with the same values under your account's Publishing settings, <https://pypi.org/manage/account/publishing/>, and the first automated release creates the project.)

### Step 4: Create the `pypi` GitHub environment

The `publish-pypi` job in `publish-release.yml` runs in the `pypi` environment, which is required and must exist in the repository:

1. Go to **Settings** → **Environments** → **New environment**
2. Name: `pypi`
3. Under **Deployment branches and tags**, select *Selected branches and tags* and allow branch `main` and tag pattern `v*`
4. Optionally add required reviewers or a wait timer

No repository secret is needed: the job requests an OIDC token (`id-token: write`) at release time and `pypa/gh-action-pypi-publish` exchanges it for a short-lived PyPI token. There is no `PYPI_TOKEN`.

### Step 5: Verify a published release

Each release's wheel and sdist carry a signed build-provenance attestation (`actions/attest` in `publish-release.yml`). Consumers can verify what they install:

```bash
pip download msn-weather-wrapper --no-deps
gh attestation verify msn_weather_wrapper-*.whl --repo jim-wyatt/msn-weather-wrapper
```

---

## Automated Publishing Workflow

Once OIDC is configured, releases are fully automatic:

1. Developer creates PR with changes
2. PR merged to main
3. ci.yml runs on `main`; on a green, releasable run its `Release` job tags `vX.Y.Z` (the version is derived from the tag by hatch-vcs), which:
   - Determines version bump
   - Creates and merges version bump PR
   - Pushes version tag
4. publish-release.yml triggers on tag:
   - Sets the package version from the tag
   - Builds Python package and attests its provenance
   - Uses OIDC to authenticate to PyPI (in the `pypi` environment)
   - Publishes to PyPI
   - Creates GitHub Release
5. Package available on PyPI ✅

---

## Version Management

### Conventional Commits

Use conventional commit prefixes in PR titles for automatic version bumping:

| Prefix | Type | Bump | Example |
|--------|------|------|---------|
| `feat:` | New Feature | Minor (0.X.0) | `feat: add weather alerts` |
| `fix:` | Bug Fix | Patch (0.0.X) | `fix: correct temp parsing` |
| `feat!:` | Breaking Feature | Major (X.0.0) | `feat!: redesign API` |
| `breaking!:` | Breaking Change | Major (X.0.0) | `breaking!: change response format` |
| `docs:` | Documentation | Patch (0.0.X) | `docs: update README` |
| `chore:` | Maintenance | Patch (0.0.X) | `chore: update deps` |

Default: Patch version (0.0.X)

---

## Testing Before Release

### Test Locally

```bash
# Build the package
python -m build

# Verify package integrity
python -m twine check dist/*

# Optional: Test on TestPyPI first
python -m twine upload --repository testpypi dist/*
```

### Verify Package Metadata

```bash
# Check what will be published
tar -tzf dist/*.tar.gz | head -20

# Verify wheel contents
unzip -l dist/*.whl | head -20
```

---

## Troubleshooting

### OIDC Configuration Issues

**Problem:** `publish-pypi` fails with `invalid-publisher` or `403 Forbidden`

**Solution:** The OIDC token's claims must match the trusted publisher exactly. Check, in order:

- The workflow filename on PyPI is `publish-release.yml` (not a display name)
- The environment name on PyPI is `pypi` and the job runs in that environment
- Owner is `jim-wyatt` and repository is `msn-weather-wrapper` (case-sensitive)
- The `publish-pypi` job still has `permissions: id-token: write`
- The `pypi` environment's deployment branch/tag rule allows the ref being published (`main` and tags `v*`); a tag that does not match the rule fails before the job starts
- Check the `publish-release.yml` logs for the exact claim PyPI rejected

### Package Upload Issues

**Problem:** Version already exists on PyPI

**Solution:**

- Versions are immutable on PyPI
- Create a new version bump (auto-version handles this)
- Cannot override or delete existing versions

**Problem:** Package name already taken

**Solution:**

- Update `project.name` in `pyproject.toml`
- Ensure uniqueness on PyPI
- Re-test with TestPyPI first

### Version Tag Issues

**Problem:** Tag not created automatically

**Solution:**

1. Check the `Release` job of the `CI/CD Pipeline` run on `main`
2. Verify version bump PR was merged
3. Manually create tag if needed:

```bash
git tag -a v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

---

## Manual Release Process

If automated release fails, you can manually publish:

```bash
# Build package
python -m build

# Get OIDC token (if using trusted publishing)
# This is handled automatically by the workflow
# For manual releases, use password/token auth

# Upload to PyPI
python -m twine upload dist/*

# Create GitHub release manually
gh release create v1.2.3 --title "Release v1.2.3" dist/*
```

---

## Security Best Practices

### ✅ Do

- Use **GitHub OIDC trusted publishing** (no tokens stored)
- Keep `pyproject.toml` version synchronized with git tags
- Review `publish-release.yml` logs for each release
- Test on TestPyPI before first production release
- Use conventional commits for clear version history

### ❌ Don't

- Never store PyPI tokens in GitHub secrets
- Never manually bump versions (let automation handle it)
- Never release without running full CI/CD pipeline
- Never use the same version twice

---

## Useful Commands

```bash
# Check current package version
grep '^version' pyproject.toml

# Build package locally
python -m build

# Check package contents
tar -tzf dist/*.tar.gz
unzip -l dist/*.whl

# Verify metadata
python -m twine check dist/*

# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# Upload to PyPI
python -m twine upload dist/*

# List releases
gh release list

# Check publish workflow runs
gh run list --workflow publish-release.yml
```

---

## Additional Resources

- [PyPI Documentation](https://pypi.org/help/)
- [Trusted Publishing Guide](https://docs.pypi.org/trusted-publishers/)
- [Python Packaging Guide](https://packaging.python.org/)
- [Hatch Documentation](https://hatch.pypa.io/)
- [twine Documentation](https://twine.readthedocs.io/)

---

## Related Documentation

- [CI/CD Workflows](WORKFLOW_DIAGRAM.md) - Complete workflow documentation
- [Versioning Guide](VERSIONING.md) - Version management process
- [Development Guide](DEVELOPMENT.md) - Local development setup
