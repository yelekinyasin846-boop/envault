"""Validation helpers for envault vault contents."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List


class ValidationError(Exception):
    def __init__(self, message: str, issues: "List[ValidationIssue]" = None):
        super().__init__(message)
        self.issues = issues or []


@dataclass
class ValidationIssue:
    key: str
    message: str
    severity: str  # 'error' | 'warning'

    def as_dict(self) -> dict:
        return {"key": self.key, "message": self.message, "severity": self.severity}


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def errors(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> List[ValidationIssue]:
        return [i for i in self.issues if i.severity == "warning"]

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def summary(self) -> str:
        if not self.issues:
            return "All variables passed validation."
        parts = []
        if self.errors:
            parts.append(f"{len(self.errors)} error(s)")
        if self.warnings:
            parts.append(f"{len(self.warnings)} warning(s)")
        return "Validation: " + ", ".join(parts) + "."


_VALID_KEY_RE = re.compile(r'^[A-Z_][A-Z0-9_]*$')
_URL_RE = re.compile(r'^https?://', re.IGNORECASE)
_SECRET_HINTS = ("password", "secret", "token", "key", "private", "credential")


def validate_env(vars_: Dict[str, str], schema: Dict[str, dict] = None) -> ValidationResult:
    """Validate a dict of env vars against optional schema rules.

    Schema keys map to rule dicts with optional fields:
      required (bool), min_length (int), max_length (int), pattern (str)
    """
    result = ValidationResult()
    schema = schema or {}

    for key, value in vars_.items():
        if not _VALID_KEY_RE.match(key):
            result.issues.append(ValidationIssue(key, f"Key '{key}' contains invalid characters.", "error"))

        if not value:
            result.issues.append(ValidationIssue(key, f"Key '{key}' has an empty value.", "warning"))

        lower_key = key.lower()
        if any(hint in lower_key for hint in _SECRET_HINTS) and len(value) < 8:
            result.issues.append(ValidationIssue(key, f"Secret-like key '{key}' has a suspiciously short value.", "warning"))

        if key in schema:
            rules = schema[key]
            if rules.get("required") and not value:
                result.issues.append(ValidationIssue(key, f"Required key '{key}' is missing a value.", "error"))
            min_len = rules.get("min_length")
            if min_len is not None and len(value) < min_len:
                result.issues.append(ValidationIssue(key, f"Value for '{key}' is shorter than min_length={min_len}.", "error"))
            max_len = rules.get("max_length")
            if max_len is not None and len(value) > max_len:
                result.issues.append(ValidationIssue(key, f"Value for '{key}' exceeds max_length={max_len}.", "error"))
            pattern = rules.get("pattern")
            if pattern and not re.search(pattern, value):
                result.issues.append(ValidationIssue(key, f"Value for '{key}' does not match pattern '{pattern}'.", "error"))

    for required_key, rules in schema.items():
        if rules.get("required") and required_key not in vars_:
            result.issues.append(ValidationIssue(required_key, f"Required key '{required_key}' is absent.", "error"))

    return result
