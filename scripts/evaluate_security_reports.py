"""Fail CI when security reports contain findings or scanner errors."""

import json
import os
import sys
from pathlib import Path
from typing import Any


def evaluate_reports(reports: Path) -> list[str]:
    """Return failures found in generated security reports and scanner statuses."""
    failures: list[str] = []
    findings: dict[str, bool] = {}
    scan_errors: dict[str, bool] = {}

    def load_report(name: str, required_list_field: str) -> dict[str, Any]:
        try:
            report = json.loads((reports / name).read_text())
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"{name}: could not read scan report ({error})")
            return {}
        if not isinstance(report, dict):
            failures.append(f"{name}: scan report must contain a JSON object")
            return {}
        if not isinstance(report.get(required_list_field), list):
            failures.append(f"{name}: required '{required_list_field}' field must be a JSON array")
            return {}
        return report

    bandit = load_report("bandit-report.json", "results")
    bandit_findings = [
        item
        for item in bandit.get("results", [])
        if isinstance(item, dict) and item.get("issue_severity") == "HIGH"
    ]
    findings["bandit"] = bool(bandit_findings)
    scan_errors["bandit"] = bool(bandit.get("errors"))
    if findings["bandit"] or scan_errors["bandit"]:
        failures.append("Bandit reported HIGH findings or scan errors")

    semgrep = load_report("semgrep-report.json", "results")
    findings["semgrep"] = bool(semgrep.get("results"))
    scan_errors["semgrep"] = bool(semgrep.get("errors"))
    if findings["semgrep"] or scan_errors["semgrep"]:
        failures.append("Semgrep reported findings or scan errors")

    pip_audit = load_report("pip-audit-report.json", "dependencies")
    dependencies = pip_audit.get("dependencies", [])
    vulnerabilities = (
        [
            vulnerability
            for dependency in dependencies
            if isinstance(dependency, dict)
            for vulnerability in dependency.get("vulns", [])
        ]
        if isinstance(dependencies, list)
        else []
    )
    findings["pip-audit"] = bool(vulnerabilities)
    scan_errors["pip-audit"] = bool(pip_audit.get("errors"))
    if findings["pip-audit"] or scan_errors["pip-audit"]:
        failures.append("pip-audit reported vulnerabilities or scan errors")

    for scan in ("bandit", "semgrep", "pip-audit"):
        try:
            exit_code = int((reports / f"{scan}-exit-code").read_text())
        except (OSError, ValueError) as error:
            failures.append(f"{scan}: missing or invalid exit code ({error})")
            continue
        if exit_code and not findings.get(scan) and not scan_errors.get(scan):
            failures.append(f"{scan} exited with status {exit_code}")

    return failures


def main() -> int:
    """Evaluate reports and communicate failures to the GitHub Actions summary."""
    failures = evaluate_reports(Path(sys.argv[1] if len(sys.argv) > 1 else "security-reports"))
    if not failures:
        print("Security scans completed without findings or scan errors.")
        return 0

    for failure in failures:
        print(f"::error::{failure}")
    github_env = os.environ.get("GITHUB_ENV")
    if github_env:
        with open(github_env, "a") as environment:
            environment.write("SECURITY_SCAN_FAILED=true\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
