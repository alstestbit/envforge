"""Transform env variable values using schema-defined rules."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envforge.schema import Schema


@dataclass
class TransformResult:
    original: Dict[str, str]
    transformed: Dict[str, str] = field(default_factory=dict)
    changes: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def summary(self) -> str:
        lines = [f"Transformed {len(self.changes)} value(s)."]
        for c in self.changes:
            lines.append(f"  ~ {c}")
        if self.errors:
            lines.append(f"{len(self.errors)} error(s):")
            for e in self.errors:
                lines.append(f"  ! {e}")
        return "\n".join(lines)


def _apply_transform(key: str, value: str, transform: str) -> Optional[str]:
    """Apply a named transform to a value."""
    if transform == "uppercase":
        return value.upper()
    elif transform == "lowercase":
        return value.lower()
    elif transform == "strip":
        return value.strip()
    elif transform == "trim_quotes":
        return value.strip("'\"")
    elif transform == "boolean_normalize":
        if value.lower() in ("1", "yes", "true", "on"):
            return "true"
        elif value.lower() in ("0", "no", "false", "off"):
            return "false"
        return value
    return None


def transform_env(env: Dict[str, str], schema: Optional[Schema] = None) -> TransformResult:
    """Apply schema-defined transforms to env values."""
    result = TransformResult(original=dict(env), transformed=dict(env))

    if schema is None:
        return result

    for key, var in schema.vars.items():
        transform = var.metadata.get("transform") if var.metadata else None
        if not transform:
            continue
        if key not in result.transformed:
            continue
        original_val = result.transformed[key]
        new_val = _apply_transform(key, original_val, transform)
        if new_val is None:
            result.errors.append(f"{key}: unknown transform '{transform}'")
        elif new_val != original_val:
            result.transformed[key] = new_val
            result.changes.append(f"{key}: '{original_val}' -> '{new_val}'")

    return result
