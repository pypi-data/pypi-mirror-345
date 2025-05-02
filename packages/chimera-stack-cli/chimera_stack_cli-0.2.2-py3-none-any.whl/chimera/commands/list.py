"""
Implementation of the list command.
"""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from chimera.core import TemplateManager

console = Console()


def list_command(search: str = None, category: str = None) -> None:
    """List all available templates."""
    try:
        template_manager = TemplateManager()

        if search:
            templates = template_manager.search_templates(search)
            _display_template_list("Search Results", templates)
            return

        if category:
            templates_by_category = template_manager.get_templates_by_category()
            if category.lower() in templates_by_category:
                _display_template_list(
                    f"Category: {category}", templates_by_category[category.lower()])
            else:
                console.print(
                    f"[yellow]No templates found for category: {category}[/]")
                # Show available categories
                _display_available_categories(templates_by_category.keys())
            return

        # Display all templates grouped by category
        templates_by_category = template_manager.get_templates_by_category()

        if not any(templates_by_category.values()):
            console.print("[yellow]No templates found.[/]")
            return

        # Show header
        console.print(Markdown("# Available Templates\n"))

        for category, templates in templates_by_category.items():
            if templates:  # Only show categories with templates
                _display_template_list(category.upper(), templates)
                console.print()  # Add spacing between categories

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise


def _display_template_list(title: str, templates: list) -> None:
    """Display a list of templates in a formatted table."""
    table = Table(title=title, show_header=True, title_style="bold cyan")
    table.add_column("Template", style="cyan")
    table.add_column("Name", style="white")
    table.add_column("Description", style="white")
    table.add_column("Version", style="dim")
    table.add_column("Variants", style="green")

    for template in templates:
        # Format variants if available
        variants = template.get('variants', [])
        variant_str = ", ".join(variants) if variants else "default"

        table.add_row(
            template['id'],
            template.get('name', ''),
            template.get('description', ''),
            template.get('version', '1.0.0'),
            variant_str
        )

    console.print(Panel(table))


def _display_available_categories(categories: list) -> None:
    """Display available template categories."""
    console.print("\n[bold]Available categories:[/]")
    for category in sorted(categories):
        console.print(f"  • [cyan]{category}[/]")
