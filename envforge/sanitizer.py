from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class SanitizeEntry:
    key: str
    original: str
    sanitized: str
    reason: str

    def __str__(self) -> str:
        return f"{self.key}: {self.original!r} -> {self.sanitized!r} ({self.reason})"


@dataclass
class SanitizeResult:
    env: Dict[str, str]
    changes: List[SanitizeEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def changed_keys(self) -> List[str]:
        return [e.key for e in self.changes]

    def summary(self) -> str:
        if not self.has_changes:
            return "No sanitization changes applied."
        lines = [f"{len(self.changes)} key(s) sanitized:"]
        for entry in self.changes:
            lines.append(f"  {entry}")
        return "\n".join(lines)


def sanitize_env(
    env: Dict[str, str],
    strip_quotes: bool = True,
    strip_whitespace: bool = True,
    remove_control_chars: bool = True,
    normalize_newlines: bool = True,
) -> SanitizeResult:
    """Apply sanitization rules to env values and return a SanitizeResult."""
    result_env: Dict[str, str] = {}
    changes: List[SanitizeEntry] = []

    for key, value in env.items():
        original = value
        current = value

        if strip_whitespace:
            stripped = current.strip()
            if stripped != current:
                current = stripped

        if strip_quotes:
            for quote in ('"', "'"):
                if current.startswith(quote) and current.endswith(quote) and len(current) >= 2:
                    current = current[1:-1]
                    break

        if normalize_newlines:
            normalized = current.replace("\r\n", "\n").replace("\r", "\n")
            current = normalized

        if remove_control_chars:
            cleaned = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", current)
            current = cleaned

        result_env[key] = current

        if current != original:
            reasons = []
            if strip_whitespace and original.strip() != original:
                reasons.append("stripped whitespace")
            if strip_quotes and (original.startswith('"') or original.startswith("'")):
                reasons.append("removed quotes")
            if normalize_newlines and ("\r" in original):
                reasons.append("normalized newlines")
            if remove_control_chars and re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", original):
                reasons.append("removed control chars")
            reason = ", ".join(reasons) if reasons else "sanitized"
            changes.append(SanitizeEntry(key=key, original=original, sanitized=current, reason=reason))

    return SanitizeResult(env=result_env, changes=changes)
