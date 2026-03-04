---
id: 4
title: Google Calendar Integration
status: closed
priority: medium
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

MailGuardian soll nicht nur Mails verwalten, sondern auch Termine. Google Calendar ist
der primäre Kalender-Provider. Die Integration benötigt OAuth2-Authentifizierung und
ermöglicht sowohl das Lesen als auch das Erstellen von Terminen — letzteres via
natürlichsprachige Eingabe, die vom LLM in strukturierte Event-Daten geparst wird.

## Erfolgskriterien

- `mg calendar auth` startet OAuth2-Flow im Browser und speichert Token
- `mg calendar view` zeigt heutige Termine als Rich-Tabelle (Zeit, Titel, Ort)
- `mg calendar view --day tomorrow` zeigt morgige Termine
- `mg calendar view --day 2026-03-10` zeigt beliebigen Tag
- `mg calendar add "Kaffee morgen um 10"` parst via LLM und erstellt Google-Event
- Credentials und Tokens werden in `~/.config/mailguardian/` gespeichert

## Umsetzung

### gcal.py — Google Calendar API Client
- `_get_credentials()` → Lädt Token aus `gcal_token.json`, refresht bei Ablauf, startet OAuth2-Flow bei Erstanmeldung
- `_save_token()` → Speichert Token als JSON
- `_parse_event_time()` → Parst dateTime (zeitspezifisch) und date (ganztägig) Formate
- `authenticate()` → Führt OAuth2-Flow aus, gibt True/False zurück
- `get_events(day, max_results)` → Holt Events für einen Tag via Calendar API v3
  - Berechnet Start/End als Tagesgrenzen (00:00 bis 23:59)
  - `singleEvents=True, orderBy=startTime` für aufgelöste recurring events
  - Gibt Liste von `CalendarEvent` Dataclasses zurück
- `create_event(summary, start, end, description, location)` → Erstellt Event via API
  - Timezone: Europe/Zurich (hardcoded — TODO: konfigurierbar machen)

### calendar_.py — CLI Commands
- `auth` → Prüft ob `gcal_credentials.json` existiert, startet OAuth2-Flow
- `view` → Zeigt Events als Rich-Tabelle (Time, Event, Location)
  - Ganztägige Events zeigen "All day"
  - Zeitspezifische Events zeigen "HH:MM–HH:MM"
- `add` → Natürlichsprachige Event-Erstellung:
  1. Sendet Text + aktuelles Datum an LLM
  2. LLM gibt JSON zurück: `{summary, start, end, location}`
  3. Strippt Markdown-Fences, parst JSON
  4. Erstellt Event via `create_event()`
  5. Zeigt Bestätigung mit Event-ID

### Credential-Dateien
- `~/.config/mailguardian/gcal_credentials.json` — OAuth2 Client-Secret (muss User manuell von Google Cloud Console herunterladen)
- `~/.config/mailguardian/gcal_token.json` — Gespeicherter Access/Refresh-Token (wird automatisch erstellt)

### Design-Entscheidungen
- **OAuth2 via InstalledAppFlow**: Öffnet lokalen HTTP-Server, Browser-Redirect — Standard für Desktop-CLI-Apps
- **Scope `calendar` (read+write)**: Braucht beides für view + add
- **LLM für natürliche Sprache**: Anstatt eigenen Parser zu bauen, nutzt das LLM das aktuelle Datum als Kontext und gibt strukturiertes JSON zurück
- **Lazy Imports**: `from mailguardian.gcal import ...` innerhalb der Command-Funktionen — CLI startet auch ohne Google-Credentials

### Betroffene Dateien
- `mailguardian/gcal.py` (neu)
- `mailguardian/calendar_.py` (komplett neu implementiert)

### Verifikation
```bash
# Voraussetzung: gcal_credentials.json in ~/.config/mailguardian/
mg calendar auth              # OAuth2 im Browser
mg calendar view              # Heutige Termine
mg calendar view --day tomorrow
mg calendar add "Meeting mit Max morgen 14 Uhr"
```

### Commit
`f3be883` — `feat: Google Calendar integration with OAuth2 and AI event creation (ref #4)`
