"""Audit .env files against a schema to produce a structured report."""

from dataclasses import dataclass, field
from typing import List, Optional
from envforge.schema import Schema
from envforge.validator import ValidationResult, validate


@dataclass
class AuditEntry:
    key: str
    status: str  # 'ok', 'missing', 'invalid', 'extra', 'default_used'
    message: Optional[str] = None

    def __str__(self) -> str:
        tag = f"[{self.status.upper()}]"
        return f"{tag} {self.key}" + (f": {self.message}" if self.message else "")


@dataclass
class AuditReport:
    entries: List[AuditEntry] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(e.status in ("ok", "default_used") for e in self.entries)

    def by_status(self, status: str) -> List[AuditEntry]:
        return [e for e in self.entries if e.status == status]

    def summary(self) -> str:
        counts = {}
        for e in self.entries:
            counts[e.status] = counts.get(e.status, 0) + 1
        parts = [f"{v} {k}" for k, v in sorted(counts.items())]
        result = "PASS" if self.passed else "FAIL"
        return f"Audit {result}: " + ", ".join(parts) if parts else f"Audit {result}"


def audit_env(env: dict, schema: Schema) -> AuditReport:
    """Audit an env dict against a schema and return a detailed AuditReport."""
    report = AuditReport()

    for var in schema.variables:
        key = var.name
        if key not in env:
            if var.required:
                report.entries.append(AuditEntry(key, "missing", "required variable not set"))
            elif var.default is not None:
                report.entries.append(AuditEntry(key, "default_used", f"default='{var.default}'"))
            else:
                report.entries.append(AuditEntry(key, "ok", "optional, not set"))
        else:
            value = env[key]
            result: ValidationResult = validate({key: value}, Schema(variables=[var]))
            if result.is_valid:
                report.entries.append(AuditEntry(key, "ok"))
            else:
                report.entries.append(AuditEntry(key, "invalid", "; ".join(str(e) for e in result.errors)))

    schema_keys = {v.name for v in schema.variables}
    for key in env:
        if key not in schema_keys:
            report.entries.append(AuditEntry(key, "extra", "not defined in schema"))

    return report
