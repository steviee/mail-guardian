"""Configuration paths and defaults for MailGuardian."""

from pathlib import Path

CONFIG_DIR = Path.home() / ".config" / "mailguardian"
ACCOUNTS_FILE = CONFIG_DIR / "accounts.yaml"


def ensure_config_dir() -> Path:
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR
