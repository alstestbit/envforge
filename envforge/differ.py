"""Diff utility for comparing .env files against a schema or another .env."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envforge.schema import Schema


@dataclass
class DiffEntry:
    key: str
    status: str  # 'missing', 'extra', 'type_mismatch', 'default_changed'
    expected: Optional[str] = None
    actual: Optional[str] = None

    def __str__(self) -> str:
        if self.status == "missing":
            return f"  - {self.key}: missing from env (expected type: {self.expected})"
        if self.status == "extra":
            return f"  + {self.key}: extra key not in schema"
        if self.status == "type_mismatch":
            return f"  ~ {self.key}: type mismatch (expected {self.expected}, got {self.actual})"
        if self.status == "default_changed":
            return f"  ~ {self.key}: default changed (schema={self.expected}, env={self.actual})"
        return f"  ? {self.key}: unknown diff"


@dataclass
class DiffResult:
    entries: List[DiffEntry] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return len(self.entries) > 0

    def summary(self) -> str:
        if not self.has_differences:
            return "No differences found."
        lines = [f"{len(self.entries)} difference(s) found:"]
        lines.extend(str(e) for e in self.entries)
        return "\n".join(lines)


def diff_env_against_schema(env: Dict[str, str], schema: Schema) -> DiffResult:
    """Compare a parsed env dict against a schema definition."""
    result = DiffResult()
    schema_keys = {var.name: var for var in schema.variables}

    for key, var in schema_keys.items():
        if key not in env:
            result.entries.append(DiffEntry(key=key, status="missing", expected=var.type))
        else:
            value = env[key]
            if var.type == "int":
                try:
                    int(value)
                except ValueError:
                    result.entries.append(
                        DiffEntry(key=key, status="type_mismatch", expected="int", actual=value)
                    )
            elif var.type == "bool":
                if value.lower() not in ("true", "false", "1", "0"):
                    result.entries.append(
                        DiffEntry(key=key, status="type_mismatch", expected="bool", actual=value)
                    )

    env_keys = set(env.keys())
    for key in env_keys - set(schema_keys.keys()):
        result.entries.append(DiffEntry(key=key, status="extra"))

    return result


def diff_two_envs(base: Dict[str, str], other: Dict[str, str]) -> DiffResult:
    """Compare two parsed env dicts and report differences."""
    result = DiffResult()
    all_keys = set(base.keys()) | set(other.keys())
    for key in sorted(all_keys):
        if key not in base:
            result.entries.append(DiffEntry(key=key, status="missing", expected=None, actual=other[key]))
        elif key not in other:
            result.entries.append(DiffEntry(key=key, status="extra", expected=base[key], actual=None))
        elif base[key] != other[key]:
            result.entries.append(
                DiffEntry(key=key, status="default_changed", expected=base[key], actual=other[key])
            )
    return result
