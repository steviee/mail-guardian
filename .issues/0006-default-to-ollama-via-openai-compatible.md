---
id: 6
title: Default to Ollama via OpenAI-compatible API
status: closed
priority: high
labels: []
created: "2026-03-04"
updated: "2026-03-04"
closed: "2026-03-04"
---

## Kontext

User-Entscheidung: Das Projekt soll primär **Ollama** als lokales LLM-Backend nutzen,
nicht einen Cloud-Provider. Ollama bietet eine OpenAI-kompatible API auf `localhost:11434`.
LiteLLM unterstützt Ollama nativ via `ollama_chat/<model>` Prefix.

Vorteile: Kein API-Key nötig, keine Kosten, Daten bleiben lokal, schnelle Iteration.

## Erfolgskriterien

- Default-Model ist `ollama_chat/llama3.2` (statt `gpt-4o-mini`)
- Zentrale Konstante `DEFAULT_LLM_MODEL` in `config.py` — kein Hardcoding verstreut
- Alle `--model` Flags zeigen den neuen Default
- `settings.yaml` default zeigt Ollama-Model
- CLAUDE.md dokumentiert Ollama als Primary Backend
- Andere Provider (OpenAI, Anthropic, etc.) bleiben via `--model` Flag nutzbar

## Umsetzung

### config.py
- Neue Konstante: `DEFAULT_LLM_MODEL = "ollama_chat/llama3.2"`
- `DEFAULT_SETTINGS["llm_model"]` referenziert die Konstante

### Alle Module aktualisiert
- `llm.py`: `summarize_mail()`, `classify_mail()`, `classify_batch()` → Default-Parameter auf `DEFAULT_LLM_MODEL`
- `inbox.py`: `scan --model`, `summarize --model` → Default auf `DEFAULT_LLM_MODEL`
- `calendar_.py`: `add --model` → Default auf `DEFAULT_LLM_MODEL`
- `agent.py`: Fallback-Werte auf `DEFAULT_LLM_MODEL`

### CLAUDE.md
- Neuer Abschnitt "LLM" mit Ollama-Dokumentation
- keyring als Dependency dokumentiert

### Design-Entscheidungen
- **`ollama_chat/` Prefix** (nicht `ollama/`): LiteLLM's `ollama_chat/` nutzt die `/api/chat` Endpoint, die Chat-Completions korrekt unterstützt (mit System-Messages etc.)
- **Zentrale Konstante statt Suchen-und-Ersetzen**: Zukünftige Model-Änderungen = eine Zeile
- **Kein Breaking Change**: `--model` Flag erlaubt weiterhin jeden LiteLLM-kompatiblen Provider

### Betroffene Dateien
- `mailguardian/config.py` (geändert: DEFAULT_LLM_MODEL)
- `mailguardian/llm.py` (geändert: Default-Parameter)
- `mailguardian/inbox.py` (geändert: Default-Parameter)
- `mailguardian/calendar_.py` (geändert: Default-Parameter)
- `mailguardian/agent.py` (geändert: Fallback-Werte)
- `CLAUDE.md` (erweitert: LLM-Dokumentation)

### Verifikation
```bash
grep -r "gpt-4o-mini" mailguardian/    # Sollte 0 Treffer ergeben
mg inbox scan --help                    # Default-Model zeigt ollama_chat/llama3.2
uv run python -c "from mailguardian.config import DEFAULT_LLM_MODEL; print(DEFAULT_LLM_MODEL)"
```

### Commit
`1fd164b` — `feat: default LLM to Ollama via OpenAI-compatible API (ref #6)`
