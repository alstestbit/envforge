"""Trimmer: strip leading/trailing whitespace from env values."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TrimEntry:
    key: str
    original: str
    trimmed: str

    def __str__(self) -> str:
        return f"{self.key}: {self.original!r} -> {self.trimmed!r}"


@dataclass
class TrimResult:
    env: Dict[str, str]
    changes: List[TrimEntry] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.changes) > 0

    def summary(self) -> str:
        if not self.has_changes():
            return "No values were trimmed."
        lines = [f"Trimmed {len(self.changes)} value(s):"]
        for entry in self.changes:
            lines.append(f"  {entry}")
        return "\n".join(lines)


def trim_env(
    env: Dict[str, str],
    trim_keys: bool = False,
) -> TrimResult:
    """Return a new env dict with whitespace stripped from values.

    Args:
        env: The source environment dictionary.
        trim_keys: If True, also strip whitespace from keys.

    Returns:
        A TrimResult containing the cleaned env and a list of changes.
    """
    result_env: Dict[str, str] = {}
    changes: List[TrimEntry] = []

    for raw_key, raw_value in env.items():
        key = raw_key.strip() if trim_keys else raw_key
        trimmed_value = raw_value.strip()

        if raw_value != trimmed_value or raw_key != key:
            changes.append(TrimEntry(key=key, original=raw_value, trimmed=trimmed_value))

        result_env[key] = trimmed_value

    return TrimResult(env=result_env, changes=changes)
