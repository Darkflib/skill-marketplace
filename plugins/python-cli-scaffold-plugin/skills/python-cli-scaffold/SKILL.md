---
name: python-cli-scaffold
description: Scaffolds beautiful Python CLI tools with Click framework and Rich terminal output. Use when creating command-line tools, automation scripts, dev tools, or admin utilities. Includes command groups, options/arguments, progress bars, tables, spinners, prompts, structured logging, testing setup, and Docker support for containerized CLIs.
---

# Python CLI Scaffold

## Overview

Provides automated scaffolding for production-ready Python CLI tools built with Click and Rich. Creates beautiful, user-friendly command-line interfaces with tables, progress bars, spinners, interactive prompts, and colored output. Includes structured JSONL logging, testing infrastructure, and optional Docker containerization.

## When to Use This Skill

Use this skill when:
- Creating command-line tools or utilities
- Building dev tools and automation scripts
- Implementing admin or ops tooling
- Creating one-off data processing scripts you want productionized
- Building CLI clients for APIs or services
- Creating internal tools for your team

## Quick Start

### Using the Scaffold Script

```bash
# Create a new CLI project
python /mnt/skills/[skill-path]/scripts/scaffold.py data-tool "CLI for data processing"
```

This creates a complete CLI structure ready for customization.

## Project Structure

The scaffold creates:

```
data-tool/
├── app/
│   ├── cli.py                    # CLI entry point (Click group)
│   ├── commands/                 # Command implementations
│   │   ├── __init__.py
│   │   └── example.py            # Example commands with Rich patterns
│   └── core/
│       ├── __init__.py
│       ├── config.py             # Pydantic settings
│       └── logging.py            # Structured logging
├── tests/
│   ├── __init__.py
│   └── test_commands.py          # CLI tests
├── pyproject.toml                # UV project config with CLI entrypoint
├── Dockerfile                    # Optional container image
├── .env.example
└── README.md
```

## Technology Stack

### Core Dependencies

- **Python 3.12+**: Modern Python features
- **Click**: Composable command-line framework
- **Rich**: Beautiful terminal output
- **Pydantic**: Type-safe configuration
- **structlog**: Structured JSONL logging

### Development Dependencies

- **pytest**: CLI testing
- **ruff**: Linting and formatting
- **mypy**: Static type checking

## Setup and Installation

### Local Development

```bash
# Install dependencies
uv sync

# Install CLI in development mode
uv pip install -e .

# Run CLI
data-tool --help
data-tool example greet --name Alice
```

### Without Installation

```bash
# Run directly with UV
uv run python -m app.cli --help
uv run python -m app.cli example table
```

## CLI Entry Point

The scaffold creates a Click group as the main entry point:

```python
# app/cli.py
import click
from rich.console import Console

console = Console()

@click.group()
@click.version_option(version="0.1.0")
@click.option("--verbose", "-v", is_flag=True)
@click.option("--format", "-f", type=click.Choice(["table", "json", "csv"]))
@click.pass_context
def cli(ctx, verbose, format):
    """My awesome CLI tool."""
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose
    ctx.obj["FORMAT"] = format

# Register command groups
from app.commands.example import example
cli.add_command(example)
```

**Configured in pyproject.toml**:
```toml
[project.scripts]
data-tool = "app.cli:cli"
```

## Rich Output Patterns

The scaffold includes examples of common Rich patterns:

### Tables

```python
from rich.table import Table
from rich.console import Console

console = Console()

table = Table(title="Data Summary", show_header=True)
table.add_column("ID", style="cyan", justify="right")
table.add_column("Name", style="green")
table.add_column("Status", style="yellow")

table.add_row("1", "Alice", "✅ Active")
table.add_row("2", "Bob", "⏸️  Pending")

console.print(table)
```

**Output**:
```
                Data Summary
┏━━━━┳━━━━━━━┳━━━━━━━━━━━┓
┃ ID ┃ Name  ┃ Status    ┃
┡━━━━╇━━━━━━━╇━━━━━━━━━━━┩
│  1 │ Alice │ ✅ Active  │
│  2 │ Bob   │ ⏸️ Pending │
└────┴───────┴───────────┘
```

### Progress Bars

```python
from rich.progress import track
import time

for item in track(range(100), description="Processing..."):
    time.sleep(0.01)
    # Process item
```

**Output**:
```
Processing... ━━━━━━━━━━━━━━━━━━━━ 100% 0:00:01
```

### Spinners

```python
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
) as progress:
    task = progress.add_task("Working...", total=None)
    time.sleep(3)
```

**Output**:
```
⠋ Working...
```

### Interactive Prompts

```python
from rich.prompt import Confirm, Prompt

name = Prompt.ask("What's your name?")
age = Prompt.ask("What's your age?", default="25")

if Confirm.ask("Would you like to continue?"):
    print("Let's go!")
```

