"""Schema definition and parsing for .env file validation."""

from dataclasses import dataclass, field
from typing import Any, Optional
import json
import re


VALID_TYPES = {"string", "integer", "boolean", "float"}


@dataclass
class EnvVar:
    """Represents a single environment variable definition in a schema."""

    name: str
    type: str = "string"
    required: bool = True
    default: Optional[Any] = None
    description: str = ""
    pattern: Optional[str] = None
    allowed_values: list = field(default_factory=list)

    def __post_init__(self):
        if self.type not in VALID_TYPES:
            raise ValueError(f"Invalid type '{self.type}' for '{self.name}'. Must be one of {VALID_TYPES}.")
        if self.pattern:
            try:
                re.compile(self.pattern)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern for '{self.name}': {e}")


@dataclass
class Schema:
    """Represents a complete .env schema."""

    name: str
    version: str = "1.0"
    variables: list[EnvVar] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Schema":
        """Parse a schema from a dictionary (e.g., loaded from JSON)."""
        variables = [
            EnvVar(
                name=var["name"],
                type=var.get("type", "string"),
                required=var.get("required", True),
                default=var.get("default"),
                description=var.get("description", ""),
                pattern=var.get("pattern"),
                allowed_values=var.get("allowed_values", []),
            )
            for var in data.get("variables", [])
        ]
        return cls(
            name=data["name"],
            version=data.get("version", "1.0"),
            variables=variables,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "Schema":
        """Parse a schema from a JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, path: str) -> "Schema":
        """Load and parse a schema from a JSON file."""
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def to_dict(self) -> dict:
        """Serialize the schema to a dictionary."""
        return {
            "name": self.name,
            "version": self.version,
            "variables": [
                {
                    "name": v.name,
                    "type": v.type,
                    "required": v.required,
                    "default": v.default,
                    "description": v.description,
                    "pattern": v.pattern,
                    "allowed_values": v.allowed_values,
                }
                for v in self.variables
            ],
        }
