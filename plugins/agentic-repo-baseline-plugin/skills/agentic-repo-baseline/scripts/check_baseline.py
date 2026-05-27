#!/usr/bin/env python3
"""Inventory a repo for agentic baseline files and report what's present/missing.

Produces a JSON report (or text, with --format text) covering:
- Presence of README.md, AGENTS.md, WORKLOG.md, CHANGELOG.md
- .gitignore presence
- Detected languages (python, node)
- Language-specific tooling state
- Git status (is it a repo, does it have any commits)

Exits 0 on success, 2 on bad input.
"""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger("check_baseline")

BASELINE_FILES = ["README.md", "AGENTS.md", "WORKLOG.md", "CHANGELOG.md"]

# Glob patterns that indicate a given language is in use.
# All patterns are matched recursively (rglob), skipping SKIP_DIRS.
# `*.js` and `*.mjs` are deliberately omitted from NODE_INDICATORS — they leak
# too easily (docs sites, stray scripts). `package.json`, `*.ts`, `*.tsx`,
# `*.jsx` are stronger Node/React signals.
PYTHON_INDICATORS = ("*.py", "pyproject.toml", "requirements.txt", "setup.py", "setup.cfg")
NODE_INDICATORS = ("package.json", "*.ts", "*.tsx", "*.jsx")

# Directories to skip when looking for language indicators — these typically
# contain dependency or build artefacts that would give false positives.
SKIP_DIRS = {".git", ".venv", "venv", "env", "node_modules", "__pycache__",
             ".mypy_cache", ".ruff_cache", ".pytest_cache", "dist", "build", ".next",
             ".turbo", ".parcel-cache", ".svelte-kit", ".vite", "site-packages"}


def _exists(repo: Path, names: list[str]) -> dict[str, bool]:
    """Return a dict mapping each name to whether it exists as a regular file."""
    return {name: (repo / name).is_file() for name in names}


def _has_any(repo: Path, patterns: tuple[str, ...]) -> bool:
    """Check whether any file matching one of these patterns exists in the repo.

    All patterns are matched recursively via rglob, with matches inside SKIP_DIRS
    excluded. This means `package.json` matches at any depth, not just the root —
    important for monorepos with frontend/ and backend/ subdirectories.
    """
    for pattern in patterns:
        try:
            for match in repo.rglob(pattern):
                # Skip matches inside excluded directories.
                rel_parts = match.relative_to(repo).parts[:-1]
                if any(part in SKIP_DIRS for part in rel_parts):
                    continue
                return True
        except OSError as exc:
            logger.debug("rglob failed for %s: %s", pattern, exc)
            continue
    return False


def _detect_languages(repo: Path) -> list[str]:
    """Return a list of detected languages, in alphabetical order for stability."""
    langs: list[str] = []
    if _has_any(repo, PYTHON_INDICATORS):
        langs.append("python")
    if _has_any(repo, NODE_INDICATORS):
        langs.append("node")
    return langs


def _git_status(repo: Path) -> dict[str, Any]:
    """Inspect git state — whether it's a repo and whether it has any commits."""
    status: dict[str, Any] = {"is_repo": False, "has_commits": False}
    if not (repo / ".git").exists():
        return status
    status["is_repo"] = True
    try:
        proc = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        status["has_commits"] = proc.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError) as exc:
        logger.warning("git inspection failed: %s", exc)
    return status


def _find_paths(repo: Path, pattern: str) -> list[str]:
    """Return relative paths to all matches of pattern, skipping SKIP_DIRS."""
    paths: list[str] = []
    try:
        for match in repo.rglob(pattern):
            rel_parts = match.relative_to(repo).parts[:-1]
            if any(part in SKIP_DIRS for part in rel_parts):
                continue
            paths.append(str(match.relative_to(repo)))
    except OSError as exc:
        logger.debug("rglob failed for %s: %s", pattern, exc)
    return sorted(paths)


