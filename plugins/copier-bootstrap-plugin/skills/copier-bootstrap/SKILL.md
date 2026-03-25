---
name: copier-bootstrap
description: Bootstrap new projects using Copier templates. Use when the user requests to create a new project, start a new service, or bootstrap from a template. Trigger phrases include "create a new project", "start a new [type] project", "bootstrap a [type]", or "create a new FastAPI/Lambda/CLI/React/etc project". Supports FastAPI services, RabbitMQ workers, CLI tools, React frontends, AWS Lambda functions, and Google Cloud Functions.
---

# Copier Bootstrap Skill

Bootstrap new projects using Copier templates with consistent conventions and proper setup.

## Quick Start

When the user requests a new project:

1. **Determine project type** - Either from explicit request or by offering choices
2. **Consult templates registry** - Read `references/templates.md` to get template URL
3. **Choose destination path** - Confirm or suggest based on project naming
4. **Run copier** - Use `scripts/run_copier.py` with sensible defaults
5. **Read AGENTS.md** - After bootstrapping, read the template's AGENTS.md for conventions
6. **Apply initial customization** - Make any requested changes following template conventions

## Detailed Workflow

### Step 1: Determine Project Type

If the user specifies a project type explicitly (e.g., "Create a new FastAPI project"), proceed directly with that type.

Otherwise, list available project types using `scripts/list_templates.py`:

```bash
python scripts/list_templates.py
```

Present the options and ask the user to choose.

### Step 2: Get Template URL

Read `references/templates.md` to find the template URL for the chosen project type. The file contains a table mapping project types to their template repositories.

### Step 3: Determine Destination Path

Ask the user for the destination path, or suggest a sensible default based on:
- Project type (e.g., `./my-fastapi-service`)
- Any naming conventions the user mentions
- Current working directory context

### Step 4: Bootstrap the Project

Run copier using the provided script:

```bash
python scripts/run_copier.py <template-url> <destination-path>
```

The script automatically:
- Uses `--trust` to allow Jinja extensions
- Uses `--defaults` to accept default answers
- Creates the project with sensible defaults

If the user provides an answers file:

```bash
python scripts/run_copier.py <template-url> <destination-path> --answers-file answers.yml
```

If the user wants to override specific values:

```bash
python scripts/run_copier.py <template-url> <destination-path> --data project_name=my-service --data author=Mike
```

### Step 5: Read Template Conventions

After successful bootstrapping, immediately read the generated project's `AGENTS.md` file:

```bash
cat <destination-path>/AGENTS.md
```

This file contains:
- Project-specific conventions
- Naming patterns
- Architecture guidance
- Development workflows
- Testing approaches

Apply these conventions in any subsequent modifications or additions to the project.

### Step 6: Initial Customization

If the user requested specific customization during creation:
- Follow the conventions from AGENTS.md
- Make changes that align with the template's structure
- Maintain consistency with the template's patterns

## Maintaining Templates

The templates registry is stored in `references/templates.md`. To update:

1. Edit the table to add/modify template URLs
2. Ensure each template has an AGENTS.md file for conventions
3. Test the template by bootstrapping a sample project

## Scripts Reference

### `scripts/run_copier.py`

Main script for running copier with proper arguments.

**Features:**
- Automatic `--trust` flag for Jinja extensions
- Default answers mode for quick bootstrapping
- Support for answers files
- Inline data overrides

### `scripts/list_templates.py`

Display available project types from the registry.

**Usage:**
```bash
python scripts/list_templates.py
```

## Common Patterns

### Quick Bootstrap with Defaults

```bash
# User: "Create a new FastAPI project"
python scripts/list_templates.py  # Verify template exists
python scripts/run_copier.py gh:darkflib/fastapi-template ./my-service
cat ./my-service/AGENTS.md  # Read conventions
```

### Bootstrap with Custom Answers

```bash
# User provides answers file
python scripts/run_copier.py gh:darkflib/fastapi-template ./my-service --answers-file my-answers.yml
```

### Interactive Template Selection

```bash
# User: "Create a new project"
python scripts/list_templates.py  # Show options
# User selects type
python scripts/run_copier.py <template-url> ./my-project
```

## Error Handling

If copier fails:
1. Check that copier is installed: `pip install copier`
2. Verify template URL is accessible
3. Ensure destination path is valid
4. Check for network connectivity (for remote templates)

If AGENTS.md is missing:
- Proceed with generic Python/Node conventions
- Suggest adding AGENTS.md to the template

## Template Requirements

For optimal use, templates should include:
- `AGENTS.md` - Conventions for AI agents
- `copier.yml` - Template configuration
- Sensible defaults for all questions
- Working initial state that can be tested immediately
