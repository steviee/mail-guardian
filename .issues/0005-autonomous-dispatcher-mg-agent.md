---
id: 5
title: Autonomous Dispatcher (mg agent)
status: closed
priority: medium
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

Der Agent ist das Herzstück von MailGuardian — ein autonomer Loop, der periodisch
die Inbox prüft, ungelesene Mails via LLM klassifiziert und basierend auf
konfigurierbaren Playbooks automatisch Aktionen auslöst. Ermöglicht "fire and forget"
Mail-Triage ohne manuelle Interaktion.

## Erfolgskriterien

- `mg agent run` startet den periodischen Loop (Standard: alle 300s)
- `mg agent run --once` führt einen einzelnen Zyklus aus und beendet sich
- Agent erkennt ungelesene Mails, klassifiziert sie via LLM, wendet Playbooks an
- `mg agent playbooks` zeigt alle konfigurierten Playbooks
- `mg agent status` zeigt Konfiguration und Bereitschaft
- Graceful Shutdown via Ctrl+C (SIGINT/SIGTERM)
- Playbooks sind YAML-Dateien in `~/.config/mailguardian/playbooks/`

## Umsetzung

### playbooks.py — Playbook-System
- **Datenmodell**:
  - `Playbook`: name, description, match (dict), action (PlaybookAction)
  - `PlaybookAction`: type (log/flag/notify/move), params (dict)
- `load_playbooks()` → Lädt alle `*.yaml` Dateien aus `~/.config/mailguardian/playbooks/`
- `create_default_playbooks()` → Erstellt Beispiel-Playbooks bei Erststart:
  - `example-spam-filter.yaml`: Loggt erkannten Spam
  - `example-meeting-alert.yaml`: Flaggt Meeting-Anfragen
- `Playbook.matches(classification)` → Prüft ob LLM-Klassifikation alle Match-Kriterien erfüllt

### Playbook-Format (YAML)
```yaml
name: spam-filter
description: Log detected spam mails
match:
  category: spam           # Muss exakt matchen
action:
  type: log                # log | flag | notify | move
  message: "Spam detected: {subject}"  # Template mit {subject}, {category}, {priority}
```

### agent.py — CLI Commands & Loop
- **`run` Command**:
  - Lädt Settings (Model, Interval), Playbooks
  - Zeigt Startup-Info (Model, Interval, Playbook-Count)
  - Loop: Timestamp → `_run_cycle()` → Sleep (in 1s-Schritten für Signal-Reaktion)
  - `--once` Flag für Einmalausführung
  - `--interval`, `--model`, `--limit`, `--account` Flags
- **`_run_cycle()`**:
  1. Verbindet sich zum IMAP-Account
  2. Holt Mail-Liste, filtert auf ungelesene
  3. Für jede ungelesene Mail: Holt Body, klassifiziert via LLM
  4. Zeigt Ergebnis: UID, Subject, Category, Priority, Action-Flag
  5. Prüft alle Playbooks gegen Klassifikation, führt matching Actions aus
- **`_execute_action()`**: Führt Playbook-Actions aus (aktuell: log, flag, notify als Console-Output)
- **`playbooks` Command**: Rich-Tabelle mit Name, Description, Match, Action
- **`status` Command**: Zeigt Account-Count, Playbook-Count, Model, Interval, Readiness

### Signal-Handling
- `SIGINT` (Ctrl+C) und `SIGTERM` setzen `_running = False`
- Sleep-Loop prüft `_running` jede Sekunde → schnelle Reaktion auf Shutdown
- Saubere Abschlussmeldung

### Design-Entscheidungen
- **Playbooks statt Hardcoded Rules**: Benutzer können eigene Regeln definieren, ohne Code zu ändern
- **Einfaches Match-System**: Key-Value Gleichheit auf LLM-Klassifikation — erweiterbar auf Regex, Ranges etc.
- **Actions als Plugins**: `type` bestimmt das Verhalten — aktuell Console-Output, erweiterbar auf tatsächliche Mail-Operationen (move, forward, reply)
- **Nur ungelesene Mails**: Verhindert redundante Verarbeitung
- **1s Sleep-Granularität**: Kompromiss zwischen CPU-Schonung und schneller Signal-Reaktion

### Betroffene Dateien
- `mailguardian/playbooks.py` (neu)
- `mailguardian/agent.py` (komplett neu implementiert)

### Verifikation
```bash
mg agent status               # Zeigt Config und Readiness
mg agent playbooks            # Zeigt geladene Playbooks
mg agent run --once           # Ein Zyklus
mg agent run --interval 60    # Loop alle 60s
mg agent run --once --model ollama_chat/llama3.2  # Mit spezifischem Model
```

### Commit
`3c3588e` — `feat: autonomous dispatcher with playbook system (ref #5)`
