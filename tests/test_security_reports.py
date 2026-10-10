"""Tests for evaluating CI security scan reports."""

import json

import pytest

from scripts.evaluate_security_reports import evaluate_reports


def write_reports(tmp_path, reports, exit_codes=(0, 0, 0)):
    for name, report in reports.items():
        (tmp_path / name).write_text(json.dumps(report))
    for scan, exit_code in zip(("bandit", "semgrep", "pip-audit"), exit_codes, strict=True):
        (tmp_path / f"{scan}-exit-code").write_text(str(exit_code))


def clean_reports():
    return {
        "bandit-report.json": {"results": [], "errors": []},
        "semgrep-report.json": {"results": [], "errors": []},
        "pip-audit-report.json": {"dependencies": [], "errors": []},
    }


def test_clean_reports_pass(tmp_path):
    write_reports(tmp_path, clean_reports())

    assert evaluate_reports(tmp_path) == []


def test_high_bandit_finding_fails(tmp_path):
    reports = clean_reports()
    reports["bandit-report.json"]["results"] = [{"issue_severity": "HIGH"}]
    write_reports(tmp_path, reports, exit_codes=(1, 0, 0))

    assert "Bandit reported HIGH findings or scan errors" in evaluate_reports(tmp_path)


def test_lower_bandit_severity_does_not_fail(tmp_path):
    reports = clean_reports()
    reports["bandit-report.json"]["results"] = [{"issue_severity": "MEDIUM"}]
    write_reports(tmp_path, reports)

    assert evaluate_reports(tmp_path) == []


def test_scanner_error_and_missing_report_fail(tmp_path):
    reports = clean_reports()
    reports["semgrep-report.json"]["errors"] = [{"message": "registry unavailable"}]
    del reports["pip-audit-report.json"]
    write_reports(tmp_path, reports)

    failures = evaluate_reports(tmp_path)
    assert "Semgrep reported findings or scan errors" in failures
    assert any(
        "pip-audit-report.json: could not read scan report" in failure for failure in failures
    )


@pytest.mark.parametrize(
    ("report_name", "required_field"),
    [
        ("bandit-report.json", "results"),
        ("semgrep-report.json", "results"),
        ("pip-audit-report.json", "dependencies"),
    ],
)
def test_missing_required_report_fields_fail(tmp_path, report_name, required_field):
    reports = clean_reports()
    del reports[report_name][required_field]
    write_reports(tmp_path, reports)

    assert any(
        f"{report_name}: required '{required_field}' field must be a JSON array" in failure
        for failure in evaluate_reports(tmp_path)
    )


@pytest.mark.parametrize(
    ("report_name", "required_field"),
    [
        ("bandit-report.json", "results"),
        ("semgrep-report.json", "results"),
        ("pip-audit-report.json", "dependencies"),
    ],
)
@pytest.mark.parametrize("invalid_value", [None, {}])
def test_required_report_fields_must_be_lists(tmp_path, report_name, required_field, invalid_value):
    reports = clean_reports()
    reports[report_name][required_field] = invalid_value
    write_reports(tmp_path, reports)

    assert any(
        f"{report_name}: required '{required_field}' field must be a JSON array" in failure
        for failure in evaluate_reports(tmp_path)
    )
