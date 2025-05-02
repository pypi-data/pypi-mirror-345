"""
Implementation of the create command.
"""
import click
import questionary
from rich.console import Console
from chimera.core import TemplateManager

console = Console()


def create_command(name: str, template: str | None = None, verbose: bool = False) -> None:
    """Create a new project from a template."""
    try:
        template_manager = TemplateManager(verbose=verbose)
        variant = None

        if not template:
            # Get all templates first
            templates_by_category = template_manager.get_templates_by_category()

            # Step 1: Select category
            categories = list(templates_by_category.keys())
            category = questionary.select(
                "Choose a category:",
                choices=categories,
                use_indicator=True
            ).ask()

            if not category:
                console.print("[red]Category selection cancelled[/]")
                return

            # Step 2: Select template from category
            templates = templates_by_category[category]
            choices = [
                {
                    'name': f"{t['id']} - {t['description']}",
                    'value': t['id']
                }
                for t in templates
            ]

            selected = questionary.select(
                "Choose a template:",
                choices=choices,
                use_indicator=True
            ).ask()

            if not selected:
                console.print("[red]Template selection cancelled[/]")
                return

            template = selected

            # Step 3: Check for variants and select if available
            template_info = next(
                (t for t in templates if t['id'] == template), None)
            if template_info and 'variants' in template_info and template_info['variants']:
                variants = template_info['variants']
                if len(variants) > 1:  # Only prompt if multiple variants exist
                    variant = questionary.select(
                        "Choose a variant:",
                        choices=variants,
                        use_indicator=True
                    ).ask()

                    if not variant:
                        console.print("[red]Variant selection cancelled[/]")
                        return

        # Create the project
        if template:
            if variant:
                console.print(
                    f"Creating project [bold blue]{name}[/] using template [bold green]{template}[/] with variant [bold cyan]{variant}[/]")
                template_manager.create_project(
                    template, name, variant=variant)
            else:
                console.print(
                    f"Creating project [bold blue]{name}[/] using template [bold green]{template}[/]")
                template_manager.create_project(template, name)
        else:
            console.print("[red]No template selected[/]")

    except Exception as e:
        console.print(f"[bold red]Error:[/] {str(e)}")
        raise
