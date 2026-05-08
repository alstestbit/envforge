"""Pin current env values to a schema, locking defaults to live values."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.schema import Schema


@dataclass
class PinEntry:
    key: str
    old_default: Optional[str]
    new_default: str
    changed: bool

    def __str__(self) -> str:
        if self.changed:
            return f"  ~ {self.key}: {self.old_default!r} -> {self.new_default!r}"
        return f"  = {self.key}: {self.new_default!r} (unchanged)"


@dataclass
class PinResult:
    entries: List[PinEntry] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.changed for e in self.entries)

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.changed]

    def summary(self) -> str:
        changed = len(self.changed_keys)
        total = len(self.entries)
        skipped = len(self.skipped)
        parts = [f"{changed}/{total} defaults updated"]
        if skipped:
            parts.append(f"{skipped} keys skipped (not in schema)")
        return ", ".join(parts)


def pin_env(schema: Schema, env: Dict[str, str]) -> PinResult:
    """Pin env values as defaults into the schema variables."""
    result = PinResult()

    schema_keys = {var.name for var in schema.variables}

    for key, value in env.items():
        if key not in schema_keys:
            result.skipped.append(key)
            continue

        var = next(v for v in schema.variables if v.name == key)
        old_default = var.default
        changed = old_default != value
        var.default = value
        result.entries.append(PinEntry(
            key=key,
            old_default=old_default,
            new_default=value,
            changed=changed,
        ))

    return result
