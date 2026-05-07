"""Detect and report duplicate keys in .env content."""
from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DuplicateEntry:
    key: str
    occurrences: int
    values: List[str]

    def __str__(self) -> str:
        return f"{self.key}: {self.occurrences} occurrences ({', '.join(repr(v) for v in self.values)})"


@dataclass
class DuplicateReport:
    duplicates: List[DuplicateEntry] = field(default_factory=list)

    @property
    def has_duplicates(self) -> bool:
        return len(self.duplicates) > 0

    @property
    def duplicate_keys(self) -> List[str]:
        return [e.key for e in self.duplicates]

    def summary(self) -> str:
        if not self.has_duplicates:
            return "No duplicate keys found."
        lines = [f"Found {len(self.duplicates)} duplicate key(s):"]
        for entry in self.duplicates:
            lines.append(f"  - {entry}")
        return "\n".join(lines)


def find_duplicates(env_string: str) -> DuplicateReport:
    """Scan raw .env string content for duplicate key definitions."""
    occurrences: Dict[str, List[str]] = {}

    for line in env_string.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "=" not in stripped:
            continue
        key, _, value = stripped.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        occurrences.setdefault(key, []).append(value)

    entries = [
        DuplicateEntry(key=k, occurrences=len(vals), values=vals)
        for k, vals in occurrences.items()
        if len(vals) > 1
    ]
    return DuplicateReport(duplicates=entries)
