# Workflow Architecture

```mermaid
flowchart LR
    PR[Pull request] --> CI
    PUSH[Push to main] --> CI
    subgraph CI [ci.yml - CI/CD Pipeline]
        direction TB
        CH[Detect Changes] --> V[Version]
        CH --> Q[Code Quality]
        CH --> U[Unit Tests<br/>3.15 on PRs, 3.10-3.15 on main]
        CH --> S[Security Scans<br/>Bandit, Semgrep, pip-audit]
        V --> C[Container<br/>build once, Trivy+Grype gates,<br/>smoke + integration tests,<br/>push + attest on main]
        U --> D[Documentation<br/>strict build, reports + deploy on main]
        S --> D
        C --> D
        Q --> G[CI Gate]
        U --> G
        S --> G
        C --> G
        D --> G
        G --> R[Release<br/>main, releasable only:<br/>tag vX.Y.Z with RELEASE_TOKEN]
    end
    R -->|tag push| PUB
    subgraph PUB [publish-release.yml]
        direction TB
        B[Build sdist + wheel from tag, attest] --> P[Publish to PyPI<br/>trusted publishing]
        P --> GR[GitHub release<br/>notes from commits, image tag check]
    end
    SCHED[Weekly schedule / manual] --> PERF[performance.yml<br/>Locust load test, benchmarks]
    DEPS[Weekly schedule] --> DEP[dependencies.yml<br/>upgrade + lock regeneration PRs]
```

## Why it is shaped this way

- **One build per run.** The container image is built once and that build is scanned,
  smoke-tested, integration-tested and, on `main`, pushed. Earlier versions of the pipeline
  built it three times per run.
- **No bump commits.** The version is derived from the git tag, so a release is a tag push, not
  a pull request. That removes two full pipeline runs per release and the manual approval that
  used to be needed for the bump pull request.
- **Release only when something ships.** Documentation, CI and tooling merges are verified but
  do not produce a release.
- **Publish does not rebuild.** The tagged commit is the one the `main` run tested and pushed;
  the publish run builds the Python package from the tag and publishes it.
- **Performance tests are scheduled**, not on the merge path.

## Triggers

| Workflow | Trigger |
| --- | --- |
| `ci.yml` | pull requests to `main`; pushes to `main`; manual |
| `publish-release.yml` | tags `v*.*.*`; manual with a tag |
| `performance.yml` | Mondays 06:00 UTC; manual |
| `dependencies.yml` | Mondays 09:00 UTC; manual |

## Secrets and environment

- `RELEASE_TOKEN` (fine-grained PAT, Contents write) for the tag push.
- `pypi` environment (OIDC trusted publishing; branch `main` and tags `v*`).
- `GITHUB_TOKEN` read-only by default; jobs request what they need.

Mermaid node labels use `<br/>` line breaks; the site's Mermaid renderer keeps them legible.
