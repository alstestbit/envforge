"""Linter for .env files — checks style and convention issues."""

from dataclasses import dataclass, field
from typing import List, Dict

from envforge.schema import Schema


@dataclass
class LintIssue:
    key: str
    code: str
    message: str
    severity: str = "warning"  # 'warning' or 'error'

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.code}: {self.key} — {self.message}"


@dataclass
class LintReport:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)

    @property
    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def summary(self) -> str:
        return (
            f"{len(self.errors)} error(s), {len(self.warnings)} warning(s) "
            f"— {'PASSED' if self.passed else 'FAILED'}"
        )


def lint_env(env: Dict[str, str], schema: Schema) -> LintReport:
    """Run lint checks on a parsed env dict against a schema."""
    report = LintReport()
    schema_keys = {var.name for var in schema.variables}

    for key, value in env.items():
        # Check naming convention: should be UPPER_SNAKE_CASE
        if key != key.upper():
            report.issues.append(LintIssue(
                key=key,
                code="E001",
                message="Key should be UPPER_SNAKE_CASE",
                severity="error",
            ))

        # Warn about keys with empty values that are required
        var = next((v for v in schema.variables if v.name == key), None)
        if var and var.required and value.strip() == "":
            report.issues.append(LintIssue(
                key=key,
                code="W001",
                message="Required key has an empty value",
                severity="warning",
            ))

        # Warn about keys not defined in schema
        if key not in schema_keys:
            report.issues.append(LintIssue(
                key=key,
                code="W002",
                message="Key is not defined in schema",
                severity="warning",
            ))

        # Warn about values that look like they contain unresolved placeholders
        if "${" in value or "%{" in value:
            report.issues.append(LintIssue(
                key=key,
                code="W003",
                message="Value appears to contain an unresolved placeholder",
                severity="warning",
            ))

    return report
