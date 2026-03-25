#!/usr/bin/env python3
"""
FastAPI Project Scaffolder

Creates a modern Python project structure with:
- UV for package management
- FastAPI for web framework
- Pydantic for configuration
- Docker support
- K8s/Cloud Run deployment templates
- Testing and linting setup
"""

import os
import shutil
import sys
from pathlib import Path


def create_directory_structure(base_path: Path, project_name: str) -> dict[str, Path]:
    """Create the standard project directory structure."""
    
    paths = {
        "root": base_path / project_name,
        "app": base_path / project_name / "app",
        "app_api": base_path / project_name / "app" / "api",
        "app_core": base_path / project_name / "app" / "core",
        "app_models": base_path / project_name / "app" / "models",
        "app_services": base_path / project_name / "app" / "services",
        "tests": base_path / project_name / "tests",
        "tests_unit": base_path / project_name / "tests" / "unit",
        "tests_integration": base_path / project_name / "tests" / "integration",
        "deploy": base_path / project_name / "deploy",
        "deploy_k8s": base_path / project_name / "deploy" / "k8s",
        "scripts": base_path / project_name / "scripts",
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
        # Replace placeholders
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
    """Create a complete FastAPI project scaffold."""
    
    if base_path is None:
        base_path = Path.cwd()
    
    print(f"🚀 Creating FastAPI project: {project_name}")
    
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
        "docker-compose.yml": paths["root"] / "docker-compose.yml",
        ".env.example": paths["root"] / ".env.example",
        ".gitignore": paths["root"] / ".gitignore",
        "README.md": paths["root"] / "README.md",
        
        # App files
        "app/__init__.py": paths["app"] / "__init__.py",
        "app/main.py": paths["app"] / "main.py",
        "app/core/__init__.py": paths["app_core"] / "__init__.py",
        "app/core/config.py": paths["app_core"] / "config.py",
        "app/api/__init__.py": paths["app_api"] / "__init__.py",
        "app/api/routes.py": paths["app_api"] / "routes.py",
        "app/models/__init__.py": paths["app_models"] / "__init__.py",
        "app/services/__init__.py": paths["app_services"] / "__init__.py",
        
        # Test files
        "tests/__init__.py": paths["tests"] / "__init__.py",
        "tests/conftest.py": paths["tests"] / "conftest.py",
        
        # Deployment files
        "deploy/k8s/deployment.yaml": paths["deploy_k8s"] / "deployment.yaml",
        "deploy/k8s/service.yaml": paths["deploy_k8s"] / "service.yaml",
    }
    
    # Copy and process templates
    for template_name, target_path in templates.items():
        template_path = skill_dir / template_name
        if copy_and_process_template(template_path, target_path, project_name, description):
            rel_path = target_path.relative_to(paths["root"])
            print(f"  ✅ Created {rel_path}")
        else:
            print(f"  ⚠️  Template not found: {template_name}")
    
    # Create __init__.py for test subdirectories
    (paths["tests_unit"] / "__init__.py").touch()
    (paths["tests_integration"] / "__init__.py").touch()
    
    print(f"\n✨ Project '{project_name}' created successfully!")
    print(f"\n📁 Project location: {paths['root']}")
    print(f"\n🚀 Next steps:")
    print(f"  cd {project_name}")
    print(f"  uv sync                              # Install dependencies")
    print(f"  cp .env.example .env                 # Configure environment")
    print(f"  uv run uvicorn app.main:app --reload # Start dev server")
    print(f"\n📚 Documentation:")
    print(f"  API docs: http://localhost:8000/docs")
    print(f"  Health check: http://localhost:8000/health")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: scaffold.py <project-name> [description]")
        print("\nExample:")
        print("  scaffold.py my-api 'A cool API service'")
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
