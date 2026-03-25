#!/usr/bin/env python3
"""
Python CLI Scaffolder

Creates a beautiful CLI tool project with:
- Click for CLI framework
- Rich for beautiful terminal output
- Structured JSONL logging
- Docker support (optional)
"""

import sys
from pathlib import Path


def create_directory_structure(base_path: Path, project_name: str) -> dict[str, Path]:
    """Create the CLI project directory structure."""
    
    paths = {
        "root": base_path / project_name,
        "app": base_path / project_name / "app",
        "app_commands": base_path / project_name / "app" / "commands",
        "app_core": base_path / project_name / "app" / "core",
        "tests": base_path / project_name / "tests",
    }
    
    for path in paths.values():
        path.mkdir(parents=True, exist_ok=True)
        
    return paths


def copy_and_process_template(
    template_path: Path,
    target_path: Path,
    project_name: str,
    description: str
):
    """Copy a template file and replace placeholders."""
    if template_path.exists():
        content = template_path.read_text()
        content = content.replace("{{PROJECT_NAME}}", project_name)
        content = content.replace("{{DESCRIPTION}}", description)
        target_path.write_text(content)
        return True
    return False


def scaffold_project(
    project_name: str,
    description: str = "",
    base_path: Path | None = None
):
    """Create a complete CLI project scaffold."""
    
    if base_path is None:
        base_path = Path.cwd()
    
    print(f"🚀 Creating CLI project: {project_name}")
    
    # Create directory structure
    paths = create_directory_structure(base_path, project_name)
    
    # Get path to skill assets directory
    skill_dir = Path(__file__).parent.parent / "assets"
    
    if not skill_dir.exists():
        print(f"❌ Error: Assets directory not found at {skill_dir}")
        sys.exit(1)
    
    # Template mappings
    templates = {
        # Root level files
        "pyproject.toml": paths["root"] / "pyproject.toml",
        "Dockerfile": paths["root"] / "Dockerfile",
        ".env.example": paths["root"] / ".env.example",
        ".gitignore": paths["root"] / ".gitignore",
        "README.md": paths["root"] / "README.md",
        
        # App files
        "app/__init__.py": paths["app"] / "__init__.py",
        "app/cli.py": paths["app"] / "cli.py",
        "app/core/__init__.py": paths["app_core"] / "__init__.py",
        "app/core/config.py": paths["app_core"] / "config.py",
        "app/core/logging.py": paths["app_core"] / "logging.py",
        "app/commands/__init__.py": paths["app_commands"] / "__init__.py",
        "app/commands/example.py": paths["app_commands"] / "example.py",
        
        # Test files
        "tests/__init__.py": paths["tests"] / "__init__.py",
        "tests/test_commands.py": paths["tests"] / "test_commands.py",
    }
    
    # Copy and process templates
    for template_name, target_path in templates.items():
        template_path = skill_dir / template_name
        if copy_and_process_template(template_path, target_path, project_name, description):
            rel_path = target_path.relative_to(paths["root"])
            print(f"  ✅ Created {rel_path}")
        else:
            print(f"  ⚠️  Template not found: {template_name}")
    
    print(f"\n✨ Project '{project_name}' created successfully!")
    print(f"\n📁 Project location: {paths['root']}")
    print(f"\n🚀 Next steps:")
    print(f"  cd {project_name}")
    print(f"  ")
    print(f"  # Install dependencies:")
    print(f"  uv sync")
    print(f"  ")
    print(f"  # Install CLI in development mode:")
    print(f"  uv pip install -e .")
    print(f"  ")
    print(f"  # Run CLI:")
    print(f"  {project_name} --help")
    print(f"  {project_name} example greet --name Alice")
    print(f"  ")
    print(f"  # Or run without installation:")
    print(f"  uv run python -m app.cli --help")
    print(f"\n📚 See README.md for more examples and patterns!")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: scaffold.py <project-name> [description]")
        print("\nExample:")
        print("  scaffold.py my-tool 'A beautiful CLI tool'")
        sys.exit(1)
    
    project_name = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else ""
    
    # Validate project name
    if not project_name.replace("-", "").replace("_", "").isalnum():
        print("❌ Error: Project name must contain only letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    # Check if directory already exists
    if (Path.cwd() / project_name).exists():
        print(f"❌ Error: Directory '{project_name}' already exists")
        sys.exit(1)
    
    scaffold_project(project_name, description)


if __name__ == "__main__":
    main()
