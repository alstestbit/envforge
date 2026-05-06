"""Compare two .env files and report differences in values, keys, and types."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class CompareEntry:
    key: str
    left_value: Optional[str]
    right_value: Optional[str]
    status: str  # 'changed', 'left_only', 'right_only'

    def __str__(self) -> str:
        if self.status == "changed":
            return f"~ {self.key}: {self.left_value!r} -> {self.right_value!r}"
        elif self.status == "left_only":
            return f"- {self.key}: {self.left_value!r}"
        elif self.status == "right_only":
            return f"+ {self.key}: {self.right_value!r}"
        return f"  {self.key}"


@dataclass
class CompareResult:
    left_label: str
    right_label: str
    entries: List[CompareEntry] = field(default_factory=list)

    @property
    def has_differences(self) -> bool:
        return len(self.entries) > 0

    @property
    def changed(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "changed"]

    @property
    def left_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "left_only"]

    @property
    def right_only(self) -> List[CompareEntry]:
        return [e for e in self.entries if e.status == "right_only"]

    def summary(self) -> str:
        if not self.has_differences:
            return f"No differences between '{self.left_label}' and '{self.right_label}'."
        lines = [
            f"Comparing '{self.left_label}' vs '{self.right_label}':",
            f"  Changed:    {len(self.changed)}",
            f"  Left only:  {len(self.left_only)}",
            f"  Right only: {len(self.right_only)}",
        ]
        return "\n".join(lines)


def compare_envs(
    left: Dict[str, str],
    right: Dict[str, str],
    left_label: str = "left",
    right_label: str = "right",
) -> CompareResult:
    """Compare two env dicts and return a CompareResult detailing all differences."""
    result = CompareResult(left_label=left_label, right_label=right_label)
    all_keys = sorted(set(left) | set(right))

    for key in all_keys:
        in_left = key in left
        in_right = key in right

        if in_left and in_right:
            if left[key] != right[key]:
                result.entries.append(
                    CompareEntry(
                        key=key,
                        left_value=left[key],
                        right_value=right[key],
                        status="changed",
                    )
                )
        elif in_left:
            result.entries.append(
                CompareEntry(key=key, left_value=left[key], right_value=None, status="left_only")
            )
        else:
            result.entries.append(
                CompareEntry(key=key, left_value=None, right_value=right[key], status="right_only")
            )

    return result
