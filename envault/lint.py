"""Lint .env variable names and values for common issues."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


class LintError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


@dataclass
class LintIssue:
    key: str
    severity: str  # "error" | "warning"
    message: str

    def as_dict(self) -> dict:
        return {"key": self.key, "severity": self.severity, "message": self.message}


@dataclass
class LintResult:
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)

    def summary(self) -> str:
        errors = sum(1 for i in self.issues if i.severity == "error")
        warnings = sum(1 for i in self.issues if i.severity == "warning")
        return f"{errors} error(s), {warnings} warning(s)"


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_LOWER_KEY_RE = re.compile(r'^[a-z]')


def lint_env(env: Dict[str, str]) -> LintResult:
    """Lint a dict of env vars, returning a LintResult with any issues found."""
    result = LintResult()

    for key, value in env.items():
        if not key:
            result.issues.append(LintIssue(key="(empty)", severity="error", message="Key must not be empty."))
            continue

        if not _VALID_KEY_RE.match(key):
            if _LOWER_KEY_RE.match(key):
                result.issues.append(LintIssue(key=key, severity="warning", message="Key should be UPPER_SNAKE_CASE."))
            else:
                result.issues.append(LintIssue(key=key, severity="error", message="Key contains invalid characters."))

        if value == "":
            result.issues.append(LintIssue(key=key, severity="warning", message="Value is empty."))

        if "\n" in value:
            result.issues.append(LintIssue(key=key, severity="warning", message="Value contains a newline character."))

        if len(value) > 4096:
            result.issues.append(LintIssue(key=key, severity="warning", message="Value exceeds 4096 characters."))

    return result
