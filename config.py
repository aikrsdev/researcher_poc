import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    claude_model: str
    api_key: str
    rate_limit_per_minute: int


def load_settings() -> Settings:
    api_key = os.environ.get("API_KEY")
    if not api_key:
        raise RuntimeError(
            "API_KEY environment variable must be set to a secret value used to "
            "authenticate requests to this service (see .env.example)."
        )

    return Settings(
        claude_model=os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5"),
        api_key=api_key,
        rate_limit_per_minute=int(os.environ.get("RATE_LIMIT_PER_MINUTE", "20")),
    )
