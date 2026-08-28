from config import load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)

    settings = load_settings()

    assert settings.claude_model == "claude-haiku-4-5"


def test_load_settings_reads_overrides(monkeypatch):
    monkeypatch.setenv("CLAUDE_MODEL", "claude-opus-5")

    settings = load_settings()

    assert settings.claude_model == "claude-opus-5"
