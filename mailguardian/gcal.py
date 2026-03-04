"""Google Calendar API client."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from mailguardian.config import CONFIG_DIR, ensure_config_dir

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_FILE = CONFIG_DIR / "gcal_token.json"
CREDENTIALS_FILE = CONFIG_DIR / "gcal_credentials.json"


@dataclass
class CalendarEvent:
    """Representation of a calendar event."""

    id: str
    summary: str
    start: datetime | None
    end: datetime | None
    location: str
    description: str
    all_day: bool


def _get_credentials() -> Credentials:
    """Get or refresh Google Calendar credentials."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_token(creds)
    elif not creds or not creds.valid:
        if not CREDENTIALS_FILE.exists():
            raise FileNotFoundError(
                f"Google credentials file not found at {CREDENTIALS_FILE}\n"
                "Download it from Google Cloud Console → APIs & Services → Credentials\n"
                "and save as 'gcal_credentials.json' in ~/.config/mailguardian/"
            )
        flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
        creds = flow.run_local_server(port=0)
        _save_token(creds)

    return creds


def _save_token(creds: Credentials) -> None:
    """Save token to disk."""
    ensure_config_dir()
    TOKEN_FILE.write_text(creds.to_json())


def _parse_event_time(event: dict, key: str) -> tuple[datetime | None, bool]:
    """Parse start/end time from a Google Calendar event."""
    time_info = event.get(key, {})
    if "dateTime" in time_info:
        return datetime.fromisoformat(time_info["dateTime"]), False
    elif "date" in time_info:
        return datetime.fromisoformat(time_info["date"]), True
    return None, False


def authenticate() -> bool:
    """Run the OAuth2 flow and store credentials. Returns True on success."""
    try:
        _get_credentials()
        return True
    except Exception:
        return False


def get_events(
    day: str = "today",
    max_results: int = 20,
) -> list[CalendarEvent]:
    """Fetch calendar events for a given day."""
    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    now = datetime.now()
    if day == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif day == "tomorrow":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        start = datetime.fromisoformat(day)

    end = start + timedelta(days=1)

    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=start.isoformat() + "Z",
            timeMax=end.isoformat() + "Z",
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    events = []
    for item in events_result.get("items", []):
        start_dt, all_day = _parse_event_time(item, "start")
        end_dt, _ = _parse_event_time(item, "end")
        events.append(CalendarEvent(
            id=item["id"],
            summary=item.get("summary", "(no title)"),
            start=start_dt,
            end=end_dt,
            location=item.get("location", ""),
            description=item.get("description", ""),
            all_day=all_day,
        ))

    return events


def create_event(
    summary: str,
    start: datetime,
    end: datetime,
    description: str = "",
    location: str = "",
) -> dict:
    """Create a new calendar event."""
    creds = _get_credentials()
    service = build("calendar", "v3", credentials=creds)

    event_body = {
        "summary": summary,
        "start": {"dateTime": start.isoformat(), "timeZone": "Europe/Zurich"},
        "end": {"dateTime": end.isoformat(), "timeZone": "Europe/Zurich"},
    }
    if description:
        event_body["description"] = description
    if location:
        event_body["location"] = location

    result = service.events().insert(calendarId="primary", body=event_body).execute()
    return result
