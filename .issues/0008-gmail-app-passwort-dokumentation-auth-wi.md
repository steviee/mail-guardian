---
id: 8
title: Gmail App-Passwort Dokumentation & Auth-Wizard Verbesserung
status: open
priority: high
labels: []
created: "2026-03-04"
updated: "2026-03-04"
---

## Problem

Gmail ist der häufigste IMAP-Provider und gleichzeitig der komplizierteste. Google erlaubt
seit Mai 2022 **kein normales Passwort mehr** für IMAP-Zugriff. Stattdessen braucht man ein
**App-Passwort** — und dafür muss 2FA aktiviert sein.

Der aktuelle Auth-Wizard (`mg auth add`) fragt einfach nach "Password (app-password recommended)",
aber erklärt nicht:
- Was ein App-Passwort ist
- Wo man es erstellt
- Dass 2FA Voraussetzung ist
- Was passiert, wenn man ein normales Passwort eingibt (Login schlägt fehl)

Ein User, der `mg auth add` ausführt und sein normales Gmail-Passwort eingibt, bekommt
erst beim `mg auth test` oder `mg inbox list` einen kryptischen IMAP-Fehler wie
"AUTHENTICATIONFAILED" — ohne hilfreichen Hinweis.

## Kontext

### Gmail App-Passwort-Voraussetzungen
1. Google-Account mit **2-Faktor-Authentifizierung (2FA)** aktiviert
2. App-Passwort erstellen unter: https://myaccount.google.com/apppasswords
3. Das generierte 16-Zeichen-Passwort verwenden (nicht das Account-Passwort)

### Andere Provider
- **Outlook**: Unterstützt normales Passwort + IMAP, bei 2FA ebenfalls App-Passwort nötig
- **Yahoo**: App-Passwort nötig seit 2013
- **Generic IMAP**: Meistens normales Passwort, hängt vom Server ab

## Erfolgskriterien

- [ ] `mg auth add` mit Provider `gmail` zeigt **vor der Passwort-Abfrage** einen Hinweis:
      ```
      ⚠ Gmail erfordert ein App-Passwort (kein normales Passwort).
        1. 2FA aktivieren: https://myaccount.google.com/signinoptions/two-step-verification
        2. App-Passwort erstellen: https://myaccount.google.com/apppasswords
        3. Das generierte 16-Zeichen-Passwort hier eingeben.
      ```
- [ ] `mg auth add` mit Provider `outlook` zeigt analogen Hinweis wenn relevant
- [ ] `mg auth test` gibt bei AUTHENTICATION-Fehler einen **provider-spezifischen Hinweis**:
      - Gmail: "Nutzt du ein App-Passwort? → https://myaccount.google.com/apppasswords"
      - Outlook: "Bei aktivierter 2FA brauchst du ein App-Passwort"
      - Generic: "Prüfe Username und Passwort"
- [ ] Neuer Command `mg auth guide <provider>` der eine vollständige Setup-Anleitung für
      den jeweiligen Provider anzeigt (gmail, outlook, yahoo, generic)
- [ ] `mg auth test` Fehlermeldungen sind klar und actionable

## Betroffene Dateien

- `mailguardian/auth.py` — Hinweise im `add` Wizard, verbesserter `test` Error-Handler, neuer `guide` Command
- `mailguardian/accounts.py` — Optional: Provider-spezifische Hinweis-Texte als Konstanten

## Hinweise zur Umsetzung

### Provider-Hinweise als Dict
```python
PROVIDER_AUTH_HINTS = {
    "gmail": {
        "setup_hint": "Gmail erfordert ein App-Passwort...",
        "setup_url": "https://myaccount.google.com/apppasswords",
        "prereq_url": "https://myaccount.google.com/signinoptions/two-step-verification",
        "error_hint": "IMAP-Login fehlgeschlagen. Nutzt du ein App-Passwort?",
    },
    "outlook": { ... },
    "yahoo": { ... },
}
```

### Typische IMAP-Fehlermeldungen
- Gmail: `[AUTHENTICATIONFAILED] Invalid credentials (Failure)`
- Gmail ohne App-PW: `Please log in via your web browser`
- Outlook: `LOGIN failed`

### Interaktiver Guide
`mg auth guide gmail` könnte eine Rich-Panel-Anleitung zeigen mit nummerierten Schritten,
URLs, und am Ende die Frage "Möchtest du jetzt einen Account hinzufügen?" → leitet zu `mg auth add` weiter.
