"""Validates .env file contents against a Schema definition."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional

from envforge.schema import Schema


@dataclass
class ValidationError:
    key: str
    message: str

    def __str__(self) -> str:
        return f"[{self.key}] {self.message}"


@dataclass
class ValidationResult:
    errors: List[ValidationError] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, key: str, message: str) -> None:
        self.errors.append(ValidationError(key=key, message=message))

    def __str__(self) -> str:
        if self.is_valid:
            return "Validation passed."
        lines = ["Validation failed with errors:"]
        lines.extend(f"  - {e}" for e in self.errors)
        return "\n".join(lines)


class Validator:
    """Validates a parsed env mapping against a Schema."""

    def __init__(self, schema: Schema) -> None:
        self.schema = schema

    def validate(self, env: dict[str, str]) -> ValidationResult:
        result = ValidationResult()

        for var in self.schema.vars:
            value: Optional[str] = env.get(var.name)

            if value is None or value == "":
                if var.required:
                    result.add_error(var.name, "required variable is missing or empty")
                continue

            if var.type == "int":
                try:
                    int(value)
                except ValueError:
                    result.add_error(var.name, f"expected int, got {value!r}")

            elif var.type == "bool":
                if value.lower() not in ("true", "false", "1", "0"):
                    result.add_error(var.name, f"expected bool, got {value!r}")

            if var.pattern and not re.fullmatch(var.pattern, value):
                result.add_error(
                    var.name,
                    f"value {value!r} does not match pattern {var.pattern!r}",
                )

        return result
