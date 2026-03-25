#!/usr/bin/env python3
"""
List available Copier templates from the registry.

This script reads the templates.md reference file and displays
available project types.
"""
import re
from pathlib import Path


def parse_templates_table(templates_md_path: Path) -> list[tuple[str, str, str]]:
    """
    Parse the templates table from templates.md.
    
    Returns:
        List of (project_type, template_url, description) tuples
    """
    content = templates_md_path.read_text()
    
    # Find the table section
    in_table = False
    templates = []
    
    for line in content.split('\n'):
        # Skip header and separator rows
        if line.startswith('| Project Type'):
            in_table = True
            continue
        if line.startswith('|---'):
            continue
        if not line.startswith('|'):
            if in_table:
                break
            continue
            
        if in_table:
            # Parse table row
            parts = [p.strip() for p in line.split('|')[1:-1]]
            if len(parts) == 3 and parts[0] and parts[1] != 'TBD':
                templates.append((parts[0], parts[1], parts[2]))
    
    return templates


def main():
    """Display available templates."""
    skill_root = Path(__file__).parent.parent
    templates_file = skill_root / "references" / "templates.md"
    
    if not templates_file.exists():
        print(f"Error: templates.md not found at {templates_file}")
        return 1
    
    templates = parse_templates_table(templates_file)
    
    if not templates:
        print("No templates configured yet.")
        print(f"Edit {templates_file} to add template URLs.")
        return 1
    
    print("Available Project Types:")
    print()
    
    max_type_len = max(len(t[0]) for t in templates)
    
    for project_type, template_url, description in templates:
        print(f"  {project_type:<{max_type_len}}  {description}")
        print(f"  {' ' * max_type_len}  → {template_url}")
        print()
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
