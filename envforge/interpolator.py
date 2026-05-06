"""Interpolator: resolves variable references within .env values.

Supports ${VAR} and $VAR syntax for referencing other keys in the same env dict.
Circular references are detected and raise a ValueError.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Optional

_REF_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolationResult:
    resolved: Dict[str, str] = field(default_factory=dict)
    unresolved: Dict[str, str] = field(default_factory=dict)

    @property
    def has_unresolved(self) -> bool:
        return bool(self.unresolved)

    def summary(self) -> str:
        lines = [f"Resolved: {len(self.resolved)} variable(s)"]
        if self.unresolved:
            keys = ", ".join(self.unresolved.keys())
            lines.append(f"Unresolved references in: {keys}")
        return "\n".join(lines)


def _resolve_value(
    key: str,
    env: Dict[str, str],
    cache: Dict[str, str],
    visiting: set,
) -> Optional[str]:
    if key in cache:
        return cache[key]
    if key not in env:
        return None
    if key in visiting:
        raise ValueError(f"Circular reference detected for variable: '{key}'")

    visiting.add(key)
    raw = env[key]

    def replacer(match: re.Match) -> str:
        ref_key = match.group(1) or match.group(2)
        resolved = _resolve_value(ref_key, env, cache, visiting)
        if resolved is None:
            return match.group(0)  # leave unresolved reference as-is
        return resolved

    result = _REF_PATTERN.sub(replacer, raw)
    visiting.discard(key)
    cache[key] = result
    return result


def interpolate_env(env: Dict[str, str]) -> InterpolationResult:
    """Resolve all variable references in *env* and return an InterpolationResult."""
    cache: Dict[str, str] = {}
    result = InterpolationResult()

    for key in env:
        try:
            resolved = _resolve_value(key, env, cache, set())
        except ValueError:
            result.unresolved[key] = env[key]
            continue

        if resolved is None:
            result.unresolved[key] = env[key]
        else:
            # Check whether any reference remained unresolved (still contains $ syntax)
            if _REF_PATTERN.search(resolved):
                result.unresolved[key] = resolved
            else:
                result.resolved[key] = resolved

    return result
