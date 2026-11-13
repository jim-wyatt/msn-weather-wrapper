# Workflows

The pipeline is documented in [README.md](README.md) (jobs, artifacts, secrets, release flow).
Related guides: [docs/AUTOMATED_VERSIONING.md](../../docs/AUTOMATED_VERSIONING.md),
[docs/VERSIONING.md](../../docs/VERSIONING.md), [docs/SECURITY.md](../../docs/SECURITY.md).

## Release flow in one paragraph

Merge a pull request to `main`. The `main` run tests, scans, builds the image once, pushes it,
deploys the docs and, if anything shippable changed (`backend/`, `frontend/`, `infra/`,
`pyproject.toml`, `requirements.txt`), tags `vX.Y.Z` with `RELEASE_TOKEN`. The tag runs
`publish-release.yml`, which builds the Python package from the tag, publishes it to PyPI and
creates the GitHub release. No version-bump commit or pull request exists: the version is the tag.

## Troubleshooting

1. **No release after a merge?** Check the `Version` job summary: documentation, CI and tooling
   changes are not released by design. Otherwise the `Release` job tells you whether
   `RELEASE_TOKEN` is missing and prints the manual tag command.
2. **Tag exists but nothing published?** Open the `Publish Release` run for that tag, or re-run
   it on demand with the tag as input.
3. **Image tag missing?** The `Container` job of the `main` run pushes the versioned tags; the
   publish run only verifies they exist.
