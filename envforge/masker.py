from dataclasses import dataclass, field
from typing import Dict, List, Optional


DEFAULT_MASK = "********"


@dataclass
class MaskEntry:
    key: str
    original: str
    masked: str
    was_masked: bool

    def __str__(self) -> str:
        status = "masked" if self.was_masked else "unchanged"
        return f"{self.key}: {status}"


@dataclass
class MaskResult:
    entries: List[MaskEntry] = field(default_factory=list)
    env: Dict[str, str] = field(default_factory=dict)

    def has_masked(self) -> bool:
        return any(e.was_masked for e in self.entries)

    def masked_keys(self) -> List[str]:
        return [e.key for e in self.entries if e.was_masked]

    def summary(self) -> str:
        total = len(self.entries)
        masked = len(self.masked_keys())
        return f"{masked}/{total} keys masked"


def mask_env(
    env: Dict[str, str],
    keys: List[str],
    mask: Optional[str] = None,
    partial: bool = False,
    reveal_chars: int = 2,
) -> MaskResult:
    """
    Mask specific keys in an env dict.

    Args:
        env: The environment dictionary.
        keys: List of keys to mask.
        mask: The mask string to use (default: DEFAULT_MASK).
        partial: If True, reveal the last `reveal_chars` characters.
        reveal_chars: Number of trailing characters to reveal when partial=True.
    """
    mask_str = mask if mask is not None else DEFAULT_MASK
    result_env: Dict[str, str] = {}
    entries: List[MaskEntry] = []

    for key, value in env.items():
        if key in keys:
            if partial and len(value) > reveal_chars:
                suffix = value[-reveal_chars:]
                masked_value = mask_str + suffix
            else:
                masked_value = mask_str
            result_env[key] = masked_value
            entries.append(MaskEntry(key=key, original=value, masked=masked_value, was_masked=True))
        else:
            result_env[key] = value
            entries.append(MaskEntry(key=key, original=value, masked=value, was_masked=False))

    return MaskResult(entries=entries, env=result_env)
