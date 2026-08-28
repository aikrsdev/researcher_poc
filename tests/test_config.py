import pytest
from config import Settings, load_settings, validate


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("OLLAMA_MODEL", raising=False)
    monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
    monkeypatch.setenv("TAVILY_API_KEY", "test-key")

    settings = load_settings()

    assert settings.ollama_model == "llama3.2"
    assert settings.ollama_base_url == "http://localhost:11434"
    assert settings.tavily_api_key == "test-key"


def test_load_settings_reads_overrides(monkeypatch):
    monkeypatch.setenv("OLLAMA_MODEL", "custom-model")
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://example:1234")
    monkeypatch.setenv("TAVILY_API_KEY", "key")

    settings = load_settings()

    assert settings.ollama_model == "custom-model"
    assert settings.ollama_base_url == "http://example:1234"


def test_validate_raises_without_tavily_key():
    settings = Settings(ollama_model="m", ollama_base_url="url", tavily_api_key=None)

    with pytest.raises(RuntimeError):
        validate(settings)


def test_validate_passes_with_tavily_key():
    settings = Settings(ollama_model="m", ollama_base_url="url", tavily_api_key="key")

    validate(settings)
