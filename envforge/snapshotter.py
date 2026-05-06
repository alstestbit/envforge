"""Snapshot and compare .env states over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Optional


@dataclass
class SnapshotEntry:
    key: str
    value: str

    def __str__(self) -> str:
        return f"{self.key}={self.value}"


@dataclass
class Snapshot:
    label: str
    timestamp: str
    entries: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "timestamp": self.timestamp,
            "entries": self.entries,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Snapshot":
        return cls(
            label=data["label"],
            timestamp=data["timestamp"],
            entries=data.get("entries", {}),
        )


@dataclass
class SnapshotDiff:
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(self.added or self.removed or self.changed)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"{len(self.added)} added")
        if self.removed:
            parts.append(f"{len(self.removed)} removed")
        if self.changed:
            parts.append(f"{len(self.changed)} changed")
        return ", ".join(parts) if parts else "no differences"


def take_snapshot(env: Dict[str, str], label: str) -> Snapshot:
    """Create a snapshot from an env dict."""
    timestamp = datetime.now(timezone.utc).isoformat()
    return Snapshot(label=label, timestamp=timestamp, entries=dict(env))


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    """Persist a snapshot to a JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot.to_dict(), f, indent=2)


def load_snapshot(path: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return Snapshot.from_dict(data)


def diff_snapshots(before: Snapshot, after: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return a SnapshotDiff."""
    result = SnapshotDiff()
    before_keys = set(before.entries)
    after_keys = set(after.entries)

    for key in after_keys - before_keys:
        result.added[key] = after.entries[key]

    for key in before_keys - after_keys:
        result.removed[key] = before.entries[key]

    for key in before_keys & after_keys:
        if before.entries[key] != after.entries[key]:
            result.changed[key] = (before.entries[key], after.entries[key])

    return result
