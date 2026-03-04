"""IMAP client wrapper for multi-account mail access."""

from __future__ import annotations

import email
import email.header
import email.utils
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from imapclient import IMAPClient


@dataclass
class MailSummary:
    """Lightweight representation of an email for listing."""

    uid: int
    subject: str
    sender: str
    date: datetime | None
    flags: list[str]

    @property
    def is_unread(self) -> bool:
        return b"\\Seen" not in self.flags and "\\Seen" not in self.flags


@dataclass
class MailDetail:
    """Full email content for display."""

    uid: int
    subject: str
    sender: str
    to: str
    date: datetime | None
    body_text: str
    body_html: str | None


def _decode_header(raw: str | bytes | None) -> str:
    """Decode an RFC2047-encoded header value."""
    if raw is None:
        return ""
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8", errors="replace")
    parts = email.header.decode_header(raw)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return " ".join(decoded)


def _extract_body(msg: email.message.Message) -> tuple[str, str | None]:
    """Extract plain text and optional HTML body from a message."""
    text_body = ""
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain" and not text_body:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    text_body = payload.decode(charset, errors="replace")
            elif content_type == "text/html" and html_body is None:
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html_body = payload.decode(charset, errors="replace")
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            content_type = msg.get_content_type()
            text = payload.decode(charset, errors="replace")
            if content_type == "text/html":
                html_body = text
            else:
                text_body = text

    return text_body, html_body


def connect(host: str, port: int, username: str, password: str) -> IMAPClient:
    """Connect and authenticate to an IMAP server."""
    client = IMAPClient(host, port=port, ssl=True)
    client.login(username, password)
    return client


def fetch_mail_list(
    client: IMAPClient,
    folder: str = "INBOX",
    limit: int = 10,
) -> list[MailSummary]:
    """Fetch a list of recent mails from the given folder."""
    client.select_folder(folder, readonly=True)
    messages = client.search(["ALL"])
    # Take the most recent `limit` messages
    recent_uids = messages[-limit:] if len(messages) > limit else messages
    if not recent_uids:
        return []

    fetched = client.fetch(recent_uids, ["ENVELOPE", "FLAGS"])
    results = []
    for uid, data in fetched.items():
        env = data[b"ENVELOPE"]
        flags = [f.decode() if isinstance(f, bytes) else f for f in data[b"FLAGS"]]
        sender_addr = ""
        if env.from_ and len(env.from_) > 0:
            fr = env.from_[0]
            name = fr.name.decode("utf-8", errors="replace") if fr.name else ""
            mailbox = (fr.mailbox or b"").decode("utf-8", errors="replace")
            host = (fr.host or b"").decode("utf-8", errors="replace")
            sender_addr = f"{name} <{mailbox}@{host}>" if name else f"{mailbox}@{host}"

        subject = _decode_header(env.subject.decode("utf-8", errors="replace") if isinstance(env.subject, bytes) else env.subject) if env.subject else "(no subject)"

        results.append(MailSummary(
            uid=uid,
            subject=subject,
            sender=sender_addr,
            date=env.date,
            flags=flags,
        ))

    # Sort by date descending (newest first)
    results.sort(key=lambda m: m.date or datetime.min, reverse=True)
    return results


def fetch_mail_detail(client: IMAPClient, uid: int, folder: str = "INBOX") -> MailDetail | None:
    """Fetch full content of a single mail by UID."""
    client.select_folder(folder, readonly=True)
    fetched = client.fetch([uid], ["RFC822"])
    if uid not in fetched:
        return None

    raw = fetched[uid][b"RFC822"]
    msg = email.message_from_bytes(raw)
    text_body, html_body = _extract_body(msg)

    return MailDetail(
        uid=uid,
        subject=_decode_header(msg["Subject"]),
        sender=_decode_header(msg["From"]),
        to=_decode_header(msg["To"]),
        date=email.utils.parsedate_to_datetime(msg["Date"]) if msg["Date"] else None,
        body_text=text_body,
        body_html=html_body,
    )
