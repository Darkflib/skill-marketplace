"""
CLI entry point for {{PROJECT_NAME}}.

Beautiful command-line interface using Click and Rich.
"""

import sys

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from app.commands.example import example
from app.core.config import settings
from app.core.logging import setup_logging

console = Console()
logger = setup_logging(settings.APP_NAME, settings.LOG_LEVEL)


@click.group()
@click.version_option(version="0.1.0")
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "csv"]),
    default=settings.OUTPUT_FORMAT,
    help="Output format",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, format: str):
    """
    {{PROJECT_NAME}} - {{DESCRIPTION}}
    
    Use --help on any command for more information.
    """
    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["FORMAT"] = format
    
    if verbose:
        logger.info("Verbose mode enabled")


# Register command groups
cli.add_command(example)


@cli.command()
def version():
    """Show version information."""
    console.print(
        Panel.fit(
            f"[bold cyan]{{{{PROJECT_NAME}}}}[/bold cyan]\n"
            f"Version: [green]0.1.0[/green]\n"
            f"Python: [green]{sys.version.split()[0]}[/green]",
            title="Version Info",
            border_style="cyan",
        )
    )


if __name__ == "__main__":
    cli()
