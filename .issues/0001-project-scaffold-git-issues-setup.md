---
id: 1
title: Project Scaffold & Git-Issues Setup
status: closed
priority: medium
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

Erstes Issue des Greenfield-Projekts MailGuardian. Ziel: lauffähiges Projekt-Grundgerüst,
damit alle folgenden Issues auf einer funktionierenden Struktur aufbauen können.

## Erfolgskriterien

- `pyproject.toml` existiert mit allen Basis-Dependencies
- `git-issues init` wurde ausgeführt, `.issues/` Verzeichnis vorhanden
- `uv run mg --help` zeigt alle Subcommand-Gruppen (auth, inbox, calendar, agent)
- `.gitignore` schützt vor versehentlichem Commit von Secrets
- `CLAUDE.md` dokumentiert Projektkonventionen für KI-Agenten
- venv via `uv` eingerichtet, alle Dependencies installierbar

## Umsetzung

### pyproject.toml
- Build-System: hatchling
- Entry-Point: `mg = "mailguardian.cli:app"`
- Dependencies: typer, imapclient, google-api-python-client, google-auth-oauthlib, litellm, rich, pyyaml, keyring
- Python >= 3.10

### Projektstruktur
```
mailguardian/
├── __init__.py      # Package mit __version__
├── cli.py           # Typer-App mit Subcommand-Gruppen
├── auth.py          # Auth-Commands (Platzhalter)
├── inbox.py         # Inbox-Commands (Platzhalter)
├── calendar_.py     # Calendar-Commands (Unterstrich wegen stdlib-Kollision)
├── agent.py         # Agent-Commands (Platzhalter)
├── config.py        # Config-Pfade (~/.config/mailguardian/)
└── accounts.py      # Multi-Account Management
```

### Design-Entscheidungen
- **Config-Pfad**: `~/.config/mailguardian/` (XDG-konform)
- **Multi-Account von Anfang an**: `accounts.yaml` mit Provider-Defaults (Gmail, Outlook, Yahoo)
- **Typer statt Click direkt**: Intuitivere API, automatische --help Generierung
- **`calendar_.py`**: Trailing Underscore nötig, da `calendar` ein Python-Stdlib-Modul ist

### Betroffene Dateien
- `pyproject.toml` (neu)
- `mailguardian/__init__.py` (neu)
- `mailguardian/cli.py` (neu)
- `mailguardian/auth.py` (neu)
- `mailguardian/inbox.py` (neu)
- `mailguardian/calendar_.py` (neu)
- `mailguardian/agent.py` (neu)
- `mailguardian/config.py` (neu)
- `mailguardian/accounts.py` (neu)
- `.gitignore` (neu)
- `CLAUDE.md` (neu)

### Verifikation
```bash
uv run mg --help        # Zeigt alle Subcommands
git-issues list         # Zeigt Issues #2-#5 als offen
```

### Commit
`60c2164` — `feat: project scaffold with pyproject.toml and CLI skeleton (ref #1)`
