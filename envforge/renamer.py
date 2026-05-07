"""Rename keys in an env mapping according to a rename map."""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class RenameEntry:
    old_key: str
    new_key: str
    value: str

    def __str__(self) -> str:
        return f"{self.old_key} -> {self.new_key}={self.value!r}"


@dataclass
class RenameResult:
    env: Dict[str, str]
    renamed: List[RenameEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return len(self.renamed) > 0

    def summary(self) -> str:
        parts = [f"{len(self.renamed)} renamed"]
        if self.skipped:
            parts.append(f"{len(self.skipped)} skipped (not found)")
        if self.errors:
            parts.append(f"{len(self.errors)} errors")
        return ", ".join(parts)


def rename_env(
    env: Dict[str, str],
    rename_map: Dict[str, str],
    *,
    overwrite: bool = False,
) -> RenameResult:
    """Rename keys in *env* according to *rename_map* ({old: new}).

    If *overwrite* is False (default) and the new key already exists,
    the rename is skipped and an error is recorded.
    """
    result_env: Dict[str, str] = dict(env)
    renamed: List[RenameEntry] = []
    skipped: List[str] = []
    errors: List[str] = []

    for old_key, new_key in rename_map.items():
        if old_key not in result_env:
            skipped.append(old_key)
            continue
        if new_key in result_env and not overwrite:
            errors.append(
                f"Cannot rename '{old_key}' to '{new_key}': target key already exists"
            )
            continue
        value = result_env.pop(old_key)
        result_env[new_key] = value
        renamed.append(RenameEntry(old_key=old_key, new_key=new_key, value=value))

    return RenameResult(env=result_env, renamed=renamed, skipped=skipped, errors=errors)
