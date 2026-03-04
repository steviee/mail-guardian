---
id: 7
title: Google Calendar Setup-Guide & Onboarding
status: open
priority: high
labels: []
created: "2026-03-04"
updated: "2026-03-04"
---

## Problem

Der Google Calendar ist implementiert (Issue #4), aber es gibt **keine Anleitung**, wie man ihn
tatsächlich einrichtet. Der einzige Hinweis ist eine Error-Message im Code:

```
Download from Google Cloud Console → APIs & Services → Credentials
and save as 'gcal_credentials.json' in ~/.config/mailguardian/
```

Das reicht nicht. Ein Benutzer, der noch nie mit der Google Cloud Console gearbeitet hat,
steht vor einer Wand: Projekt erstellen, API aktivieren, OAuth Consent Screen einrichten,
Credentials anlegen, JSON herunterladen, richtig ablegen, dann erst `mg calendar auth`.

## Kontext

Google Calendar API erfordert OAuth2-Credentials vom Typ "Desktop Application".
Der Flow ist:

1. Google Cloud Projekt erstellen/auswählen
2. Google Calendar API aktivieren
3. OAuth Consent Screen konfigurieren (External oder Internal)
4. OAuth 2.0 Client ID erstellen (Typ: Desktop)
5. JSON herunterladen
6. Ablegen als `~/.config/mailguardian/gcal_credentials.json`
7. `mg calendar auth` → Browser öffnet sich → Login → Token wird gespeichert
8. Ab jetzt funktioniert `mg calendar view` / `mg calendar add`

## Erfolgskriterien

- [ ] `mg calendar auth` gibt bei fehlender `gcal_credentials.json` eine **vollständige
      Schritt-für-Schritt-Anleitung** aus (nicht nur "download from Google Cloud Console")
- [ ] Eigener CLI-Command `mg calendar setup` der interaktiv durch den Prozess führt:
      1. Erklärt was nötig ist
      2. Öffnet den Browser zur Google Cloud Console (richtiger Deep-Link)
      3. Wartet auf den User: "Hast du die JSON-Datei heruntergeladen? (Pfad eingeben)"
      4. Kopiert/verschiebt die Datei nach `~/.config/mailguardian/gcal_credentials.json`
      5. Startet automatisch `mg calendar auth`
- [ ] Verifizierung: `mg calendar view` funktioniert nach Durchlaufen des Setup-Wizards
- [ ] Die Error-Messages in `gcal.py` und `calendar_.py` werden verbessert

## Betroffene Dateien

- `mailguardian/calendar_.py` — neuer `setup` Command, verbesserte Error-Messages
- `mailguardian/gcal.py` — verbesserte `FileNotFoundError` Message mit vollständiger Anleitung

## Hinweise zur Umsetzung

### Deep-Links für Google Cloud Console
- Neues Projekt: `https://console.cloud.google.com/projectcreate`
- API Library (Calendar API): `https://console.cloud.google.com/apis/library/calendar-json.googleapis.com`
- Credentials: `https://console.cloud.google.com/apis/credentials`
- OAuth Consent Screen: `https://console.cloud.google.com/apis/credentials/consent`

### OAuth Consent Screen Fallstricke
- Bei "External" muss man Test-User hinzufügen (sich selbst)
- Scopes: `https://www.googleapis.com/auth/calendar` muss aktiviert sein
- App muss nicht verifiziert werden für persönliche Nutzung (Test-Modus reicht)

### Mögliches Format für die CLI-Anleitung
```
╭─ Google Calendar Setup ──────────────────────────────╮
│                                                       │
│  Schritt 1: Google Cloud Projekt                      │
│  → https://console.cloud.google.com/projectcreate     │
│                                                       │
│  Schritt 2: Calendar API aktivieren                   │
│  → https://console.cloud.google.com/apis/library/...  │
│                                                       │
│  Schritt 3: OAuth Consent Screen einrichten           │
│  → App-Typ: External, Test-User: deine E-Mail        │
│                                                       │
│  Schritt 4: OAuth 2.0 Client ID erstellen             │
│  → Typ: Desktop-Anwendung                            │
│  → JSON herunterladen                                 │
│                                                       │
╰───────────────────────────────────────────────────────╯
```
