---
id: 10
title: CalDAV/iCal Support als Alternative zu Google Calendar
status: open
priority: low
labels: []
relations:
    depends-on:
        - 9
created: "2026-03-04"
updated: "2026-03-04"
---

## Problem

Die PRD spezifiziert "Kalender (Google/**iCal**)", aber implementiert ist **nur Google Calendar**.
Benutzer, die keinen Google-Account haben oder ihren Kalender selbst hosten (Nextcloud, Radicale,
Baikal, Synology, etc.), können den Kalender-Teil von MailGuardian nicht nutzen.

CalDAV ist der offene Standard für Kalender-Zugriff und wird unterstützt von:
- Nextcloud
- Radicale
- Baikal
- macOS/iCloud Calendar
- Synology Calendar
- Fastmail
- Und vielen weiteren

## Kontext

### Aktueller Stand
- `mailguardian/gcal.py` — Google Calendar API Client (proprietäre REST API)
- `mailguardian/calendar_.py` — CLI Commands, importiert direkt aus `gcal.py`
- Keine Abstraktion: Die CLI ist direkt an Google gebunden

### CalDAV vs Google Calendar API
| Aspekt | Google Calendar API | CalDAV |
|--------|-------------------|--------|
| Auth | OAuth2 (komplex) | Basic Auth oder OAuth2 |
| Setup | Cloud Console, Credentials-JSON | Nur URL + Username + Passwort |
| Dependency | `google-api-python-client` | `caldav` (Python-Library) |
| Hosting | Nur Google | Jeder CalDAV-Server |
| Offline | Nein | Server kann lokal laufen |

### Multi-Calendar ähnlich wie Multi-Account IMAP
Analog zum IMAP Multi-Account-System (Issue #2) könnte ein Multi-Calendar-System funktionieren:

```yaml
# ~/.config/mailguardian/calendars.yaml
calendars:
  - name: google-privat
    provider: google
    # Nutzt gcal.py mit OAuth2
    default: true

  - name: nextcloud-work
    provider: caldav
    url: https://cloud.example.com/remote.php/dav/calendars/user/personal/
    username: user
    # Passwort in Keyring

  - name: icloud
    provider: caldav
    url: https://caldav.icloud.com/
    username: user@icloud.com
```

## Erfolgskriterien

- [ ] Abstrakte `CalendarProvider`-Schnittstelle die Google und CalDAV vereint
- [ ] `mg calendar view` funktioniert mit CalDAV-Server
- [ ] `mg calendar add` funktioniert mit CalDAV-Server
- [ ] Multi-Calendar analog zu Multi-Account IMAP: `--calendar` Flag
- [ ] `mg calendar auth` unterstützt CalDAV (simpel: URL + Username + Passwort im Keyring)
- [ ] `calendars.yaml` Konfigurationsdatei
- [ ] Bestehende Google-Calendar-Funktionalität bleibt unverändert
- [ ] `caldav` Library als optionale Dependency (nicht jeder braucht es)

## Betroffene Dateien

### Neue Dateien
- `mailguardian/caldav_client.py` — CalDAV-Client analog zu `gcal.py`
- `mailguardian/calendar_provider.py` — Abstrakte Schnittstelle / Protocol

### Zu ändern
- `mailguardian/calendar_.py` — Provider-Auswahl statt direktem `gcal.py` Import
- `mailguardian/config.py` — `CALENDARS_FILE` Pfad
- `pyproject.toml` — `caldav` als optionale Dependency

## Hinweise zur Umsetzung

### CalDAV Python Library
```bash
uv pip install caldav
```

```python
import caldav

client = caldav.DAVClient(
    url="https://cloud.example.com/remote.php/dav/",
    username="user",
    password="pass",
)
principal = client.principal()
calendars = principal.calendars()
calendar = calendars[0]

# Events eines Tages abrufen
events = calendar.search(
    start=datetime(2026, 3, 4),
    end=datetime(2026, 3, 5),
    event=True,
)

# Event erstellen
from icalendar import Calendar, Event
cal = Calendar()
event = Event()
event.add("summary", "Meeting")
event.add("dtstart", datetime(2026, 3, 5, 14, 0))
event.add("dtend", datetime(2026, 3, 5, 15, 0))
cal.add_component(event)
calendar.save_event(cal.to_ical())
```

### Provider-Abstraktion (Protocol)
```python
from typing import Protocol

class CalendarProvider(Protocol):
    def get_events(self, day: str) -> list[CalendarEvent]: ...
    def create_event(self, summary: str, start: datetime, end: datetime, **kwargs) -> dict: ...
    def authenticate(self) -> bool: ...
```

### Optionale Dependency in pyproject.toml
```toml
[project.optional-dependencies]
caldav = ["caldav>=1.0", "icalendar>=6.0"]
```

### Reihenfolge der Umsetzung
1. `CalendarProvider` Protocol definieren
2. `gcal.py` an das Protocol anpassen (ohne Breaking Changes)
3. `caldav_client.py` implementieren
4. `calendar_.py` um Provider-Auswahl erweitern
5. `calendars.yaml` Config-System
6. Tests mit einem lokalen Radicale-Server

## Abhängigkeiten

- Issue #9 (Timezone) sollte vorher oder gleichzeitig umgesetzt werden, da CalDAV-Events
  timezone-aware iCalendar-Objekte verwenden