### Panels and Boxes

```python
from rich.panel import Panel
from rich.console import Console

console = Console()

console.print(
    Panel.fit(
        "[bold cyan]Important Message[/bold cyan]\n"
        "This is a highlighted panel",
        title="Notice",
        border_style="cyan",
    )
)
```

### Trees

```python
from rich.tree import Tree

tree = Tree("📁 Project")
app = tree.add("📁 app")
app.add("📄 cli.py")
app.add("📄 config.py")

console.print(tree)
```

**Output**:
```
📁 Project
└── 📁 app
    ├── 📄 cli.py
    └── 📄 config.py
```

### JSON Output

```python
from rich.console import Console

console = Console()

data = {"name": "Alice", "age": 30, "active": True}
console.print_json(data=data)
```

## Click Command Patterns

### Basic Command

```python
@click.command()
@click.option("--name", "-n", help="Name to greet")
@click.option("--count", "-c", default=1, help="Number of greetings")
def greet(name, count):
    """Greet someone."""
    for i in range(count):
        console.print(f"[green]Hello {name}![/green]")
```

**Usage**:
```bash
data-tool greet --name Alice --count 3
```

### Command Groups

```python
@click.group()
def database():
    """Database operations."""
    pass

@database.command()
def migrate():
    """Run migrations."""
    console.print("[cyan]Running migrations...[/cyan]")

@database.command()
def seed():
    """Seed database."""
    console.print("[cyan]Seeding database...[/cyan]")
```

**Usage**:
```bash
data-tool database migrate
data-tool database seed
```

### Arguments and Options

```python
@click.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.argument("output_file", type=click.Path())
@click.option("--format", "-f", type=click.Choice(["json", "csv"]))
@click.option("--verbose", "-v", is_flag=True)
def convert(input_file, output_file, format, verbose):
    """Convert file format."""
    if verbose:
        console.print(f"Converting {input_file} to {output_file}")
```

**Usage**:
```bash
data-tool convert data.json data.csv --format csv --verbose
```

### Context Passing

```python
@click.group()
@click.option("--config", type=click.Path())
@click.pass_context
def cli(ctx, config):
    """Main CLI."""
    ctx.ensure_object(dict)
    ctx.obj["CONFIG"] = config

@cli.command()
@click.pass_context
def status(ctx):
    """Show status."""
    config = ctx.obj.get("CONFIG")
    console.print(f"Config: {config}")
```

### Prompts

```python
@click.command()
@click.option("--name", prompt="Your name")
@click.option("--password", prompt=True, hide_input=True)
def login(name, password):
    """Login to service."""
    console.print(f"Logging in as {name}...")
```

**Usage**:
```bash
$ data-tool login
Your name: Alice
Password: ****
Logging in as Alice...
```

## Adding New Commands

1. **Create command file**:

```python
# app/commands/data.py
import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
def data():
    """Data processing commands."""
    pass

@data.command()
@click.argument("filename", type=click.Path(exists=True))
def analyze(filename):
    """Analyze data file."""
    console.print(f"[cyan]Analyzing {filename}...[/cyan]")
    
    # Process data...
    
    # Show results
    table = Table(title="Analysis Results")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Records", "1,234")
    table.add_row("Columns", "10")
    
    console.print(table)
```

2. **Register in cli.py**:

```python
from app.commands.data import data

cli.add_command(data)
```

3. **Use it**:

```bash
data-tool data analyze myfile.csv
```

## Testing

The scaffold includes Click's testing utilities:

```python
# tests/test_commands.py
from click.testing import CliRunner
from app.cli import cli

def test_greet():
    """Test greet command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["example", "greet", "--name", "Alice"])
    
    assert result.exit_code == 0
    assert "Hello Alice!" in result.output

def test_table():
    """Test table command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["example", "table", "--rows", "5"])
    
    assert result.exit_code == 0
```

**Running tests**:
```bash
uv run pytest
uv run pytest --cov=app
```

## Configuration Management

### Pydantic Settings

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "data-tool"
    LOG_LEVEL: str = "INFO"
    OUTPUT_FORMAT: str = "table"
    
    # API configuration
    API_URL: str = "https://api.example.com"
    API_KEY: str | None = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### Environment Variables

```env
# .env
APP_NAME=data-tool
LOG_LEVEL=DEBUG
OUTPUT_FORMAT=json
API_URL=https://api.example.com
API_KEY=your-key-here
```

### Using in Commands

```python
from app.core.config import settings

@click.command()
def status():
    """Show configuration."""
    console.print(f"App: {settings.APP_NAME}")
    console.print(f"Log Level: {settings.LOG_LEVEL}")
```

## Structured Logging

All logs output as JSON lines:

```python
import structlog

logger = structlog.get_logger()

@click.command()
def process():
    """Process data."""
    logger.info("Processing started", count=100)
    # ... do work ...
    logger.info("Processing complete", processed=100, failed=0)
```

