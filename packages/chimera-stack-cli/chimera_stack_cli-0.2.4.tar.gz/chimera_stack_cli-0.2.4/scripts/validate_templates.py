#!/usr/bin/env python3
"""Validate every `template.yaml` file in the repository.

Usage
-----
Run from repository root::

    python scripts/validate_templates.py  # or make it executable and run directly

The script will scan *src/chimera/templates/*** for any file called
``template.yaml`` (or ``template.yml`` for good measure), validate it against
ChimeraStack's schema, and exit with code 1 if any file is invalid.  This makes
it suitable for CI pipelines or pre-commit hooks.
"""

from __future__ import annotations
from chimera.core import validate_template, TemplateValidationError
from rich.table import Table
from rich.console import Console
import yaml

import sys
from pathlib import Path
from typing import List

# ---------------------------------------------------------------------------
# Ensure project src path is in sys.path before importing package modules.
# ---------------------------------------------------------------------------
PROJECT_SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(PROJECT_SRC))

# Now we can import chimera modules

# ---------------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------------

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent / \
    "src" / "chimera" / "templates"

console = Console()


def find_template_files(root: Path) -> List[Path]:
    """Return list of all template YAML files under *root*."""
    return [p for p in root.rglob("template.y*ml") if p.is_file()]


def main() -> None:  # noqa: D103
    failed: List[str] = []
    table = Table(title="Template Validation Results", show_lines=True)
    table.add_column("Template", style="cyan")
    table.add_column("Status", style="green")

    for tpl_file in sorted(find_template_files(TEMPLATE_ROOT)):
        rel = tpl_file.relative_to(Path.cwd()) if tpl_file.is_relative_to(
            Path.cwd()) else tpl_file
        try:
            with tpl_file.open("r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            validate_template(config, tpl_file)
            table.add_row(str(rel), "✓ Valid")
        except (TemplateValidationError, yaml.YAMLError) as err:
            failed.append(str(rel))
            table.add_row(str(rel), f"[red]✗ {err}")

    console.print(table)

    if failed:
        console.print(
            f"\n[bold red]{len(failed)} template(s) failed validation.[/]")
        sys.exit(1)

    console.print("\n[bold green]All templates are valid![/]")


if __name__ == "__main__":
    main()
