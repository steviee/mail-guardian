# PRD: MailGuardian CLI

## 1. Projekt-Vision
**MailGuardian** ist eine modulare CLI-Suite, die E-Mail-Postfächer (IMAP) und Kalender (Google/iCal) für KI-Agenten (z. B. Claude Code, OpenClaw) zugänglich macht. Ziel ist die Automatisierung von Triage, Antwort-Entwürfen und Terminmanagement durch eine rein textbasierte Schnittstelle.

---

## 2. Kern-Philosophie: "Agent-Native Management"
Dieses Projekt wird **ausnahmslos** über das Tool `git-issues` verwaltet.
* **Source of Truth:** Der Aufgabenstatus wird im Branch `refs/heads/git-issues` gespeichert.
* **Workflow:** Der KI-Agent muss vor jedem Arbeitsschritt den Status via `git issues list` prüfen.
* **Dokumentation:** Jede Code-Änderung muss einem Issue zugeordnet sein. Commits sollten die Form `feat: add imap login (ref #ID)` haben.
* **Autonomie:** Der Agent ist ausdrücklich aufgefordert, bei technischer Komplexität Unteraufgaben als neue Issues anzulegen.

---

## 3. Technische Spezifikationen

### Stack
* **Sprache:** Python 3.10+
* **CLI-Framework:** `Typer` (für intuitive Subcommands)
* **E-Mail:** `imaplib` / `email` (Standard-Lib) oder `imapclient`
* **Kalender:** `google-api-python-client` / `google-auth-oauthlib`
* **KI-Schnittstelle:** `LiteLLM` (für herstellerunabhängige LLM-Aufrufe)
* **Task-Management:** `git-issues` (@steviee)

### Modul-Struktur (`mg` Kommando)
1.  **`mg auth`**: Initialisiert OAuth2-Flows und speichert verschlüsselte Credentials/Tokens lokal.
2.  **`mg inbox`**:
    * `list [--limit N]`: Zeigt die neuesten E-Mails.
    * `scan --ai`: Klassifiziert Mails (z. B. "Support", "Meeting-Anfrage", "Spam").
    * `show <ID>`: Gibt den Mail-Body im Plain-Text aus.
3.  **`mg calendar`**:
    * `view --day [today|tomorrow]`: Listet Termine.
    * `add "Text"`: Nutzt KI, um "Kaffee morgen um 10" in ein API-Event zu wandeln.
4.  **`mg agent` (Daemon/Loop)**: Ein Modus, der periodisch die Inbox prüft und basierend auf lokalen "Playbooks" (JSON/YAML) Aktionen auslöst.

---

## 4. Initiales Backlog für `git-issues`

Der Agent soll nach dem Start folgende Issues initial anlegen:

| ID | Titel | Erfolgskriterium |
| :--- | :--- | :--- |
| #1 | **Project Scaffold & Git-Issues Setup** | `pyproject.toml` existiert, `git issues init` ausgeführt. |
| #2 | **IMAP Core Module** | Abruf von Mail-Listen via CLI funktioniert. |
| #3 | **LLM Integration (LiteLLM)** | CLI kann Mail-Inhalte an ein LLM senden und Zusammenfassung ausgeben. |
| #4 | **Google Calendar Integration** | Authentifizierung erfolgt; Termine werden im Terminal gelistet. |
| #5 | **Autonomous Dispatcher (`mg agent`)** | Grundgerüst für den Loop, der Mails liest und kategorisiert. |

---

## 5. Instruktionen für den KI-Agenten (System-Prompt Ergänzung)

### Phase 1: Planung & Initialisierung
1.  Lies diese `PRD.md` vollständig.
2.  Initialisiere das Git-Repository.
3.  Installiere `git-issues` (oder nutze das Binary) und führe `git issues init` aus.
4.  Erstelle die Issues #1 bis #5.
5.  **Stoppe hier** und frage den Nutzer nach den bevorzugten Provider-Daten (Gmail, Outlook, etc.) und dem Speicherort für Configs.

### Phase 2: Iterative Umsetzung
* Wähle das Issue mit der niedrigsten ID.
* Erstelle einen Feature-Branch.
* Implementiere die Funktion.
* Schließe das Issue mit `git issues close <ID>`.
* Merge den Branch und lösche ihn lokal.

---

## 6. Erfolgskriterien
* Das Tool ist für andere Agenten über `stdout` (JSON-formatiert) konsumierbar.
* Die gesamte Entwicklungshistorie ist über `git issues list --all` nachvollziehbar.
* Keine "toten" Features: Jede Zeile Code hat ein entsprechendes Issue.

---
**Status:** Ready for Implementation.

