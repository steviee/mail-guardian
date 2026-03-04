---
id: 2
title: IMAP Core Module
status: closed
priority: medium
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

Kernfunktionalität von MailGuardian: Mails aus IMAP-Postfächern lesen und anzeigen.
Muss mehrere Accounts gleichzeitig unterstützen (Gmail, Outlook, beliebige IMAP-Server).
Passwörter dürfen nicht im Klartext in Config-Dateien stehen.

## Erfolgskriterien

- `mg auth add` fügt interaktiv einen neuen Account hinzu (Name, Provider, Username, Passwort)
- `mg auth list` zeigt alle konfigurierten Accounts als Rich-Tabelle
- `mg auth test` prüft IMAP-Verbindung und meldet Erfolg/Fehler
- `mg auth remove` entfernt einen Account
- `mg inbox list` zeigt die neuesten Mails (UID, Datum, Absender, Betreff, Unread-Marker)
- `mg inbox show <UID>` zeigt den vollständigen Mail-Body im Terminal
- `mg inbox scan` zeigt Read/Unread-Status aller Mails
- `--account` Flag funktioniert bei allen inbox/auth-Commands

## Umsetzung

### imap_client.py — IMAP-Abstraktionsschicht
- `connect(host, port, username, password)` → IMAPClient-Verbindung mit SSL
- `fetch_mail_list(client, folder, limit)` → Liste von `MailSummary`-Objekten (UID, Subject, Sender, Date, Flags)
- `fetch_mail_detail(client, uid, folder)` → `MailDetail` mit vollem Body (Plain-Text + optional HTML)
- `_decode_header()` → RFC2047-Dekodierung für internationale Betreffzeilen
- `_extract_body()` → Multipart-Parsing, bevorzugt text/plain, Fallback auf text/html

### accounts.py — Multi-Account-Verwaltung
- `add_account()` → Speichert Account in `~/.config/mailguardian/accounts.yaml`, Passwort in System-Keyring
- `remove_account()` → Entfernt Account + Keyring-Eintrag
- `get_account(name=None)` → Gibt Account by Name zurück, oder Default-Account
- `get_password(account_name)` → Holt Passwort aus Keyring
- Provider-Defaults: `PROVIDER_DEFAULTS` dict für Gmail, Outlook, Yahoo (Host + Port)

### auth.py — CLI-Commands
- `add` → Interaktiver Wizard mit typer.prompt(), unterstützt auch non-interaktiv via Flags
- `list` → Rich-Tabelle mit Name, Provider, Username, Host, Default-Marker
- `remove` → Löscht Account
- `test` → Verbindet sich, listet Folder-Anzahl

### inbox.py — CLI-Commands
- `list` → Rich-Tabelle mit UID, Datum, Absender, Betreff, Unread-Marker (*)
- `show` → Rich-Panel mit Header + Plain-Text Body
- `scan` → Read/Unread-Status-Übersicht

### Design-Entscheidungen
- **keyring statt Klartext**: Passwörter werden im System-Keyring gespeichert (macOS Keychain, etc.)
- **IMAPClient statt imaplib**: Höhere Abstraktion, saubere API für ENVELOPE/FLAGS-Fetch
- **Dataclasses `MailSummary` / `MailDetail`**: Klare Trennung zwischen Listing (leichtgewichtig) und Detail (voller Body)
- **Readonly-Modus**: `select_folder(readonly=True)` — kein versehentliches Ändern von Flags
- **Sortierung**: Mails nach Datum absteigend (neueste zuerst)

### Betroffene Dateien
- `mailguardian/imap_client.py` (neu)
- `mailguardian/accounts.py` (erweitert: add_account, remove_account, get_password, PROVIDER_DEFAULTS)
- `mailguardian/auth.py` (komplett neu: add, list, remove, test)
- `mailguardian/inbox.py` (komplett neu: list, show, scan mit IMAP-Anbindung)
- `pyproject.toml` (keyring Dependency hinzugefügt)

### Verifikation
```bash
mg auth add                    # Interaktiver Account-Wizard
mg auth list                   # Zeigt Accounts-Tabelle
mg auth test                   # Testet IMAP-Verbindung
mg inbox list --limit 5        # Zeigt 5 neueste Mails
mg inbox show <UID>            # Zeigt Mail-Detail
mg inbox list --account <name> # Spezifischer Account
```

### Commit
`1532d9f` — `feat: IMAP core module with multi-account support (ref #2)`
