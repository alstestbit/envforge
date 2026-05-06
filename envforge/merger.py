"""Merge multiple .env files or override values from a base environment."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class MergeResult:
    """Result of merging two or more env mappings."""

    merged: Dict[str, str] = field(default_factory=dict)
    overrides: Dict[str, str] = field(default_factory=dict)  # key -> new value
    added: List[str] = field(default_factory=list)           # keys new in overlay
    removed: List[str] = field(default_factory=list)         # keys only in base

    @property
    def has_changes(self) -> bool:
        return bool(self.overrides or self.added or self.removed)

    def summary(self) -> str:
        lines = []
        if self.added:
            lines.append(f"Added   ({len(self.added)}): {', '.join(sorted(self.added))}")
        if self.overrides:
            lines.append(f"Changed ({len(self.overrides)}): {', '.join(sorted(self.overrides))}")
        if self.removed:
            lines.append(f"Removed ({len(self.removed)}): {', '.join(sorted(self.removed))}")
        return "\n".join(lines) if lines else "No changes."


def merge_envs(
    base: Dict[str, str],
    overlay: Dict[str, str],
    *,
    remove_missing: bool = False,
) -> MergeResult:
    """Merge *overlay* on top of *base*.

    Args:
        base: The starting environment mapping.
        overlay: Values to apply on top of base.
        remove_missing: If True, keys present in base but absent from overlay
            are removed from the result.

    Returns:
        A :class:`MergeResult` describing what changed.
    """
    result = MergeResult()
    merged: Dict[str, str] = {}

    for key, value in base.items():
        if key in overlay:
            new_value = overlay[key]
            merged[key] = new_value
            if new_value != value:
                result.overrides[key] = new_value
        elif not remove_missing:
            merged[key] = value
        else:
            result.removed.append(key)

    for key, value in overlay.items():
        if key not in base:
            merged[key] = value
            result.added.append(key)

    result.merged = merged
    return result


def merge_many(
    envs: List[Dict[str, str]],
    *,
    remove_missing: bool = False,
) -> MergeResult:
    """Sequentially merge a list of env dicts, left-to-right."""
    if not envs:
        return MergeResult()
    accumulated = envs[0].copy()
    final_result = MergeResult(merged=accumulated)
    for overlay in envs[1:]:
        result = merge_envs(accumulated, overlay, remove_missing=remove_missing)
        accumulated = result.merged
        final_result.overrides.update(result.overrides)
        final_result.added.extend(result.added)
        final_result.removed.extend(result.removed)
    final_result.merged = accumulated
    return final_result
