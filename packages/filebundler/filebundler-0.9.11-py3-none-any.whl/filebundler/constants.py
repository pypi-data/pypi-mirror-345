# filebundler/constants.py
import os

from typing import Literal, Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class EnvironmentSettings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=False)

    env: Literal["dev", "prod"] = "prod"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "WARNING"
    anthropic_api_key: Optional[str] = None

    @field_validator("log_level", mode="before")
    def validate_log_level(cls, value: str) -> str:
        return value.upper()

    @property
    def is_dev(self) -> bool:
        return self.env == "dev"


def get_env_settings():
    env_settings = EnvironmentSettings()
    if env_settings.is_dev and env_settings.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = env_settings.anthropic_api_key

    return env_settings


DEFAULT_MAX_RENDER_FILES = 500

DEFAULT_IGNORE_PATTERNS = [
    # root dir folders
    "venv/**",
    "venv",
    ".venv/**",
    ".venv",
    "node_modules/**",
    "node_modules",
    ".mypy_cache/**",
    ".mypy_cache",
    ".pytest_cache/**",
    ".pytest_cache",
    ".git/**",
    ".git",
    ".ruff_cache/**",
    ".ruff_cache",
    ".vscode/**",
    ".vscode",
    # recursive folders
    "*/__pycache__",
    "*/.ipynb_checkpoints",
    # files
    ".env",
    ".DS_Store",
    "*credentials.json",
    "package-lock.json",
    ".prettierrc*",
    ".eslint.config.js",
    # extensions
    "*.lock",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.gif",
    "*.pdf",
    "*.zip",
    "*.exe",
    "*.dll",
    "*.pyc",
    "*.so",
    "*.bin",
    "*.dat",
]


DISPLAY_NR_OF_RECENT_PROJECTS = 5
SELECTIONS_BUNDLE_NAME = "default-bundle"
