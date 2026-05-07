"""Sort .env key-value pairs by key name or definition order in schema."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envforge.schema import Schema


@dataclass
class SortResult:
    original: Dict[str, str]
    sorted_env: Dict[str, str]
    order: str  # 'alpha' | 'schema' | 'alpha_desc'
    keys_reordered: List[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return list(self.original.keys()) != list(self.sorted_env.keys())

    def summary(self) -> str:
        if not self.has_changes:
            return f"Keys already in {self.order!r} order — no changes."
        return (
            f"Sorted {len(self.keys_reordered)} key(s) using {self.order!r} order."
        )


def sort_env(
    env: Dict[str, str],
    order: str = "alpha",
    schema: Optional[Schema] = None,
) -> SortResult:
    """Return a SortResult with keys reordered according to *order*.

    Supported orders:
      - ``'alpha'``       — A-Z (case-insensitive)
      - ``'alpha_desc'``  — Z-A (case-insensitive)
      - ``'schema'``      — follow the variable order defined in *schema*;
                            keys absent from the schema are appended alphabetically.
    """
    if order == "alpha":
        sorted_keys = sorted(env.keys(), key=str.casefold)
    elif order == "alpha_desc":
        sorted_keys = sorted(env.keys(), key=str.casefold, reverse=True)
    elif order == "schema":
        if schema is None:
            raise ValueError("A Schema instance is required for 'schema' order.")
        schema_keys = list(schema.variables.keys())
        in_schema = [k for k in schema_keys if k in env]
        out_of_schema = sorted(
            (k for k in env if k not in schema.variables), key=str.casefold
        )
        sorted_keys = in_schema + out_of_schema
    else:
        raise ValueError(
            f"Unknown sort order {order!r}. Choose 'alpha', 'alpha_desc', or 'schema'."
        )

    sorted_env = {k: env[k] for k in sorted_keys}
    original_keys = list(env.keys())
    reordered = [k for i, k in enumerate(sorted_keys) if sorted_keys[i] != original_keys[i] if i < len(original_keys)]

    return SortResult(
        original=dict(env),
        sorted_env=sorted_env,
        order=order,
        keys_reordered=reordered,
    )
