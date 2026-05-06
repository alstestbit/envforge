"""Profile env files against named environments (e.g. dev, staging, prod)."""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from envforge.schema import Schema
from envforge.validator import ValidationResult, Validator


@dataclass
class ProfileEntry:
    environment: str
    env: Dict[str, str]
    result: ValidationResult

    def __str__(self) -> str:
        status = "PASS" if self.result.is_valid else "FAIL"
        return f"[{status}] {self.environment}: {len(self.env)} vars, {len(self.result.errors)} error(s)"


@dataclass
class ProfileReport:
    schema: Schema
    entries: List[ProfileEntry] = field(default_factory=list)

    def passed(self) -> List[str]:
        return [e.environment for e in self.entries if e.result.is_valid]

    def failed(self) -> List[str]:
        return [e.environment for e in self.entries if not e.result.is_valid]

    def summary(self) -> str:
        lines = [f"Profile Report ({len(self.entries)} environment(s))"]
        for entry in self.entries:
            lines.append(f"  {entry}")
        return "\n".join(lines)

    def get(self, environment: str) -> Optional[ProfileEntry]:
        for e in self.entries:
            if e.environment == environment:
                return e
        return None


def profile_envs(schema: Schema, envs: Dict[str, Dict[str, str]]) -> ProfileReport:
    """Validate multiple named env dicts against a schema."""
    report = ProfileReport(schema=schema)
    validator = Validator(schema)
    for env_name, env_vars in envs.items():
        result = validator.validate(env_vars)
        report.entries.append(ProfileEntry(
            environment=env_name,
            env=env_vars,
            result=result,
        ))
    return report
