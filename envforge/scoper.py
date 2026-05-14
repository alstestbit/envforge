"""Scoper: filter and extract env vars by scope prefix (e.g. APP_, DB_)."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ScopeEntry:
    key: str
    scoped_key: str
    value: str

    def __str__(self) -> str:
        return f"{self.key} -> {self.scoped_key}={self.value}"


@dataclass
class ScopeResult:
    scope: str
    entries: List[ScopeEntry] = field(default_factory=list)
    excluded: List[str] = field(default_factory=list)

    @property
    def has_matches(self) -> bool:
        return len(self.entries) > 0

    @property
    def scoped_env(self) -> Dict[str, str]:
        """Return env dict with prefix stripped from keys."""
        return {e.scoped_key: e.value for e in self.entries}

    @property
    def original_env(self) -> Dict[str, str]:
        """Return env dict with original keys."""
        return {e.key: e.value for e in self.entries}

    def summary(self) -> str:
        return (
            f"Scope '{self.scope}': {len(self.entries)} matched, "
            f"{len(self.excluded)} excluded."
        )


def scope_env(
    env: Dict[str, str],
    prefix: str,
    strip_prefix: bool = True,
    case_sensitive: bool = True,
) -> ScopeResult:
    """Extract env vars matching a given prefix scope.

    Args:
        env: The environment dictionary to scope.
        prefix: The prefix to match (e.g. 'APP_').
        strip_prefix: If True, remove the prefix from matched keys.
        case_sensitive: If False, match prefix case-insensitively.
    """
    result = ScopeResult(scope=prefix)
    norm_prefix = prefix if case_sensitive else prefix.upper()

    for key, value in env.items():
        compare_key = key if case_sensitive else key.upper()
        if compare_key.startswith(norm_prefix):
            scoped_key = key[len(prefix):] if strip_prefix else key
            result.entries.append(ScopeEntry(key=key, scoped_key=scoped_key, value=value))
        else:
            result.excluded.append(key)

    return result
