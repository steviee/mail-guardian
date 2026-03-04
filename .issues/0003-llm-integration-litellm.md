---
id: 3
title: LLM Integration (LiteLLM)
status: closed
priority: medium
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

Mails sollen nicht nur gelesen, sondern automatisch analysiert werden können.
LiteLLM dient als Provider-agnostische Abstraktionsschicht — unterstützt OpenAI, Anthropic,
Ollama und dutzende weitere Backends mit einheitlicher API.

## Erfolgskriterien

- `mg inbox summarize <UID>` generiert eine 1-3 Satz Zusammenfassung via LLM
- `mg inbox scan --ai` klassifiziert Mails nach Kategorie, Priorität und Handlungsbedarf
- Klassifikation liefert strukturiertes JSON: `{category, priority, action_required, summary}`
- Fortschrittsanzeige bei Batch-Klassifikation
- `--model` Flag erlaubt Model-Override
- settings.yaml speichert das Standard-Model zentral

## Umsetzung

### llm.py — LLM-Funktionen
- `summarize_mail(subject, body, model)` → Sendet Mail an LLM mit System-Prompt für Zusammenfassung, max 200 Tokens
- `classify_mail(subject, body, model)` → Klassifikation als JSON mit:
  - `category`: meeting, support, newsletter, billing, personal, spam, other
  - `priority`: high, medium, low
  - `action_required`: boolean
  - `summary`: Einzeiler
- `classify_batch(mails, model)` → Batch-Verarbeitung mehrerer Mails
- Robustes JSON-Parsing: Strippt Markdown-Code-Fences, Fallback bei Parse-Fehler

### inbox.py — Neue/erweiterte Commands
- `scan --ai` → Holt für jede Mail den Body via IMAP, klassifiziert via LLM, zeigt Rich-Tabelle mit:
  - UID, Category, Priority (farbcodiert), Action-Required-Flag, Subject, Summary
  - `rich.progress.Progress` Fortschrittsbalken während Klassifikation
- `summarize <UID>` → Neuer Command, zeigt AI-Zusammenfassung in grünem Rich-Panel
- `--model` Flag bei scan und summarize

### config.py — Settings-System
- `SETTINGS_FILE = ~/.config/mailguardian/settings.yaml`
- `DEFAULT_SETTINGS = {"llm_model": ..., "check_interval": 300}`
- `load_settings()` → Merged User-Settings mit Defaults
- `save_settings()` → Schreibt Settings auf Disk

### Design-Entscheidungen
- **LiteLLM statt direkter API-Calls**: Ein Interface für alle Provider — Wechsel von OpenAI zu Ollama = nur Model-String ändern
- **JSON-Output vom LLM**: Strukturiert, maschinenlesbar, weiterverarbeitbar durch Agent
- **Body-Truncation auf 2000 Zeichen**: Verhindert Token-Explosion bei langen Mails
- **Lazy Import**: `from mailguardian.llm import ...` nur innerhalb der Funktionen, die es brauchen — CLI startet schnell auch ohne LLM-Config

### Betroffene Dateien
- `mailguardian/llm.py` (neu)
- `mailguardian/inbox.py` (erweitert: scan --ai, summarize)
- `mailguardian/config.py` (erweitert: SETTINGS_FILE, load/save_settings)

### Verifikation
```bash
mg inbox scan --ai --limit 3                    # AI-Klassifikation
mg inbox scan --ai --model ollama_chat/llama3.2  # Mit spezifischem Model
mg inbox summarize <UID>                         # Einzelne Mail zusammenfassen
```

### Commit
`da980c1` — `feat: LLM integration via LiteLLM for mail analysis (ref #3)`
