"""LLM integration via LiteLLM for mail analysis."""

from __future__ import annotations

import json

import litellm

from mailguardian.config import DEFAULT_LLM_MODEL


def summarize_mail(subject: str, body: str, model: str = DEFAULT_LLM_MODEL) -> str:
    """Generate a concise summary of an email."""
    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an email assistant. Summarize the following email "
                    "in 1-3 sentences. Be concise and focus on actionable items."
                ),
            },
            {
                "role": "user",
                "content": f"Subject: {subject}\n\n{body}",
            },
        ],
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


def classify_mail(subject: str, body: str, model: str = DEFAULT_LLM_MODEL) -> dict:
    """Classify an email into categories.

    Returns dict with keys: category, priority, action_required.
    """
    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an email classifier. Analyze the email and return a JSON object with:\n"
                    '- "category": one of "meeting", "support", "newsletter", "billing", "personal", "spam", "other"\n'
                    '- "priority": one of "high", "medium", "low"\n'
                    '- "action_required": boolean\n'
                    '- "summary": one-sentence summary\n'
                    "Return ONLY valid JSON, no markdown."
                ),
            },
            {
                "role": "user",
                "content": f"Subject: {subject}\n\n{body[:2000]}",
            },
        ],
        max_tokens=200,
    )

    raw = response.choices[0].message.content.strip()
    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {
            "category": "other",
            "priority": "medium",
            "action_required": False,
            "summary": raw,
        }


def classify_batch(
    mails: list[dict],
    model: str = DEFAULT_LLM_MODEL,
) -> list[dict]:
    """Classify multiple mails. Each mail dict needs 'subject' and 'body' keys."""
    results = []
    for mail in mails:
        result = classify_mail(mail["subject"], mail.get("body", ""), model=model)
        result["uid"] = mail.get("uid")
        result["subject"] = mail["subject"]
        results.append(result)
    return results
