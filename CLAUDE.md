# CLAUDE.md – MailGuardian Project Conventions

## Project
MailGuardian is an agent-native CLI suite for email triage and calendar management.

## Package Manager
- **uv** – use `uv run mg` to run the CLI, `uv pip install -e .` for dev install

## Task Management
- **git-issues** (`~/go/bin/git-issues`) – all work must reference an issue
- Before starting work: `git-issues list` to check open issues
- Commit format: `feat: description (ref #ID)` / `fix: description (ref #ID)`
- Close issues with: `git-issues done <ID>`

## Config
- User config directory: `~/.config/mailguardian/`
- Accounts file: `~/.config/mailguardian/accounts.yaml`

## Architecture
- CLI entry point: `mailguardian/cli.py` → `mg` command
- Subcommand groups: `auth`, `inbox`, `calendar`, `agent`
- Multi-account IMAP support (Gmail, Outlook, generic IMAP servers)
- `calendar_.py` has trailing underscore to avoid stdlib collision

## Key Dependencies
- typer (CLI framework)
- imapclient (IMAP)
- google-api-python-client + google-auth-oauthlib (Calendar)
- litellm (LLM integration)
- rich (terminal output)
