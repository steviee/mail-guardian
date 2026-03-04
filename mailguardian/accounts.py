"""Multi-account management for IMAP providers."""

from __future__ import annotations

from typing import Optional

import keyring
import yaml

from mailguardian.config import ACCOUNTS_FILE, ensure_config_dir

SERVICE_NAME = "mailguardian"

# Well-known provider defaults
PROVIDER_DEFAULTS: dict[str, dict] = {
    "gmail": {"imap_host": "imap.gmail.com", "imap_port": 993},
    "outlook": {"imap_host": "outlook.office365.com", "imap_port": 993},
    "yahoo": {"imap_host": "imap.mail.yahoo.com", "imap_port": 993},
}


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


def add_account(
    name: str,
    provider: str,
    username: str,
    password: str,
    imap_host: str | None = None,
    imap_port: int | None = None,
    default: bool = False,
) -> dict:
    """Add a new account and store password in system keyring."""
    accounts = _load_accounts()

    # Check for duplicate name
    if any(a["name"] == name for a in accounts):
        raise ValueError(f"Account '{name}' already exists")

    # Apply provider defaults if not specified
    defaults = PROVIDER_DEFAULTS.get(provider, {})
    host = imap_host or defaults.get("imap_host", "")
    port = imap_port or defaults.get("imap_port", 993)

    if not host:
        raise ValueError("imap_host is required for generic providers")

    # If this is the first account or explicitly default, set it
    if default or not accounts:
        for a in accounts:
            a.pop("default", None)

    account = {
        "name": name,
        "provider": provider,
        "imap_host": host,
        "imap_port": port,
        "username": username,
    }
    if default or not accounts:
        account["default"] = True

    accounts.append(account)
    _save_accounts(accounts)

    # Store password securely in system keyring
    keyring.set_password(SERVICE_NAME, name, password)

    return account


def remove_account(name: str) -> bool:
    """Remove an account by name."""
    accounts = _load_accounts()
    filtered = [a for a in accounts if a["name"] != name]
    if len(filtered) == len(accounts):
        return False
    _save_accounts(filtered)
    try:
        keyring.delete_password(SERVICE_NAME, name)
    except keyring.errors.PasswordDeleteError:
        pass
    return True


def get_account(name: Optional[str] = None) -> dict | None:
    """Get an account by name, or the default account if name is None."""
    accounts = _load_accounts()
    if not accounts:
        return None
    if name:
        return next((a for a in accounts if a["name"] == name), None)
    return next((a for a in accounts if a.get("default")), accounts[0])


def get_password(account_name: str) -> str | None:
    """Retrieve password for an account from system keyring."""
    return keyring.get_password(SERVICE_NAME, account_name)


def list_accounts() -> list[dict]:
    """Return all configured accounts."""
    return _load_accounts()
