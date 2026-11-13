# Automated Versioning and Releases

Every merge to `main` that changes something shippable is released automatically. There is no
version-bump commit and no bump pull request: **the version is the git tag**.

## How a release happens

1. A pull request is merged to `main` (squash). Its title decides the bump:
   `feat:` or `feature:` → minor, `feat!:` / `breaking:` → major, anything else → patch.
2. The `CI/CD Pipeline` run on `main`:
   - `Detect Changes` decides whether the merge is *releasable* (changes under `backend/`,
     `frontend/`, `infra/`, or to `pyproject.toml` / `requirements.txt`). CI, docs and tooling
     changes are verified but not released.
   - `Version` computes the next version from the latest `vX.Y.Z` tag and the bump type.
   - the image is built with that version baked in, scanned, smoke- and integration-tested,
     pushed to GHCR with `X.Y.Z`, `X.Y`, `X` and `latest` tags, and attested; tests, security
     scans and the docs deploy run alongside.
   - `Release` tags the merged commit `vX.Y.Z` using `RELEASE_TOKEN`.
3. The tag triggers `Publish Release`: build the sdist and wheel from the tag (hatch-vcs derives
   the version), attest, publish to PyPI (trusted publishing), verify the image tag exists, and
   create the GitHub release with notes generated from the commits since the previous tag.

Total: the pull request run, one `main` run and one short publish run.

## Where the version lives

- `pyproject.toml` declares `dynamic = ["version"]`; hatch-vcs reads it from git.
- `backend.__version__` is read from the installed distribution's metadata, so it matches the
  wheel or image it ships in (`0.0.0+unknown` only when the package is not installed at all).
- The container image gets the version through the `APP_VERSION` build argument
  (`SETUPTOOLS_SCM_PRETEND_VERSION` inside the build, since the build context has no `.git`).
  Local builds default to `0.0.0.dev0`.
- Untagged checkouts report `X.Y.Z.devN` (the version after the latest tag).

## RELEASE_TOKEN

Hands-free releases need a repository secret `RELEASE_TOKEN`: a fine-grained personal access
token scoped to this repository with *Contents: Read and write*. The `Release` job pushes the
tag with it; a tag pushed with the built-in `GITHUB_TOKEN` would not trigger
`publish-release.yml`. Without the secret the job fails and prints the manual command:

```bash
git tag -a vX.Y.Z <merged commit> -m "Release vX.Y.Z" && git push origin vX.Y.Z
```

The repository setting *Allow GitHub Actions to create and approve pull requests* can stay
disabled: nothing in the release path opens a pull request any more.

## Releasing by hand

Tag any commit on `main` (`vX.Y.Z`) and push it: `publish-release.yml` runs. To republish an
existing tag, run `Publish Release` on demand with the tag as input. The `Container` job only
pushes versioned image tags from a `main` run, so a hand-made tag for a commit whose `main` run
was not releasable will publish to PyPI but have no matching image tag (the publish run warns).

## Skipping a release

Merges that only touch documentation, workflows or tooling are not released. For a code change
that must not release on its own, batch it with the change it belongs to; there is no opt-out
label, and deleting a tag after the fact does not undo a PyPI publish.
