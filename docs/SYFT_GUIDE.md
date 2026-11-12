# Syft Integration for MSN Weather Wrapper

## Overview

This project includes comprehensive Software Bill of Materials (SBOM) generation using [Syft](https://github.com/anchore/syft) by Anchore. SBOMs provide detailed inventories of all software components, dependencies, and metadata.

## What is Syft?

Syft is a CLI tool and Go library for generating SBOMs from container images and filesystems. It supports multiple output formats including:
- **SPDX** (Software Package Data Exchange)
- **CycloneDX**
- **Syft JSON**
- **Table** (human-readable)

## Quick Start

### Generate All SBOMs

```bash
./scripts/generate_sbom.sh
```

This will:
1. Check/install Syft automatically
2. Generate SBOMs for the container images (see the note below)
3. Generate SBOMs for source code
4. Generate SBOMs for Python packages
5. Create a summary report

> **Note:** The script currently targets the legacy `msn-weather-wrapper_api`/`_frontend` images; the project now ships a single unified image (compose service `app`, built from `infra/containers/Containerfile`). For the unified image, build it with `podman-compose -f infra/compose/podman-compose.yml build`, find the resulting tag with `podman images`, and run `syft <image built by compose> -o spdx-json`, or scan the published image directly with `syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest -o spdx-json`.

### View Results

```bash
# View summary
cat sbom_output/SBOM_SUMMARY_*.md

# View API packages (table format)
cat sbom_output/api_sbom_table_*.txt

# View frontend packages
cat sbom_output/frontend_sbom_table_*.txt
```

## Installation

### Automatic Installation

The `scripts/generate_sbom.sh` script will automatically install Syft if not found.

### Manual Installation

**macOS:**
```bash
brew install syft
```

**Linux:**
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

**Windows (WSL):**
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

**Verify Installation:**
```bash
syft version
```

## Scripts

### 1. `generate_sbom.sh` - Full SBOM Generation

Complete SBOM generation with multiple formats and comprehensive analysis.

```bash
./scripts/generate_sbom.sh
```

**Generates:**
- API and frontend container SBOMs (SPDX, CycloneDX, Table) from the legacy `localhost/msn-weather-wrapper_api:latest` and `localhost/msn-weather-wrapper_frontend:latest` images
- Source code SBOMs (SPDX, CycloneDX, Table)
- Python packages SBOMs (SPDX, Table)
- Summary report in Markdown

**Output Directory:** `sbom_output/`

### 2. `generate_sbom_ci.sh` - CI/CD Optimized

Lightweight script for CI/CD pipelines.

```bash
./scripts/generate_sbom_ci.sh
```

The script scans the legacy `msn-weather-wrapper_api`/`_frontend` images if they exist and always generates a source SBOM (`source_sbom_*.json`). The GitHub Actions workflows do not call it; see [CI/CD Integration](#cicd-integration).

**Environment Variables:**
```bash
# Customize output directory
SBOM_DIR=artifacts/sboms ./scripts/generate_sbom_ci.sh

# Change output format
FORMAT=cyclonedx-json ./scripts/generate_sbom_ci.sh
```

## Output Formats

### SPDX JSON (`*_spdx_*.json`)
Industry-standard SBOM format, widely supported for compliance and security scanning.

```bash
# Parse with jq
jq '.packages[] | {name: .name, version: .versionInfo}' sbom_output/api_sbom_spdx_*.json
```

### CycloneDX JSON (`*_cyclonedx_*.json`)
Modern SBOM standard optimized for security use cases.

```bash
# View components
jq '.components[] | {name: .name, version: .version}' sbom_output/api_sbom_cyclonedx_*.json
```

### Table Format (`*_table_*.txt`)
Human-readable format for quick review.

```bash
# View directly
cat sbom_output/api_sbom_table_*.txt
```

## Use Cases

### 1. Vulnerability Scanning

Feed SBOMs into vulnerability scanners like Grype:

```bash
# Generate SBOM
./scripts/generate_sbom.sh

# Scan for vulnerabilities
grype sbom:sbom_output/api_sbom_spdx_*.json
```

### 2. License Compliance

Analyze software licenses:

```bash
# Extract license information
jq '.packages[] | {name: .name, license: .licenseDeclared}' sbom_output/api_sbom_spdx_*.json
```

### 3. Dependency Tracking

Monitor dependencies across releases:

```bash
# Compare SBOMs
diff <(jq -S '.packages[].name' sbom_v1.json) \
     <(jq -S '.packages[].name' sbom_v2.json)
```

### 4. Supply Chain Security

Track and verify all software components:

```bash
# List all Python packages
jq '.packages[] | select(.name | startswith("python")) | .name' sbom_output/api_sbom_spdx_*.json
```

## Manual SBOM Generation

### Scan Container Images

Scan the published unified image (or `msn-weather-app:test` for an image built locally the way CI builds it):

```bash
# SPDX format
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest -o spdx-json > container_sbom.json

# CycloneDX format
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest -o cyclonedx-json > container_sbom.json

# Table format (human-readable)
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest -o table

# Syft JSON (most detailed)
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest -o syft-json > container_sbom.json
```

### Scan Directories

```bash
# Scan entire project
syft dir:. -o spdx-json > project_sbom.json

# Scan specific directory
syft dir:./backend -o table

# Scan Python virtual environment
syft dir:./.venv -o spdx-json > venv_sbom.json
```

### Scan Archives

```bash
# Scan tar archive
syft file:archive.tar.gz -o spdx-json

# Scan zip file
syft file:package.zip -o table
```

## CI/CD Integration

### GitHub Actions (this repository)

SBOM generation is already wired into the reusable workflows called by `ci.yml`; neither `generate_sbom.sh` nor `generate_sbom_ci.sh` is used in CI.

- **`build.yml`, `sbom` job** — installs Syft and runs `syft dir:.` to produce `sbom_output/source_sbom.json` (SPDX) and `sbom_output/source_cyclonedx.json` (CycloneDX). On pushes to `main` the directory is uploaded as the `sbom-reports` artifact (7-day retention).
- **`security.yml`, `container-scan` job** — builds the unified image as `msn-weather-app:security-scan`, runs Syft on it to produce `container-sbom.json`, and feeds that SBOM to Grype (`grype sbom:security-reports/container-sbom.json`). On `main` and tag runs the SBOM and scan results are uploaded inside the `container-security-reports` artifact (30-day retention). Trivy and Grype also fail the job on fixable CRITICAL (and, for Trivy, HIGH) findings.
- **`build.yml`, image push** — the image pushed to `ghcr.io/jim-wyatt/msn-weather-wrapper` on `main` and `v*` tags is built with `sbom: true` and `provenance: true`, so an SBOM and provenance attestation are attached to the image in the registry, and `actions/attest` records a signed build-provenance attestation verifiable with `gh attestation verify oci://ghcr.io/jim-wyatt/msn-weather-wrapper:<tag> --repo jim-wyatt/msn-weather-wrapper`.

Download the artifacts from a workflow run with `gh run download <run-id> -n sbom-reports` or `-n container-security-reports`.

### Other CI systems (generic examples)

The snippets below are generic examples for teams reusing these scripts elsewhere; they are not used by this project.

**GitLab CI:**

```yaml
generate-sbom:
  stage: build
  image: ubuntu:latest
  script:
    - apt-get update && apt-get install -y curl
    - curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
    - ./scripts/generate_sbom_ci.sh
  artifacts:
    paths:
      - sbom_output/
    expire_in: 30 days
```

**Jenkins:**

```groovy
pipeline {
    agent any
    stages {
        stage('Generate SBOM') {
            steps {
                sh '''
                    curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
                    ./scripts/generate_sbom_ci.sh
                '''
                archiveArtifacts artifacts: 'sbom_output/**', fingerprint: true
            }
        }
    }
}
```

## Advanced Usage

### Custom Catalogers

```bash
# Only catalog Python packages
syft dir:. --catalogers python -o table

# Only catalog OS packages
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest --catalogers dpkg,apk -o table
```

### Filtering Output

```bash
# Exclude specific paths
syft dir:. --exclude './node_modules/**' --exclude './.git/**' -o spdx-json

# Include only specific file types
syft dir:. --select-catalogers python,javascript -o table
```

### Output to Multiple Formats

```bash
# Generate multiple formats at once
syft ghcr.io/jim-wyatt/msn-weather-wrapper:latest \
  -o spdx-json=container_spdx.json \
  -o cyclonedx-json=container_cyclonedx.json \
  -o table=container_table.txt
```

## Best Practices

### 1. Generate SBOMs on Every Build

Automate SBOM generation in your CI/CD pipeline to maintain up-to-date inventories.

### 2. Store SBOMs with Releases

Archive SBOMs alongside release artifacts for compliance and auditing.

### 3. Version Control SBOMs

Track changes to dependencies by committing representative SBOMs.

### 4. Regular Vulnerability Scanning

Combine Syft with Grype for continuous vulnerability monitoring:

```bash
# Generate and scan
./scripts/generate_sbom.sh
grype sbom:sbom_output/api_sbom_spdx_*.json --fail-on high
```

### 5. License Auditing

Review licenses regularly:

```bash
jq '.packages[] | select(.licenseDeclared != null) | {name: .name, license: .licenseDeclared}' \
  sbom_output/api_sbom_spdx_*.json | sort -u
```

## Troubleshooting

### Syft Not Found

```bash
# Install manually
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# Add to PATH
export PATH=$PATH:/usr/local/bin
```

### Container Not Found

```bash
# Build the unified image
podman-compose -f infra/compose/podman-compose.yml build

# Verify images exist
podman images | grep -E 'msn-weather|app'
```

`generate_sbom.sh` looks for the legacy `localhost/msn-weather-wrapper_api:latest` and `_frontend` images and runs a bare `podman-compose build` when they are missing; with the unified compose file that produces a single `app` image, so scan it directly with `syft <image built by compose>` instead.

### Permission Denied

```bash
# Make scripts executable
chmod +x scripts/generate_sbom.sh scripts/generate_sbom_ci.sh
```

### Large SBOM Files

```bash
# Compress SBOMs
gzip sbom_output/*.json

# View compressed SBOM
zcat sbom_output/api_sbom_spdx_*.json.gz | jq '.packages[].name'
```

## Output Structure

```
sbom_output/
├── api_sbom_spdx_YYYYMMDD_HHMMSS.json             # API container SPDX SBOM
├── api_sbom_cyclonedx_YYYYMMDD_HHMMSS.json        # API container CycloneDX SBOM
├── api_sbom_table_YYYYMMDD_HHMMSS.txt             # API container Table SBOM
├── frontend_sbom_spdx_YYYYMMDD_HHMMSS.json        # Frontend container SPDX SBOM
├── frontend_sbom_cyclonedx_YYYYMMDD_HHMMSS.json   # Frontend container CycloneDX SBOM
├── frontend_sbom_table_YYYYMMDD_HHMMSS.txt        # Frontend container Table SBOM
├── source_sbom_spdx_YYYYMMDD_HHMMSS.json          # Source SPDX SBOM
├── source_sbom_cyclonedx_YYYYMMDD_HHMMSS.json     # Source CycloneDX SBOM
├── source_sbom_table_YYYYMMDD_HHMMSS.txt          # Source Table SBOM
├── python_packages_sbom_spdx_YYYYMMDD_HHMMSS.json # Python SPDX SBOM
├── python_packages_sbom_table_YYYYMMDD_HHMMSS.txt # Python Table SBOM
└── SBOM_SUMMARY_YYYYMMDD_HHMMSS.md                # Summary Report
```

`generate_sbom_ci.sh` writes `api_sbom_*.json`, `frontend_sbom_*.json` (when the legacy images exist) and `source_sbom_*.json` in the format given by `FORMAT`.

## Resources

- [Syft GitHub Repository](https://github.com/anchore/syft)
- [Syft Documentation](https://github.com/anchore/syft#syft)
- [SPDX Specification](https://spdx.dev/)
- [CycloneDX Standard](https://cyclonedx.org/)
- [NTIA SBOM Minimum Elements](https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom)
- [Grype Vulnerability Scanner](https://github.com/anchore/grype)

## Support

For issues or questions:
- Syft Issues: https://github.com/anchore/syft/issues
- Project Issues: https://github.com/jim-wyatt/msn-weather-wrapper/issues
