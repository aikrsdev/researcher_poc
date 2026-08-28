import os
from dataclasses import dataclass


@dataclass
class Settings:
    ollama_model: str
    ollama_base_url: str
    tavily_api_key: str | None


def load_settings() -> Settings:
    return Settings(
        ollama_model=os.environ.get("OLLAMA_MODEL", "llama3.2"),
        ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
        tavily_api_key=os.environ.get("TAVILY_API_KEY"),
    )


def validate(settings: Settings) -> None:
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY environment variable is required")
