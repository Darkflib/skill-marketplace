#!/usr/bin/env python3
"""
Copier bootstrap script for consistent project creation.

Usage:
    # Interactive mode with defaults
    python run_copier.py <template-url> <destination-path>
    
    # With answers file
    python run_copier.py <template-url> <destination-path> --answers-file answers.yml
    
    # With inline answers
    python run_copier.py <template-url> <destination-path> --data key=value
"""
import subprocess
import sys
from pathlib import Path


def run_copier(
    template: str,
    destination: str,
    answers_file: str | None = None,
    trust: bool = True,
    defaults: bool = True,
    data: dict | None = None,
) -> int:
    """
    Run copier with specified arguments.
    
    Args:
        template: Template URL or path
        destination: Destination directory path
        answers_file: Optional path to YAML answers file
        trust: Trust template (allows Jinja extensions)
        defaults: Use default answers for all questions
        data: Optional dict of inline answer data
        
    Returns:
        Exit code from copier command
    """
    cmd = ["copier", "copy"]
    
    if trust:
        cmd.append("--trust")
    
    if defaults:
        cmd.append("--defaults")
    
    if answers_file:
        cmd.extend(["--answers-file", answers_file])
    
    if data:
        for key, value in data.items():
            cmd.extend(["--data", f"{key}={value}"])
    
    cmd.extend([template, destination])
    
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    """CLI entry point."""
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    template = sys.argv[1]
    destination = sys.argv[2]
    
    # Parse optional arguments
    answers_file = None
    data = {}
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] == "--answers-file" and i + 1 < len(sys.argv):
            answers_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--data" and i + 1 < len(sys.argv):
            key_value = sys.argv[i + 1]
            if "=" in key_value:
                key, value = key_value.split("=", 1)
                data[key] = value
            i += 2
        else:
            i += 1
    
    exit_code = run_copier(
        template=template,
        destination=destination,
        answers_file=answers_file,
        data=data if data else None,
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
