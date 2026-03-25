# {{PROJECT_NAME}}

{{DESCRIPTION}}

Beautiful command-line interface built with Click and Rich.

## Tech Stack

- **Python 3.12** with UV for package management
- **Click** for CLI framework
- **Rich** for beautiful terminal output
- **Pydantic** for configuration management
- **structlog** for structured logging

## Project Structure

```
{{PROJECT_NAME}}/
├── app/
│   ├── cli.py               # CLI entry point
│   ├── commands/            # Command implementations
│   │   ├── __init__.py
│   │   └── example.py
│   └── core/                # Core functionality
│       ├── __init__.py
│       ├── config.py        # Configuration
│       └── logging.py       # Structured logging
├── tests/                   # Test suite
│   ├── __init__.py
│   └── test_commands.py
├── pyproject.toml           # Project dependencies
├── Dockerfile               # Container image (optional)
└── .env.example             # Environment template
```

## Quick Start

### Installation

```bash
# Install dependencies
uv sync

# Install CLI in development mode
uv pip install -e .
```

### Usage

```bash
# Show help
{{PROJECT_NAME}} --help

# Run a command
{{PROJECT_NAME}} example greet --name Alice

# Enable verbose output
{{PROJECT_NAME}} --verbose example table

# Show version
{{PROJECT_NAME}} version
```

## Development

### Running Locally

```bash
# Without installation
uv run python -m app.cli --help

# With installation
{{PROJECT_NAME}} --help
```

### Adding New Commands

1. **Create command file** in `app/commands/`:

```python
# app/commands/mycommand.py
import click
from rich.console import Console

console = Console()

@click.group()
def mycommand():
    """My new command group."""
    pass

@mycommand.command()
@click.argument("name")
def hello(name: str):
    """Say hello."""
    console.print(f"[green]Hello {name}![/green]")
```

2. **Register in** `app/cli.py`:

```python
from app.commands.mycommand import mycommand

cli.add_command(mycommand)
```

3. **Use it**:

```bash
{{PROJECT_NAME}} mycommand hello Alice
```

### Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app

# Test a specific command
uv run pytest tests/test_commands.py::test_greet -v
```

### Code Quality

```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format .

# Type checking
uv run mypy app/
```

## Rich Features

### Tables

```python
from rich.table import Table
from rich.console import Console

console = Console()

table = Table(title="My Data")
table.add_column("ID", style="cyan")
table.add_column("Name", style="green")
table.add_row("1", "Alice")
table.add_row("2", "Bob")

console.print(table)
```

### Progress Bars

```python
from rich.progress import track
import time

for i in track(range(100), description="Processing..."):
    time.sleep(0.01)
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

### Prompts

```python
from rich.prompt import Confirm, Prompt

name = Prompt.ask("What's your name?")
if Confirm.ask("Continue?"):
    print("Let's go!")
```

### Panels and Trees

```python
from rich.panel import Panel
from rich.tree import Tree
from rich.console import Console

console = Console()

# Panel
console.print(Panel("Hello World", title="Greeting"))

# Tree
tree = Tree("Root")
branch = tree.add("Branch")
branch.add("Leaf 1")
branch.add("Leaf 2")
console.print(tree)
```

## Click Features

### Options and Arguments

```python
@click.command()
@click.option("--count", "-c", default=1, help="Number of times")
@click.option("--name", "-n", prompt="Your name", help="Name")
@click.argument("filename", type=click.Path(exists=True))
def process(count: int, name: str, filename: str):
    """Process a file."""
    pass
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
    pass

@database.command()
def seed():
    """Seed database."""
    pass
```

### Context Passing

```python
@click.group()
@click.option("--verbose", is_flag=True)
@click.pass_context
def cli(ctx, verbose):
    ctx.ensure_object(dict)
    ctx.obj["VERBOSE"] = verbose

@cli.command()
@click.pass_context
def subcommand(ctx):
    if ctx.obj["VERBOSE"]:
        print("Verbose mode enabled")
```

## Configuration

### Environment Variables

Configure via `.env` file:

```env
APP_NAME={{PROJECT_NAME}}
LOG_LEVEL=INFO
OUTPUT_FORMAT=table
```

### Pydantic Settings

```python
from app.core.config import settings

# Access configuration
print(settings.APP_NAME)
print(settings.LOG_LEVEL)
```

## Deployment

### Build Container Image

```bash
docker build -t {{PROJECT_NAME}}:latest .
```

### Run as Container

```bash
# Run CLI in container
docker run --rm {{PROJECT_NAME}}:latest example greet --name Alice

# With environment file
docker run --rm --env-file .env {{PROJECT_NAME}}:latest --help
```

### Package as Executable (PyInstaller)

```bash
# Install PyInstaller
uv add --dev pyinstaller

# Build executable
uv run pyinstaller --onefile --name {{PROJECT_NAME}} app/cli.py

# Executable in dist/
./dist/{{PROJECT_NAME}} --help
```

## Examples

### Simple Greeting

```bash
$ {{PROJECT_NAME}} example greet --name Alice --count 2
Hello Alice! (#1)
Hello Alice! (#2)
```

### Display Table

```bash
$ {{PROJECT_NAME}} example table --rows 5
┏━━━━┳━━━━━━━━┳━━━━━━━━━━┳━━━━━━━┓
┃ ID ┃ Name   ┃ Status   ┃ Value ┃
┡━━━━╇━━━━━━━━╇━━━━━━━━━━╇━━━━━━━┩
│  1 │ Item 1 │ ✅ Active │  $100 │
│  2 │ Item 2 │ ⏸️ Pending │  $200 │
│  3 │ Item 3 │ ❌ Inactive│  $300 │
│  4 │ Item 4 │ ✅ Active │  $400 │
│  5 │ Item 5 │ ⏸️ Pending │  $500 │
└────┴────────┴──────────┴───────┘
```

### Progress Bar

```bash
$ {{PROJECT_NAME}} example progress --items 20
Processing... ━━━━━━━━━━━━━━━━━━━━ 100% 0:00:02

✓ Complete!
```

## Common Patterns

### API Client

```python
import httpx
from rich.console import Console

console = Console()

@click.command()
@click.argument("endpoint")
def fetch(endpoint: str):
    """Fetch data from API."""
    with console.status("[bold green]Fetching data..."):
        response = httpx.get(f"https://api.example.com/{endpoint}")
        data = response.json()
    
    console.print_json(data=data)
```

### File Processing

```python
@click.command()
@click.argument("input_file", type=click.File("r"))
@click.argument("output_file", type=click.File("w"))
def transform(input_file, output_file):
    """Transform input file to output file."""
    data = input_file.read()
    # Process data
    output_file.write(data.upper())
```

### Error Handling

```python
from rich.console import Console

console = Console()

try:
    result = risky_operation()
except Exception as e:
    console.print(f"[bold red]Error:[/bold red] {e}")
    raise click.Abort()
```

## License

[Your License Here]