def _python_tooling(repo: Path) -> dict[str, Any]:
    """Check for Python-specific tooling files and config.

    Reports root-level presence plus locations of any pyproject.toml found
    anywhere in the tree (useful for monorepos with sub-packages).
    """
    pyproject = repo / "pyproject.toml"
    pyproject_locations = _find_paths(repo, "pyproject.toml")
    info: dict[str, Any] = {
        "pyproject_toml_at_root": pyproject.is_file(),
        "pyproject_toml_locations": pyproject_locations,
        "python_version_file": (repo / ".python-version").is_file(),
        "ruff_configured": False,
        "mypy_configured": False,
    }
    # Check ruff/mypy config in the root pyproject.toml; we don't recurse into
    # sub-packages for this — sub-packages can have their own conventions.
    if pyproject.is_file():
        try:
            content = pyproject.read_text(encoding="utf-8")
            # Cheap and cheerful — a full TOML parse would be more correct but
            # we just want to know whether these sections exist.
            info["ruff_configured"] = "[tool.ruff" in content
            info["mypy_configured"] = "[tool.mypy" in content
        except OSError as exc:
            logger.warning("could not read %s: %s", pyproject, exc)
    return info


def _node_tooling(repo: Path) -> dict[str, Any]:
    """Check for Node-specific tooling files.

    Reports root-level presence plus locations of any package.json found
    anywhere in the tree (useful for monorepos with frontend/ subdirs).
    """
    package_json_locations = _find_paths(repo, "package.json")
    return {
        "package_json_at_root": (repo / "package.json").is_file(),
        "package_json_locations": package_json_locations,
        "lockfile_at_root": any(
            (repo / lf).is_file()
            for lf in ("package-lock.json", "pnpm-lock.yaml", "yarn.lock", "bun.lockb")
        ),
    }


def inventory(repo: Path) -> dict[str, Any]:
    """Build the inventory report for a given repo path."""
    if not repo.exists():
        raise ValueError(f"path does not exist: {repo}")
    if not repo.is_dir():
        raise ValueError(f"not a directory: {repo}")

    languages = _detect_languages(repo)
    report: dict[str, Any] = {
        "repo_path": str(repo.resolve()),
        "baseline_files": _exists(repo, BASELINE_FILES),
        "gitignore_present": (repo / ".gitignore").is_file(),
        "languages_detected": languages,
        "git": _git_status(repo),
    }
    if "python" in languages:
        report["python_tooling"] = _python_tooling(repo)
    if "node" in languages:
        report["node_tooling"] = _node_tooling(repo)
    return report


def _print_text(report: dict[str, Any]) -> None:
    """Human-readable rendering of the report."""
    print(f"Repo: {report['repo_path']}")
    print()
    print("Baseline files:")
    for name, present in report["baseline_files"].items():
        marker = "[OK]" if present else "[--]"
        print(f"  {marker} {name}")
    print()
    print(f"  {'[OK]' if report['gitignore_present'] else '[--]'} .gitignore")
    print()
    langs = report["languages_detected"]
    print(f"Languages detected: {', '.join(langs) if langs else '(none)'}")
    git = report["git"]
    print(f"Git: repo={git['is_repo']}, commits={git['has_commits']}")

    if "python_tooling" in report:
        print()
        print("Python tooling:")
        pt = report["python_tooling"]
        print(f"  {'[OK]' if pt['pyproject_toml_at_root'] else '[--]'} pyproject.toml at root")
        if pt["pyproject_toml_locations"]:
            print(f"       found at: {', '.join(pt['pyproject_toml_locations'])}")
        print(f"  {'[OK]' if pt['python_version_file'] else '[--]'} .python-version")
        print(f"  {'[OK]' if pt['ruff_configured'] else '[--]'} [tool.ruff] in root pyproject")
        print(f"  {'[OK]' if pt['mypy_configured'] else '[--]'} [tool.mypy] in root pyproject")

    if "node_tooling" in report:
        print()
        print("Node tooling:")
        nt = report["node_tooling"]
        print(f"  {'[OK]' if nt['package_json_at_root'] else '[--]'} package.json at root")
        if nt["package_json_locations"]:
            print(f"       found at: {', '.join(nt['package_json_locations'])}")
        print(f"  {'[OK]' if nt['lockfile_at_root'] else '[--]'} lockfile at root")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_path", type=Path, help="Path to the repository root")
    parser.add_argument(
        "--format",
        choices=["json", "text"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Emit debug logs to stderr",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.WARNING,
        format="%(levelname)s: %(message)s",
    )

    try:
        report = inventory(args.repo_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # noqa: BLE001 — surface any unexpected error
        logger.exception("inventory failed")
        print(f"error: unexpected failure: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        _print_text(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
