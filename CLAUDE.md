# CLAUDE.md – MailGuardian Project Conventions

## Project
MailGuardian is an agent-native CLI suite for email triage and calendar management.

## Package Manager
- **uv** – use `uv run mg` to run the CLI, `uv pip install -e .` for dev install

## Task Management — git-issues

**Binary:** `~/go/bin/git-issues` (installiert via `go install github.com/steviee/git-issues@latest`)

**WICHTIG:** Das Binary heißt `git-issues`, nicht `issues`. Ohne PATH-Eintrag immer mit vollem Pfad aufrufen.

### Workflow
1. Vor jeder Arbeit: `~/go/bin/git-issues list` — offene Issues prüfen
2. Issue claimen: `~/go/bin/git-issues claim <ID>`
3. Implementieren, committen mit Issue-Referenz
4. Issue schließen: `~/go/bin/git-issues done <ID>`

### Häufige Commands
```bash
~/go/bin/git-issues list                  # Offene Issues anzeigen
~/go/bin/git-issues list --status all     # Alle Issues (inkl. geschlossene)
~/go/bin/git-issues show <ID>             # Issue-Details anzeigen
~/go/bin/git-issues new -t "Titel" -b "Body" [-p high|medium|low]  # Neues Issue
~/go/bin/git-issues claim <ID>            # Issue als "in-progress" markieren
~/go/bin/git-issues done <ID>             # Issue schließen
~/go/bin/git-issues reopen <ID>           # Geschlossenes Issue wieder öffnen
~/go/bin/git-issues relate <ID> depends-on <ID>  # Abhängigkeit setzen
~/go/bin/git-issues blocked               # Blockierte Issues anzeigen
~/go/bin/git-issues next                  # Nächstes bearbeitbares Issue
```

### Issue-Dateien
- Gespeichert als Markdown in `.issues/NNNN-slug.md`
- YAML-Frontmatter mit id, title, status, priority, labels, relations
- Body ist freier Markdown — soll ausführlich dokumentiert sein (Kontext, Erfolgskriterien, Umsetzung, betroffene Dateien)
- Können direkt editiert werden (Frontmatter-Felder beachten)

### Commit-Format
- `feat: description (ref #ID)` — neues Feature
- `fix: description (ref #ID)` — Bugfix
- `docs: description (ref #ID)` — Dokumentation
- Jeder Commit muss einem Issue zugeordnet sein

## Config
- User config directory: `~/.config/mailguardian/`
- Accounts file: `~/.config/mailguardian/accounts.yaml`

## Architecture
- CLI entry point: `mailguardian/cli.py` → `mg` command
- Subcommand groups: `auth`, `inbox`, `calendar`, `agent`
- Multi-account IMAP support (Gmail, Outlook, generic IMAP servers)
- `calendar_.py` has trailing underscore to avoid stdlib collision

## LLM
- Primary backend: **Ollama** (local, via OpenAI-compatible API)
- Default model: `ollama_chat/llama3.2` (configurable in `~/.config/mailguardian/settings.yaml`)
- LiteLLM handles provider abstraction — any LiteLLM-compatible model works
- Central default: `mailguardian/config.py:DEFAULT_LLM_MODEL`

## Key Dependencies
- typer (CLI framework)
- imapclient (IMAP)
- google-api-python-client + google-auth-oauthlib (Calendar)
- litellm (LLM integration, provider-agnostic)
- rich (terminal output)
- keyring (secure password storage)
