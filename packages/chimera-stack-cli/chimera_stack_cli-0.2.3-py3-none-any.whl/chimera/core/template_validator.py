from __future__ import annotations

"""Template YAML validation logic.

Provides a thin wrapper around the `jsonschema` package so we can ensure that
any `template.yaml` (stack, component, core) respects a minimal contract
before the rest of the generator tries to use it.

The schema is intentionally **permissive**: we validate the presence and type
of core keys, but allow additional properties so we do not block forward
compatibility.
"""

from pathlib import Path
from typing import Any

import jsonschema

# ---------------------------------------------------------------------------
# JSON-Schema
# ---------------------------------------------------------------------------
# We rely on the `type` discriminator to tighten requirements for each kind of
# template. A stack **must** declare `components`, whereas a component/core
# must declare either `component` or `services` (depending on exact use-case).
# The schema can evolve as our template spec becomes more formal.
# ---------------------------------------------------------------------------

_SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "required": ["name", "version", "description", "type"],
    "properties": {
        "name": {"type": "string"},
        "version": {"type": "string"},
        "description": {"type": "string"},
        "type": {"type": "string", "enum": ["stack", "component", "core"]},
        # Common optional keys (kept loose for now)
        "tags": {"type": "array", "items": {"type": "string"}},
        "services": {"type": "object"},
        "environment": {"type": "object"},
        "files": {"type": "array"},
        "compose": {"type": "object"},
        "network": {"type": "object"},
        "post_create": {"anyOf": [{"type": "array"}, {"type": "object"}]},
        # Stack-specific
        "components": {"type": "object"},
        "stack": {"type": "object"},
        "variants": {"type": "array", "items": {"type": "string"}},
        # Component-specific
        "component": {"type": "object"},
    },
    "allOf": [
        {
            "if": {"properties": {"type": {"const": "stack"}}},
            "then": {"required": ["components"]},
        },
        {
            "if": {"properties": {"type": {"const": "component"}}},
            "then": {"required": ["component"]},
        },
    ],
    # Allow additional keys so we stay forward-compatible.
    "additionalProperties": True,
}


class TemplateValidationError(Exception):
    """Raised when a template.yaml file fails schema validation."""


def validate_template(config: dict[str, Any], path: Path | str | None = None) -> None:
    """Validate ``config`` against the Chimera template schema.

    Parameters
    ----------
    config:
        The *parsed* YAML document (typically produced by ``yaml.safe_load``).
    path:
        Optional path to the YAML file, only used for better error messages.

    Raises
    ------
    TemplateValidationError
        If validation fails. The exception message contains the validation
        error plus the offending file path when provided.
    """

    try:
        jsonschema.validate(instance=config, schema=_SCHEMA)
    except jsonschema.ValidationError as exc:  # pragma: no cover – simple re-throw
        file_hint = f" in {path}" if path else ""
        raise TemplateValidationError(
            f"template.yaml validation error{file_hint}: {exc.message}") from exc
