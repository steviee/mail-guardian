"""Multi-account management for IMAP providers."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

from mailguardian.config import ACCOUNTS_FILE, ensure_config_dir


def _load_accounts() -> list[dict]:
    """Load accounts from accounts.yaml."""
    if not ACCOUNTS_FILE.exists():
        return []
    data = yaml.safe_load(ACCOUNTS_FILE.read_text()) or {}
    return data.get("accounts", [])


def _save_accounts(accounts: list[dict]) -> None:
    """Save accounts to accounts.yaml."""
    ensure_config_dir()
    ACCOUNTS_FILE.write_text(yaml.dump({"accounts": accounts}, default_flow_style=False))


def get_account(name: Optional[str] = None) -> dict | None:
    """Get an account by name, or the default account if name is None."""
    accounts = _load_accounts()
    if not accounts:
        return None
    if name:
        return next((a for a in accounts if a["name"] == name), None)
    return next((a for a in accounts if a.get("default")), accounts[0])


def list_accounts() -> list[dict]:
    """Return all configured accounts."""
    return _load_accounts()
