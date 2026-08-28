import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    claude_model: str


def load_settings() -> Settings:
    return Settings(
        claude_model=os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5"),
    )
