---
id: 9
title: Timezone konfigurierbar machen
status: open
priority: medium
labels: []
relations:
    blocks:
        - 10
created: "2026-03-04"
updated: "2026-03-04"
---

## Problem

In `gcal.py` ist die Timezone hardcoded als `"Europe/Zurich"`:

```python
# gcal.py:146-147
"start": {"dateTime": start.isoformat(), "timeZone": "Europe/Zurich"},
"end": {"dateTime": end.isoformat(), "timeZone": "Europe/Zurich"},
```

Das bedeutet:
- Events werden immer in Schweizer Zeit erstellt, egal wo der User ist
- `mg calendar view` zeigt Zeiten korrekt an (kommt von der API), aber `mg calendar add`
  schickt die Zeiten im falschen Kontext wenn der User nicht in CH ist
- Der Agent-Modus (`mg agent run`) hat aktuell kein Timezone-Problem, weil er keine
  Calendar-Events erstellt — aber sobald er das tut (z.B. "Meeting aus Mail in Kalender
  eintragen"), wird die Timezone relevant

## Kontext

### Wo Timezone überall relevant ist
1. **`gcal.py:create_event()`** — Timezone beim Event-Erstellen (aktuell hardcoded)
2. **`gcal.py:get_events()`** — Tagesgrenzen-Berechnung mit `datetime.now()` (nutzt lokale Zeit,
   hängt aber am "Z" Suffix an → wird als UTC interpretiert! Das ist ein **Bug**)
3. **`calendar_.py:add`** — LLM-generierte Zeiten haben keine explizite Timezone
4. **`agent.py`** — Timestamps im Log sind `time.strftime("%H:%M:%S")` (lokale Zeit, ok)

### Bug in get_events()
```python
# gcal.py:107-108
timeMin=start.isoformat() + "Z",  # ← "Z" = UTC, aber start ist lokale Zeit!
timeMax=end.isoformat() + "Z",
```
Das kann dazu führen, dass Events vom falschen Tag angezeigt werden wenn die lokale
Timezone weit von UTC entfernt ist. Für Europe/Zurich (UTC+1/+2) ist der Fehler gering,
aber für US-Timezones (UTC-5 bis -8) wird es problematisch.

## Erfolgskriterien

- [ ] `settings.yaml` unterstützt `timezone: "Europe/Zurich"` (oder beliebige IANA Timezone)
- [ ] Default: System-Timezone des Rechners (via `datetime.now().astimezone().tzinfo`)
- [ ] `gcal.py:create_event()` liest Timezone aus Settings statt Hardcoding
- [ ] `gcal.py:get_events()` Bug gefixt: Tagesgrenzen korrekt als timezone-aware datetimes
- [ ] `mg calendar add` LLM-Prompt enthält die konfigurierte Timezone als Kontext
- [ ] Neuer Config-Wert in `config.py:DEFAULT_SETTINGS`

## Betroffene Dateien

- `mailguardian/config.py` — `timezone` in DEFAULT_SETTINGS
- `mailguardian/gcal.py` — `create_event()` und `get_events()` timezone-aware machen
- `mailguardian/calendar_.py` — LLM-Prompt für `add` um Timezone ergänzen

## Hinweise zur Umsetzung

### System-Timezone ermitteln
```python
from datetime import datetime, timezone
import zoneinfo

# Python 3.9+
local_tz = datetime.now().astimezone().tzinfo
# Oder explizit:
tz = zoneinfo.ZoneInfo("Europe/Zurich")
```

### get_events() Fix
```python
from zoneinfo import ZoneInfo

tz = ZoneInfo(settings.get("timezone", "Europe/Zurich"))
start = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0)
# Kein "Z" Suffix mehr, stattdessen:
timeMin=start.isoformat()  # enthält automatisch den Offset
```

### LLM-Prompt Ergänzung
```python
f"Today is {datetime.now().strftime('%Y-%m-%d %A')}. Timezone: {timezone}. "
"All times in the output should be in this timezone."
```
