# CI/CD Workflows

Three workflows, one pipeline per event.

## `ci.yml` — CI/CD Pipeline

Runs on every pull request and every push to `main` (and on demand).

| Job | What it does | PR | main |
| --- | --- | --- | --- |
| **Detect Changes** | Classifies the diff: documentation-only changes skip the heavy jobs; only changes to `backend/`, `frontend/`, `infra/`, `pyproject.toml` or `requirements.txt` are *releasable* | ✓ | ✓ |
| **Version** | Derives the version the run produces: on `main` the next semver from the latest tag and the merged PR's title (`feat:` → minor, `feat!:`/`breaking:` → major, else patch); `X.Y.Z.dev0` when nothing shippable changed; `0.0.0.dev0` on PRs | ✓ | ✓ |
| **Code Quality** | `ruff format --check --preview`, `ruff check`, `mypy --strict` | ✓ | ✓ |
| **Unit Tests** | unit, API and security tests with coverage; Python 3.15 on PRs, 3.10–3.15 on `main` | ✓ | ✓ |
| **Security Scans** | Bandit (HIGH gates), Semgrep (pipx-isolated), pip-audit, pip-licenses, evaluated by `scripts/evaluate_security_reports.py` | ✓ | ✓ |
| **Container** | builds the image **once** (version baked in via `APP_VERSION`), gates on fixable CRITICAL/HIGH (Trivy) and fixable CRITICAL (Grype), smoke-tests and integration-tests that build; on `main` also uploads Trivy SARIF/JSON, Syft SBOMs and the Grype report, then pushes the same build to GHCR (`sha-…`, `main`, and on a release `X.Y.Z`, `X.Y`, `X`, `latest`) with a signed provenance attestation | ✓ | ✓ |
| **Documentation** | `mkdocs build --strict`; on `main` renders the test, coverage, security, license and CI reports from this run's artifacts and deploys the site | ✓ | ✓ |
| **CI Gate** | the single status check the `main` ruleset requires; fails unless every job above succeeded (skipped is fine for documentation-only changes) | ✓ | ✓ |
| **Release** | on a green, releasable `main` run, tags `vX.Y.Z` at the merged commit using `RELEASE_TOKEN` | | ✓ |

Typical wall-clock: about 5 minutes for a pull request, 6 for a push to `main`, plus 2 for the release.

## `publish-release.yml` — Publish Release

Triggered by the tag that `ci.yml` pushes (or on demand with a tag). The tagged commit was
already tested, scanned and pushed as an image by the `main` run, so nothing is rebuilt:

1. build the sdist and wheel from the tag (hatch-vcs reads the version from git) and attest them;
2. publish to PyPI through the `pypi` environment (OIDC trusted publishing, no token);
3. check that `ghcr.io/jim-wyatt/msn-weather-wrapper:X.Y.Z` exists, write release notes from the
   commits since the previous tag, and create the GitHub release with the package attached.

## `performance.yml` — Performance Testing

Load tests (Locust) and benchmarks, weekly on Mondays at 06:00 UTC and on demand. Not part of
the merge path.

## `dependencies.yml` — Dependency Update

Weekly (Mondays 09:00 UTC): upgrades Python and npm dependencies, regenerates the hash-pinned
`requirements.txt`, runs the tests and opens pull requests. Dependabot covers pip, npm,
GitHub Actions (SHA pins) and the container base-image digests separately.

## Versioning

There is no version string in the repository. `pyproject.toml` declares the version as dynamic
and hatch-vcs derives it from the git tag (`vX.Y.Z` → `X.Y.Z`; untagged checkouts get
`X.Y.Z.devN`). The container image receives it as the `APP_VERSION` build argument. See
`docs/VERSIONING.md` and `docs/AUTOMATED_VERSIONING.md`.

## Secrets and settings

- **`RELEASE_TOKEN`** (required for hands-free releases): fine-grained PAT scoped to this
  repository with *Contents: Read and write*. The `Release` job pushes the tag with it so that
  `publish-release.yml` triggers (pushes made with `GITHUB_TOKEN` never trigger workflows).
  Without it the job fails with the manual `git tag … && git push` command.
- No PyPI token: trusted publishing via the `pypi` environment (restricted to `main` and `v*`).
- `GITHUB_TOKEN` defaults to read-only; each job requests the scopes it needs.
- Third-party actions are pinned to commit SHAs; Dependabot keeps the pins current.

## Branch protection

`main` is governed by a repository ruleset: required status check **`CI Gate`** (branch up to
date), CodeQL code-scanning results required, squash merges only, deletions and force-pushes
blocked. Do not add the individual job names as required checks; `CI Gate` aggregates them.

## Artifacts

| Artifact | From | Retention |
| --- | --- | --- |
| `security-reports` | Security Scans, every run | 3 days |
| `test-results-<python>` | Unit Tests (pushes, or failed PR runs) | 3 days |
| `coverage-reports` | Unit Tests (pushes) | 7 days |
| `container-security-reports` | Container (pushes): Trivy JSON, SBOMs, Grype report, integration JUnit | 30 days |
| `python-package` | Publish Release | 90 days (default) |

## Dependency graph

```text
changes ──┬──> version ───────────────┐
          ├──> quality ──────────────┐│
          ├──> unit ─────────────────┤├──> ci-gate ──> release (main, releasable) ──> tag ──> publish-release.yml
          ├──> security ─────────────┤│
          └──> container ──> docs ───┘┘
```
