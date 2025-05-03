"""
ChimeraStack CLI entry point.
"""
import click
from rich.console import Console
from rich.traceback import install
import questionary
from datetime import datetime

from chimera import __version__, __author__, __email__, __license__, __repository__, __description__
from chimera.commands.create import create_command
from chimera.commands.list import list_command
from chimera.core import TemplateManager

# Set up rich error handling
install(show_locals=True)
console = Console()


class CustomGroup(click.Group):
    def format_help(self, ctx, formatter):
        # Custom header with ASCII art
        formatter.write("""
 ╔════════════════════════════════════════════════════════════════════════╗
 ║                                                                        ║
 ║   ██████╗██╗  ██╗██╗███╗   ███╗███████╗██████╗  █████╗                ║
 ║  ██╔════╝██║  ██║██║████╗ ████║██╔════╝██╔══██╗██╔══██╗               ║
 ║  ██║     ███████║██║██╔████╔██║█████╗  ██████╔╝███████║               ║
 ║  ██║     ██╔══██║██║██║╚██╔╝██║██╔══╝  ██╔══██╗██╔══██║               ║
 ║  ╚██████╗██║  ██║██║██║ ╚═╝ ██║███████╗██║  ██║██║  ██║               ║
 ║   ╚═════╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝               ║
 ║                                                                        ║
 ║   ███████╗████████╗ █████╗  ██████╗██╗  ██╗                           ║
 ║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝██║ ██╔╝                           ║
 ║   ███████╗   ██║   ███████║██║     █████╔╝                            ║
 ║   ╚════██║   ██║   ██╔══██║██║     ██╔═██╗                            ║
 ║   ███████║   ██║   ██║  ██║╚██████╗██║  ██╗                           ║
 ║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝                           ║
 ║                                                                        ║
 ║                        by Amirofcodes                                  ║
 ║                                                                        ║
 ╚════════════════════════════════════════════════════════════════════════╝

ChimeraStack CLI v{0} - Copyright © {1}

{2}

Author: {3} <{4}>
License: {5}
Repository: {6}
        """.format(__version__, datetime.now().year, __description__, __author__, __email__, __license__, __repository__))

        # Standard help content
        formatter.write("\n")
        super().format_help(ctx, formatter)

        # Additional tips at the bottom
        formatter.write("\n\nQuick Start:\n")
        formatter.write(
            "  1. Create a new project: chimera create my-project\n")
        formatter.write("  2. List available templates: chimera list\n\n")
        formatter.write(
            "For more information, visit: {}\n".format(__repository__))


@click.group(cls=CustomGroup)
@click.version_option(
    version=__version__,
    message=(
        f'chimera, version %(version)s\n'
        f'Author: {__author__} <{__email__}>\n'
        f'License: {__license__}\n'
        f'Repository: {__repository__}\n'
    )
)
def cli():
    """ChimeraStack CLI - A development environment manager.

    Quickly set up pre-configured Docker-based development environments.
    """
    pass


@cli.command()
@click.argument('name')
@click.option('--template', '-t', help='Template to use for the project (e.g., php/nginx/mysql)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output during creation')
def create(name: str, template: str | None = None, verbose: bool = False):
    """Create a new project from a template.

    Examples:
    \b
    chimera create myproject                    # Interactive mode
    chimera create myproject -t php/nginx/mysql # Direct template selection
    chimera create myproject -v                 # Verbose output (shows detailed process)
    """
    create_command(name, template, verbose)


@cli.command()
@click.option('--search', '-s', help='Search for templates (e.g., mysql, postgresql)')
@click.option('--category', '-c', help='Filter by category (e.g., "PHP Development", "Fullstack Development")')
def list(search: str = None, category: str = None):
    """List available templates.

    Examples:
    \b
    chimera list                                  # List all templates
    chimera list -s mysql                         # Search for templates containing "mysql"
    chimera list -c "PHP Development"             # List PHP templates
    chimera list -c "Fullstack Development"       # List fullstack templates
    """
    list_command(search, category)


def main():
    try:
        cli()
    except Exception as e:
        console.print_exception()
        exit(1)


if __name__ == '__main__':
    main()
