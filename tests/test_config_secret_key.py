"""Secret key resolution: file-based secrets and production strength checks."""

import pytest

from backend.api import config


def _production(monkeypatch):
    monkeypatch.setattr(config, "ENVIRONMENT", "production")
    monkeypatch.setattr(config, "DEBUG", False)
    monkeypatch.setattr(config, "TESTING", False)
    monkeypatch.delenv("APP_SECRET_KEY", raising=False)
    monkeypatch.delenv("APP_SECRET_KEY_FILE", raising=False)


def test_file_takes_precedence_over_environment(tmp_path, monkeypatch):
    _production(monkeypatch)
    secret_file = tmp_path / "app_secret_key"
    secret_file.write_text("f" * 64 + "\n")
    monkeypatch.setenv("APP_SECRET_KEY_FILE", str(secret_file))
    monkeypatch.setenv("APP_SECRET_KEY", "e" * 64)
    assert config.get_secret_key() == "f" * 64


def test_environment_value_is_used_when_no_file(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setenv("APP_SECRET_KEY", "e" * 64)
    assert config.get_secret_key() == "e" * 64


def test_short_key_is_rejected_in_production(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setenv("APP_SECRET_KEY", "too-short")
    with pytest.raises(ValueError, match="at least 32 characters"):
        config.get_secret_key()


def test_placeholder_is_rejected_in_production(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setenv("APP_SECRET_KEY", config.DEFAULT_SECRET_KEY_PLACEHOLDER)
    with pytest.raises(ValueError, match="must be set"):
        config.get_secret_key()


def test_unreadable_file_is_an_error(tmp_path, monkeypatch):
    _production(monkeypatch)
    monkeypatch.setenv("APP_SECRET_KEY_FILE", str(tmp_path / "missing"))
    with pytest.raises(ValueError, match="could not be read"):
        config.get_secret_key()


def test_development_generates_a_key_when_unset(monkeypatch):
    _production(monkeypatch)
    monkeypatch.setattr(config, "ENVIRONMENT", "development")
    key = config.get_secret_key()
    assert len(key) >= 32
