from dataclasses import dataclass, field
from typing import Dict, List, Optional
import re


@dataclass
class FilterResult:
    original: Dict[str, str]
    filtered: Dict[str, str]
    excluded: List[str] = field(default_factory=list)

    def has_exclusions(self) -> bool:
        return len(self.excluded) > 0

    def summary(self) -> str:
        if not self.has_exclusions():
            return "No keys excluded."
        keys = ", ".join(self.excluded)
        return f"Excluded {len(self.excluded)} key(s): {keys}"


def filter_env(
    env: Dict[str, str],
    keys: Optional[List[str]] = None,
    pattern: Optional[str] = None,
    prefix: Optional[str] = None,
    invert: bool = False,
) -> FilterResult:
    """
    Filter an env dict by explicit key list, regex pattern, or prefix.
    If invert=True, the matched keys are excluded instead of kept.
    """
    if not keys and not pattern and not prefix:
        return FilterResult(original=env, filtered=dict(env), excluded=[])

    compiled = re.compile(pattern) if pattern else None

    def matches(key: str) -> bool:
        if keys and key in keys:
            return True
        if compiled and compiled.search(key):
            return True
        if prefix and key.startswith(prefix):
            return True
        return False

    filtered: Dict[str, str] = {}
    excluded: List[str] = []

    for key, value in env.items():
        keep = matches(key)
        if invert:
            keep = not keep
        if keep:
            filtered[key] = value
        else:
            excluded.append(key)

    return FilterResult(original=env, filtered=filtered, excluded=excluded)
