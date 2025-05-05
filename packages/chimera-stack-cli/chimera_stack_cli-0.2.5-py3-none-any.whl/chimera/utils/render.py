"""Jinja2-powered rendering helpers used across ChimeraStack.

This utility module centralises all template/string rendering so we do not
re-implement variable substitution logic in multiple places.  It exposes two
main helpers:

* ``render_string`` – render a *string* template with a context
* ``render_file`` – render a *file* on disk with a context

Both helpers use a **single, lazily-constructed** Jinja2 ``Environment`` with
``StrictUndefined`` so we fail fast when an undefined variable is referenced.
This behaviour mirrors what we expect from a scaffolding tool: it should alert
users/devs about missing variables instead of rendering silent placeholders.
"""

from __future__ import annotations

from pathlib import Path
from functools import lru_cache
from typing import Any, Dict

from jinja2 import Environment, FileSystemLoader, BaseLoader, StrictUndefined, select_autoescape

__all__ = [
    "render_string",
    "render_file",
]

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def _get_env(loader: BaseLoader | None = None) -> Environment:
    """Return a *cached* Jinja2 environment instance.

    We cache the :class:`~jinja2.Environment` because initialisation is a bit
    expensive (it sets up a parser, code generator, etc.).  A single instance
    is more than enough for the CLI lifetime.
    """

    if loader is None:
        loader = FileSystemLoader(".")  # default – overridden for file renders

    return Environment(
        loader=loader,
        autoescape=select_autoescape(default_for_string=False),
        undefined=StrictUndefined,  # fail hard on undefined variables
        trim_blocks=True,
        lstrip_blocks=True,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render_string(template: str, context: Dict[str, Any]) -> str:  # noqa: D401
    """Render *template* (a raw string) with *context* using Jinja2."""

    # We first render with a Jinja2 environment configured to recognise the
    # ``${VAR}`` placeholder style widely used in Docker/UNIX config files.

    env = _get_env(BaseLoader())
    # Override variable delimiters on *this* environment instance because we
    # cannot easily change them once the env is cached.  Hence we create a
    # *new* environment here instead of using the cached one.
    env = Environment(
        loader=env.loader,
        autoescape=env.autoescape,
        undefined=env.undefined,
        trim_blocks=env.trim_blocks,
        lstrip_blocks=env.lstrip_blocks,
        variable_start_string="${",
        variable_end_string="}",
    )

    rendered = env.from_string(template).render(**context)

    # ------------------------------------------------------------------
    # Back-compat: replace bare ``$VAR`` placeholders.
    # ------------------------------------------------------------------
    for key, value in context.items():
        rendered = rendered.replace(f"${key}", str(value))

    return rendered


def render_file(template_path: str | Path, context: Dict[str, Any]) -> str:  # noqa: D401
    """Render a template *file* at *template_path* with *context*.

    The file is *not* modified on disk – callers must write the returned value
    themselves if they wish to persist the rendered output.  This keeps the API
    flexible and side-effect-free.
    """

    template_path = Path(template_path)
    base_env = _get_env(FileSystemLoader(str(template_path.parent)))

    env = Environment(
        loader=base_env.loader,
        autoescape=base_env.autoescape,
        undefined=base_env.undefined,
        trim_blocks=base_env.trim_blocks,
        lstrip_blocks=base_env.lstrip_blocks,
        variable_start_string="${",
        variable_end_string="}",
    )

    tmpl = env.get_template(template_path.name)
    rendered = tmpl.render(**context)

    # Back-compat for $VAR placeholders
    for key, value in context.items():
        rendered = rendered.replace(f"${key}", str(value))

    return rendered
