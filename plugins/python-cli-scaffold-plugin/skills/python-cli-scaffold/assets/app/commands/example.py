"""
Example commands demonstrating Click + Rich patterns.
"""

import time
from typing import Any

import click
from rich.console import Console
from rich.progress import track, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.tree import Tree
import json

console = Console()


@click.group()
def example():
    """Example commands showcasing Rich features."""
    pass


@example.command()
@click.option("--name", "-n", prompt="Your name", help="Name to greet")
@click.option("--count", "-c", default=1, help="Number of greetings")
def greet(name: str, count: int):
    """
    Greet someone with style.
    
    Example: cli example greet --name Alice --count 3
    """
    for i in range(count):
        console.print(f"[bold green]Hello {name}![/bold green] (#{i + 1})")
    
    logger.info("Greet command executed", name=name, count=count)


@example.command()
@click.option("--rows", "-r", default=5, help="Number of rows")
def table(rows: int):
    """
    Display data in a table.
    
    Example: cli example table --rows 10
    """
    table = Table(title="Sample Data", show_header=True, header_style="bold magenta")
    
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Name", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Value", justify="right")
    
    # Sample data
    statuses = ["✅ Active", "⏸️  Pending", "❌ Inactive"]
    for i in range(rows):
        table.add_row(
            str(i + 1),
            f"Item {i + 1}",
            statuses[i % 3],
            f"${(i + 1) * 100:,}",
        )
    
    console.print(table)


@example.command()
@click.option("--items", "-n", default=10, help="Number of items to process")
@click.option("--delay", "-d", default=0.1, type=float, help="Delay per item")
def progress(items: int, delay: float):
    """
    Show a progress bar.
    
    Example: cli example progress --items 20 --delay 0.05
    """
    console.print(f"[cyan]Processing {items} items...[/cyan]\n")
    
    for i in track(range(items), description="Processing..."):
        time.sleep(delay)
        # Simulate work
    
    console.print("\n[bold green]✓ Complete![/bold green]")


@example.command()
@click.option("--duration", "-d", default=3, type=int, help="Spinner duration (seconds)")
def spinner(duration: int):
    """
    Show a spinner for long-running tasks.
    
    Example: cli example spinner --duration 5
    """
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Working...", total=None)
        time.sleep(duration)
        progress.update(task, completed=True)
    
    console.print("[bold green]✓ Task complete![/bold green]")


@example.command()
def prompt():
    """
    Interactive prompts.
    
    Example: cli example prompt
    """
    name = Prompt.ask("What's your name?")
    console.print(f"Hello, [bold cyan]{name}[/bold cyan]!")
    
    age = Prompt.ask("What's your age?", default="25")
    console.print(f"You are [yellow]{age}[/yellow] years old")
    
    if Confirm.ask("Would you like to continue?"):
        console.print("[green]Great! Let's continue...[/green]")
    else:
        console.print("[yellow]Okay, goodbye![/yellow]")


@example.command()
def tree():
    """
    Display a tree structure.
    
    Example: cli example tree
    """
    tree = Tree("📁 [bold cyan]Project Structure[/bold cyan]")
    
    app = tree.add("📁 app")
    app.add("📄 cli.py")
    app.add("📄 __init__.py")
    
    commands = app.add("📁 commands")
    commands.add("📄 example.py")
    commands.add("📄 __init__.py")
    
    core = app.add("📁 core")
    core.add("📄 config.py")
    core.add("📄 logging.py")
    
    tree.add("📄 pyproject.toml")
    tree.add("📄 README.md")
    
    console.print(tree)


@example.command()
@click.argument("data", type=str)
@click.option("--pretty", "-p", is_flag=True, help="Pretty print JSON")
@click.pass_context
def json_output(ctx: click.Context, data: str, pretty: bool):
    """
    Output data as JSON.
    
    Example: cli example json-output '{"key":"value"}' --pretty
    """
    try:
        # Parse input data
        parsed = json.loads(data)
        
        # Add metadata
        result = {
            "data": parsed,
            "format": ctx.obj.get("FORMAT", "json"),
            "verbose": ctx.obj.get("VERBOSE", False),
        }
        
        # Output
        if pretty:
            console.print_json(data=result)
        else:
            click.echo(json.dumps(result))
            
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Error:[/bold red] Invalid JSON - {e}")
        raise click.Abort()


# Import logger from cli module
from app.cli import logger
