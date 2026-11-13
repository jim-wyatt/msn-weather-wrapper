# Automated Semantic Versioning

This project uses **automated semantic versioning** - every merged pull request automatically increments the version number and publishes a new release to PyPI.

## How It Works

When a PR is merged to `main`, the CI/CD pipeline (`ci.yml`) runs on the push and, once it succeeds, dispatches the Auto-Version and Release workflow (`auto-version-release.yml`), which:

1. **Determines the version bump type** based on the merged PR's title
2. **Increments the version** in `pyproject.toml` and `backend/__init__.py` following semantic versioning
3. **Opens and merges a version bump PR** against the main branch
4. **Creates a git tag** for the new version
5. **Triggers the publish workflow** (`publish-release.yml`) which builds and publishes to PyPI
6. **Dispatches the CI pipeline on the tag** (`ci.yml`) so the versioned container image (`X.Y.Z`, `X.Y`, `X`, `latest`) is pushed to GHCR; a tag pushed with the workflow token would not trigger it otherwise

## Version Bump Rules

The workflow follows [Semantic Versioning 2.0.0](https://semver.org/):

### Major Version (X.0.0) - Breaking Changes

Increments the major version and resets minor/patch to 0.

**Triggered by:**
- PR title: `feat!:`, `feature!:`, or `breaking!:` (with exclamation mark)

**Example:** `1.2.3` → `2.0.0`

**Use when:**
- Breaking API changes
- Incompatible changes to public interfaces
- Removing deprecated features
- Major architectural changes

### Minor Version (0.X.0) - New Features

Increments the minor version and resets patch to 0.

**Triggered by:**
- PR title: `feat:` or `feature:`

**Example:** `1.2.3` → `1.3.0`

**Use when:**
- Adding new features
- Adding new functionality (backwards compatible)
- Deprecating features (but not removing them)
- Substantial internal improvements

### Patch Version (0.0.X) - Bug Fixes & Maintenance

Increments only the patch version. **This is the default** if no specific indicators are found.

**Triggered by:**
- PR title: `fix:`, `bugfix:`, `chore:`, `perf:`, `refactor:`, `docs:`
- **Default for all other PRs**

**Example:** `1.2.3` → `1.2.4`

**Use when:**
- Bug fixes
- Performance improvements
- Refactoring
- Documentation updates
- Test improvements
- Dependency updates
- CI/CD improvements

## Priority Order

The workflow checks only the merged PR's title:

1. **PR Title** (conventional commit format, optional scope such as `feat(api):`)
2. **Default to patch** (if nothing matches)

PR labels and branch prefixes are not used to determine the bump.

## Examples

### Using Conventional Commit Titles

```bash
# Feature (minor bump)
gh pr create --title "feat: add temperature forecast"
# Result: 1.2.3 → 1.3.0

# Breaking change (major bump)
gh pr create --title "feat!: redesign API response format"
# Result: 1.2.3 → 2.0.0

# Bug fix (patch bump)
gh pr create --title "fix: correct humidity calculation"
# Result: 1.2.3 → 1.2.4
```

## Workflow Integration

### Creating a PR with Proper Versioning

```bash
# For a bug fix (patch):
git checkout -b fix/issue-description
# ... make changes ...
git commit -m "fix: description of fix"
gh pr create --title "fix: description"

# For a new feature (minor):
git checkout -b feat/feature-name
# ... make changes ...
git commit -m "feat: description of feature"
gh pr create --title "feat: description"

# For a breaking change (major):
git checkout -b breaking/change-description
# ... make changes ...
git commit -m "feat!: description of breaking change"
gh pr create --title "feat!: description"
```

### What Happens After Merge

1. **CI/CD Pipeline runs on main** (`ci.yml`)
   - Runs all tests and security scans
   - Builds and pushes the container image
   - Deploys documentation
   - Dispatches the Auto-Version workflow

2. **Auto-Version workflow runs** (`auto-version-release.yml`)
   - Determines bump type
   - Updates `pyproject.toml` and `backend/__init__.py`
   - Opens and merges a version bump PR
   - Creates version tag
   - Dispatches the publish workflow

3. **Publish workflow runs** (`publish-release.yml`)
   - Builds Python package
   - Publishes to PyPI
   - Creates GitHub Release

4. **Release is live!**
   - PyPI: `pip install msn-weather-wrapper==X.Y.Z`
   - GitHub: Release with artifacts
   - Containers: `ghcr.io/jim-wyatt/msn-weather-wrapper:latest` (pushed by `ci.yml` on main)

## Monitoring Releases

### Check Version Bump Status

```bash
# View workflow runs
gh run list --workflow=auto-version-release.yml --limit 5

# View specific run
gh run view <run-id>
```

### Check Release Pipeline

```bash
# View CI/CD runs
gh run list --workflow=ci.yml --limit 5

# Check the publish workflow
gh run list --workflow=publish-release.yml --limit 5
```

### Verify Publication

```bash
# Check PyPI
pip index versions msn-weather-wrapper

# Check GitHub releases
gh release list --limit 5

# Check containers
gh api /user/packages/container/msn-weather-wrapper/versions
```

## Best Practices

### 1. Use Descriptive PR Titles

Good:
```
feat: add weather alerts endpoint
fix: correct temperature unit conversion
refactor: improve caching logic
```

Bad:
```
Updated code
Fixed stuff
Changes
```

### 2. Get the Title Prefix Right

- The PR title is the only input to the version bump
- Labels and branch names are for humans; they do not change the bump
- Edit the PR title before merging if the prefix is wrong

### 3. Group Related Changes

- Combine related fixes in one PR (single patch bump)
- Don't split one feature across multiple PRs (avoid unnecessary minor bumps)
- Use draft PRs for work-in-progress

### 4. Review Before Merging

- Every merge creates a new release
- Ensure all tests pass
- Review the version bump that will occur
- Consider if the change warrants immediate release

### 5. Handle Breaking Changes Carefully

- Document breaking changes thoroughly
- Update CHANGELOG.md
- Consider deprecation warnings before removal
- Coordinate with users for major versions

## Skipping Auto-Release

There is no opt-out; every merge to `main` releases. If a release must not happen, do not merge, or merge and accept the patch release. Deleting the tag after the fact does not cancel `publish-release.yml`, which is dispatched explicitly by the workflow right after the tag push.

### RELEASE_TOKEN, or opening the bump PR by hand

**Hands-free releases need a `RELEASE_TOKEN` secret.** Create a fine-grained personal access
token (GitHub → Settings → Developer settings → Fine-grained tokens) scoped to this repository
with *Contents: Read and write* and *Pull requests: Read and write* (nothing else; set an
expiry and rotate it), and store it as the repository secret `RELEASE_TOKEN`. With it the
workflow opens the bump pull request (so its CI runs on its own), merges it once `CI Gate`
passes, and pushes the tag with the same token, which triggers the publish and container-image
runs natively; the explicit dispatch steps are skipped.


The repository setting **Allow GitHub Actions to create and approve pull requests** is
disabled as part of the hardening baseline. Without a `RELEASE_TOKEN` secret (a GitHub App
token or fine-grained PAT with *Contents* and *Pull requests* write), the workflow can push
the `chore/version-bump-X.Y.Z` branch but cannot open the pull request, and fails at
"Create version bump pull request". Recovery:

```bash
gh pr create --base main --head chore/version-bump-X.Y.Z --title "chore: bump version to X.Y.Z"
gh workflow run auto-version-release.yml -f pr_title="<title of the merged PR>" -f pr_number=<n>
```

The re-run reuses the open PR, waits for `CI Gate`, merges, tags and dispatches the publish
and container-image runs. Do not merge anything else to `main` until the tag exists, or a
second release run computes a conflicting version. With `RELEASE_TOKEN` set none of this is
needed, and the bump PR's CI and the tag push also trigger on their own.

## Troubleshooting

### Release Waiting on the Version Bump PR

`main` requires the `CI Gate` status check. GitHub holds workflow runs on pull requests
opened with the default `GITHUB_TOKEN` until a maintainer approves them, so the version
bump PR shows **Approve and run workflows** and the release workflow waits.

- **To finish a release by hand:** approve the run on the version bump PR. The release
  workflow merges it once `CI Gate` passes, then tags and publishes. If the workflow has
  already timed out, re-run it; it reuses the open PR, or resumes at the tag step if the
  bump is already merged.
- **To make releases hands-off:** add a repository secret named `RELEASE_TOKEN` holding a
  GitHub App installation token or fine-grained personal access token with read and write
  access to *Contents* and *Pull requests* on this repository. The version bump PR is then
  opened with that token and its CI starts without approval.

### Version Already Exists

If the workflow reports "Version Already Exists":
- The calculated version was already tagged
- Check if someone manually created the tag
- The workflow will skip and not create a duplicate

### Tag Created But No Release

If tag is created but PyPI release fails:
1. Check the `publish-release.yml` run status
2. Look for build failures
3. PyPI trusted publishing configuration might need updating (see [PYPI_SETUP.md](PYPI_SETUP.md))

### Wrong Version Bump

If the version bumped incorrectly:
1. Check the merged PR's title prefix
2. Remember labels and branch names are ignored
3. Default is patch if nothing matches

To fix:
```bash
# Delete the tag
git push origin :refs/tags/vX.Y.Z

# Create a new PR with correct versioning indicators
```

## Related Documentation

- [Semantic Versioning Specification](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## Migrating from Manual Versioning

If you previously used manual version bumps:

1. **No action needed** - The workflow now handles all versioning
2. **Remove manual version bump PRs** - These are no longer necessary
3. **Update contribution docs** - Instruct contributors on PR title prefixes
4. **Communicate changes** - Inform team about new automated process
