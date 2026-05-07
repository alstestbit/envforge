"""Patch (add/update/remove) keys in an env dictionary."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class PatchEntry:
    key: str
    operation: str  # 'set', 'delete', 'rename'
    old_value: Optional[str] = None
    new_value: Optional[str] = None

    def __str__(self) -> str:
        if self.operation == "set":
            if self.old_value is None:
                return f"[ADD] {self.key}={self.new_value}"
            return f"[UPDATE] {self.key}: {self.old_value!r} -> {self.new_value!r}"
        if self.operation == "delete":
            return f"[DELETE] {self.key}"
        return f"[{self.operation.upper()}] {self.key}"


@dataclass
class PatchResult:
    env: Dict[str, str]
    changes: List[PatchEntry] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes applied."
        lines = [str(c) for c in self.changes]
        if self.errors:
            lines += [f"[ERROR] {e}" for e in self.errors]
        return "\n".join(lines)


def patch_env(
    env: Dict[str, str],
    set_pairs: Optional[List[Tuple[str, str]]] = None,
    delete_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Apply set and delete patches to an env dict.

    Args:
        env: Original environment dictionary.
        set_pairs: List of (key, value) tuples to add or update.
        delete_keys: List of keys to remove.

    Returns:
        PatchResult with updated env and recorded changes.
    """
    result_env = dict(env)
    changes: List[PatchEntry] = []
    errors: List[str] = []

    for key, value in (set_pairs or []):
        if not key:
            errors.append("Empty key is not allowed.")
            continue
        old = result_env.get(key)
        result_env[key] = value
        changes.append(PatchEntry(key=key, operation="set", old_value=old, new_value=value))

    for key in (delete_keys or []):
        if key not in result_env:
            errors.append(f"Key not found for deletion: {key}")
            continue
        old = result_env.pop(key)
        changes.append(PatchEntry(key=key, operation="delete", old_value=old))

    return PatchResult(env=result_env, changes=changes, errors=errors)
