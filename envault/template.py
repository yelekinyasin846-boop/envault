"""Template rendering: substitute vault variables into text templates."""

import re
from typing import Dict, Optional

from envault.exceptions import EnvaultError


class TemplateError(EnvaultError):
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


# Matches ${VAR_NAME} or $VAR_NAME patterns
_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def render_template(
    template_text: str,
    variables: Dict[str, str],
    strict: bool = True,
) -> str:
    """Render a template string by substituting env variables.

    Args:
        template_text: Text containing $VAR or ${VAR} placeholders.
        variables: Mapping of variable names to values.
        strict: If True, raise TemplateError for missing variables.
                If False, leave unresolved placeholders as-is.

    Returns:
        Rendered string with substitutions applied.
    """
    missing = []

    def _replace(match: re.Match) -> str:
        name = match.group(1) or match.group(2)
        if name in variables:
            return variables[name]
        if strict:
            missing.append(name)
            return match.group(0)
        return match.group(0)

    result = _PATTERN.sub(_replace, template_text)

    if strict and missing:
        raise TemplateError(
            f"Template references undefined variable(s): {', '.join(sorted(missing))}"
        )

    return result


def render_template_file(
    template_path: str,
    variables: Dict[str, str],
    strict: bool = True,
) -> str:
    """Read a template file and render it with the given variables."""
    try:
        with open(template_path, "r", encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise TemplateError(f"Cannot read template file '{template_path}': {exc}") from exc

    return render_template(text, variables, strict=strict)


def list_placeholders(template_text: str):
    """Return a sorted list of unique variable names referenced in the template."""
    names = set()
    for match in _PATTERN.finditer(template_text):
        names.add(match.group(1) or match.group(2))
    return sorted(names)
