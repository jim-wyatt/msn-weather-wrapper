# Scripts Directory

This folder contains the small utilities that help you **run**, **inspect**, and **report on** the project.

If you are new to the repo, think of `scripts/` as the **toolbox**, while the real application code lives in `src/` and `frontend/`.

## Most useful scripts

### `dev.sh`

The main daily-entry script for local development.

```bash
./dev.sh setup
./dev.sh start
./dev.sh test
./dev.sh logs
```

### `generate_reports.py`

Builds markdown reports from CI/test artifacts.

Common use:

```bash
python scripts/generate_reports.py --type coverage --input . --output docs/reports/coverage-report.md
```

### `generate_sbom.sh`

Generates a full software bill of materials (SBOM).

```bash
./scripts/generate_sbom.sh
```

### `generate_sbom_ci.sh`

A smaller, CI-friendly SBOM generator.

```bash
./scripts/generate_sbom_ci.sh
```

### `test_deployment.sh`

Builds the app with containers and runs the deployment-oriented integration check.

```bash
./scripts/test_deployment.sh
```

---

## Quick reference

| Script | When to use it |
| --- | --- |
| `dev.sh` | Daily local development |
| `generate_reports.py` | Turn test/CI artifacts into docs |
| `generate_sbom.sh` | Full SBOM generation |
| `generate_sbom_ci.sh` | Fast CI/security SBOM check |
| `test_deployment.sh` | Verify the containerized deployment |

---

## Beginner tip

If you are asking **"where do I start?"**:

1. Read `README.md`
2. Explore `src/msn_weather_wrapper/`
3. Check `tests/` for examples
4. Use `scripts/` only when you need project tooling

For more detail, see:

- [Project Structure Guide](../docs/PROJECT_STRUCTURE.md)
- [Development Guide](../docs/DEVELOPMENT.md)
- [SBOM Guide](../docs/SYFT_GUIDE.md)

These are the best next reads for most contributors.
