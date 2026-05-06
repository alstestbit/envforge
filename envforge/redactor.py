"""Redactor module for masking sensitive values in .env data."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.schema import Schema

DEFAULT_SENSITIVE_PATTERNS = [
    "SECRET",
    "PASSWORD",
    "PASSWD",
    "TOKEN",
    "API_KEY",
    "PRIVATE_KEY",
    "CREDENTIALS",
    "AUTH",
]

DEFAULT_MASK = "***REDACTED***"


@dataclass
class RedactResult:
    original: Dict[str, str]
    redacted: Dict[str, str]
    redacted_keys: List[str] = field(default_factory=list)

    @property
    def has_redactions(self) -> bool:
        return len(self.redacted_keys) > 0

    def summary(self) -> str:
        if not self.has_redactions:
            return "No sensitive keys redacted."
        keys = ", ".join(self.redacted_keys)
        return f"Redacted {len(self.redacted_keys)} sensitive key(s): {keys}"


def _is_sensitive(
    key: str,
    schema: Optional[Schema],
    extra_patterns: Optional[List[str]],
) -> bool:
    """Return True if a key should be treated as sensitive."""
    if schema is not None:
        var = schema.vars.get(key)
        if var is not None and getattr(var, "sensitive", False):
            return True

    patterns = list(DEFAULT_SENSITIVE_PATTERNS)
    if extra_patterns:
        patterns.extend(p.upper() for p in extra_patterns)

    upper_key = key.upper()
    return any(pat in upper_key for pat in patterns)


def redact_env(
    env: Dict[str, str],
    schema: Optional[Schema] = None,
    extra_patterns: Optional[List[str]] = None,
    mask: str = DEFAULT_MASK,
) -> RedactResult:
    """Return a RedactResult with sensitive values masked."""
    redacted: Dict[str, str] = {}
    redacted_keys: List[str] = []

    for key, value in env.items():
        if _is_sensitive(key, schema, extra_patterns):
            redacted[key] = mask
            redacted_keys.append(key)
        else:
            redacted[key] = value

    return RedactResult(
        original=dict(env),
        redacted=redacted,
        redacted_keys=sorted(redacted_keys),
    )
