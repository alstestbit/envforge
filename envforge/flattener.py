"""Flattener: collapse nested prefix groups in an env dict into dot-notation keys."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class FlattenEntry:
    original_key: str
    flat_key: str
    value: str

    def __str__(self) -> str:
        if self.original_key == self.flat_key:
            return f"{self.flat_key}={self.value} (unchanged)"
        return f"{self.original_key} -> {self.flat_key}={self.value}"


@dataclass
class FlattenResult:
    entries: List[FlattenEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def has_changes(self) -> bool:
        return any(e.original_key != e.flat_key for e in self.entries)

    def changed_keys(self) -> List[str]:
        return [e.original_key for e in self.entries if e.original_key != e.flat_key]

    def summary(self) -> str:
        changed = self.changed_keys()
        if not changed:
            return "No keys were flattened."
        return f"{len(changed)} key(s) flattened: {', '.join(changed)}"


def flatten_env(
    env: Dict[str, str],
    separator: str = "__",
    replacement: str = ".",
    prefix_filter: Optional[str] = None,
) -> FlattenResult:
    """Replace `separator` occurrences in keys with `replacement`.

    Args:
        env: Source environment dictionary.
        separator: The substring in keys to replace (default ``"__"``).
        replacement: The string to substitute in place of the separator (default ``"."``).
        prefix_filter: If provided, only keys starting with this prefix are processed.

    Returns:
        A :class:`FlattenResult` with the transformed env and change log.
    """
    entries: List[FlattenEntry] = []
    result_env: Dict[str, str] = {}

    for key, value in env.items():
        if separator in key and (prefix_filter is None or key.startswith(prefix_filter)):
            flat_key = key.replace(separator, replacement)
        else:
            flat_key = key
        entries.append(FlattenEntry(original_key=key, flat_key=flat_key, value=value))
        result_env[flat_key] = value

    return FlattenResult(entries=entries, env=result_env)
