"""Configuration paths and defaults for MailGuardian."""

from pathlib import Path

import yaml

CONFIG_DIR = Path.home() / ".config" / "mailguardian"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.yaml"
SETTINGS_FILE = CONFIG_DIR / "settings.yaml"

DEFAULT_LLM_MODEL = "ollama_chat/llama3.2"

DEFAULT_SETTINGS = {
    "llm_model": DEFAULT_LLM_MODEL,
    "check_interval": 300,
}


def ensure_config_dir() -> Path:
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_settings() -> dict:
    """Load user settings, merged with defaults."""
    settings = dict(DEFAULT_SETTINGS)
    if SETTINGS_FILE.exists():
        user = yaml.safe_load(SETTINGS_FILE.read_text()) or {}
        settings.update(user)
    return settings


def save_settings(settings: dict) -> None:
    """Save settings to disk."""
    ensure_config_dir()
    SETTINGS_FILE.write_text(yaml.dump(settings, default_flow_style=False))
