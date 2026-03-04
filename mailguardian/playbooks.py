"""Playbook system for the autonomous dispatcher.

Playbooks define rules for automatic mail handling. They are stored as
YAML files in ~/.config/mailguardian/playbooks/.

Example playbook:
    name: spam-filter
    description: Auto-archive spam
    match:
      category: spam
    action:
      type: log
      message: "Spam detected: {subject}"
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from mailguardian.config import CONFIG_DIR


PLAYBOOKS_DIR = CONFIG_DIR / "playbooks"


@dataclass
class PlaybookAction:
    """An action to execute when a playbook matches."""

    type: str  # "log", "flag", "notify", "move"
    params: dict[str, Any] = field(default_factory=dict)


@dataclass
class Playbook:
    """A rule for automated mail handling."""

    name: str
    description: str
    match: dict[str, Any]
    action: PlaybookAction

    def matches(self, classification: dict) -> bool:
        """Check if a mail classification matches this playbook's criteria."""
        for key, value in self.match.items():
            if classification.get(key) != value:
                return False
        return True


def load_playbooks() -> list[Playbook]:
    """Load all playbooks from the playbooks directory."""
    if not PLAYBOOKS_DIR.exists():
        return []

    playbooks = []
    for f in sorted(PLAYBOOKS_DIR.glob("*.yaml")):
        data = yaml.safe_load(f.read_text())
        if not data:
            continue
        action_data = data.get("action", {})
        action = PlaybookAction(
            type=action_data.get("type", "log"),
            params={k: v for k, v in action_data.items() if k != "type"},
        )
        playbooks.append(Playbook(
            name=data.get("name", f.stem),
            description=data.get("description", ""),
            match=data.get("match", {}),
            action=action,
        ))

    return playbooks


def create_default_playbooks() -> None:
    """Create example playbooks if none exist."""
    PLAYBOOKS_DIR.mkdir(parents=True, exist_ok=True)

    example = PLAYBOOKS_DIR / "example-spam-filter.yaml"
    if not example.exists():
        example.write_text(yaml.dump({
            "name": "spam-filter",
            "description": "Log detected spam mails",
            "match": {"category": "spam"},
            "action": {"type": "log", "message": "Spam detected: {subject}"},
        }, default_flow_style=False))

    example2 = PLAYBOOKS_DIR / "example-meeting-alert.yaml"
    if not example2.exists():
        example2.write_text(yaml.dump({
            "name": "meeting-alert",
            "description": "Flag meeting requests as action required",
            "match": {"category": "meeting"},
            "action": {"type": "flag", "message": "Meeting request: {subject}"},
        }, default_flow_style=False))
