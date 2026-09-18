import pytest

from config import load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("RATE_LIMIT_PER_MINUTE", raising=False)
    monkeypatch.setenv("API_KEY", "test-key")

    settings = load_settings()

    assert settings.claude_model == "claude-haiku-4-5"
    assert settings.api_key == "test-key"
    assert settings.rate_limit_per_minute == 20


def test_load_settings_reads_overrides(monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "claude-opus-5")
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "5")

    settings = load_settings()

    assert settings.claude_model == "claude-opus-5"
    assert settings.rate_limit_per_minute == 5


def test_load_settings_requires_api_key(monkeypatch):
    monkeypatch.delenv("API_KEY", raising=False)

    with pytest.raises(RuntimeError):
        load_settings()