**Output**:
```json
{"event": "Processing started", "timestamp": "2025-01-01T12:00:00Z", "level": "info", "count": 100}
{"event": "Processing complete", "timestamp": "2025-01-01T12:00:10Z", "level": "info", "processed": 100, "failed": 0}
```

## Common Patterns

### API Client

```python
import httpx
from rich.console import Console

console = Console()

@click.command()
@click.argument("endpoint")
def fetch(endpoint):
    """Fetch data from API."""
    with console.status("[bold green]Fetching..."):
        response = httpx.get(f"https://api.example.com/{endpoint}")
        data = response.json()
    
    console.print_json(data=data)
```

### File Processing

```python
@click.command()
@click.argument("input", type=click.File("r"))
@click.argument("output", type=click.File("w"))
def transform(input, output):
    """Transform file."""
    for line in track(input.readlines(), description="Processing"):
        # Transform line
        output.write(line.upper())
```

### Error Handling

```python
from rich.console import Console

console = Console()

@click.command()
def risky():
    """Command that might fail."""
    try:
        result = do_risky_operation()
        console.print("[green]Success![/green]")
    except ValueError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise click.Abort()
```

### Progress with Steps

```python
from rich.progress import Progress

@click.command()
def multi_step():
    """Multi-step process."""
    with Progress() as progress:
        task1 = progress.add_task("[cyan]Step 1...", total=100)
        task2 = progress.add_task("[green]Step 2...", total=50)
        
        # Process step 1
        for i in range(100):
            progress.update(task1, advance=1)
        
        # Process step 2
        for i in range(50):
            progress.update(task2, advance=1)
```

## Deployment

### Docker Container

```bash
# Build image
docker build -t data-tool:latest .

# Run CLI in container
docker run --rm data-tool:latest --help
docker run --rm data-tool:latest example greet --name Alice

# With environment file
docker run --rm --env-file .env data-tool:latest status
```

### PyInstaller Executable

```bash
# Install PyInstaller
uv add --dev pyinstaller

# Build single-file executable
uv run pyinstaller --onefile --name data-tool app/cli.py

# Run executable
./dist/data-tool --help
```

### Distribution

```bash
# Build wheel
uv build

# Install from wheel
pip install dist/data_tool-0.1.0-py3-none-any.whl

# Upload to PyPI
uv publish
```

## Best Practices

### User Experience

- Use clear, descriptive help text
- Provide sensible defaults
- Show progress for long operations
- Use colors meaningfully (green=success, red=error, yellow=warning)
- Format output appropriately (tables for data, panels for messages)

### Error Handling

- Catch and display errors clearly
- Use `click.Abort()` to exit gracefully
- Log errors for debugging
- Provide actionable error messages

### Configuration

- Support environment variables
- Provide `--config` option for config files
- Use `.env` for development
- Document all configuration options

### Testing

- Use `CliRunner` for integration tests
- Test error conditions
- Test with various input combinations
- Mock external dependencies

## Extending the Scaffold

### Add Database Support

```python
# app/core/database.py
from sqlalchemy import create_engine
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)

# Use in commands
@click.command()
def query():
    with engine.connect() as conn:
        result = conn.execute("SELECT * FROM users")
        # Display with Rich table
```

### Add Async Support

```python
import asyncio
import click

def async_command(f):
    """Decorator for async Click commands."""
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@click.command()
@async_command
async def fetch_all():
    """Fetch data asynchronously."""
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
```

### Add Config File Support

```python
import yaml

@click.group()
@click.option("--config", type=click.Path())
@click.pass_context
def cli(ctx, config):
    """CLI with config file support."""
    ctx.ensure_object(dict)
    
    if config:
        with open(config) as f:
            ctx.obj["CONFIG"] = yaml.safe_load(f)
```

## Troubleshooting

### Command not found after installation

```bash
# Reinstall in editable mode
uv pip install -e .

# Or use full path
~/.local/bin/data-tool --help
```

### Rich output not showing colors

```bash
# Force color output
data-tool --color example table

# Or set environment variable
export FORCE_COLOR=1
```

### Tests failing

```bash
# Run with verbose output
uv run pytest -vv

# Run specific test
uv run pytest tests/test_commands.py::test_greet -v
```

## Summary

This scaffold provides:
- ✅ Click framework for robust CLIs
- ✅ Rich for beautiful terminal output
- ✅ Tables, progress bars, spinners, prompts
- ✅ Command groups and subcommands
- ✅ Options, arguments, and flags
- ✅ Context passing between commands
- ✅ Structured JSONL logging
- ✅ Pydantic configuration management
- ✅ Testing with CliRunner
- ✅ Docker containerization
- ✅ PyInstaller executable building

Use the scaffold script for instant setup, then add your command implementations!
