"""
CLI commands for Git operations in Spectomate.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click


def run_command(cmd: List[str], cwd: Optional[str] = None) -> int:
    """Run a command in a subprocess and return the exit code."""
    try:
        process = subprocess.run(
            cmd,
            cwd=cwd,
            check=False,
        )
        return process.returncode
    except subprocess.SubprocessError as e:
        click.echo(f"Error running command: {e}", err=True)
        return 1


def get_project_root() -> Path:
    """Get the project root directory."""
    # Try to find the project root by looking for .git directory
    current_dir = Path.cwd()
    while current_dir != current_dir.parent:
        if (current_dir / ".git").exists():
            return current_dir
        current_dir = current_dir.parent

    # If not found, use the current directory
    return Path.cwd()


@click.group()
def git_cli():
    """Commands for Git operations."""
    pass


@git_cli.command("submodules")
@click.option(
    "--auto-fix", "-a", is_flag=True, help="Automatically fix detected issues"
)
@click.option("--ignore", "-i", multiple=True, help="Directories to ignore")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def submodules_command(auto_fix: bool, ignore: List[str], verbose: bool):
    """Detect and fix Git submodule issues.

    This command checks for directories that might be Git repositories but aren't properly
    configured as submodules, and helps set them up correctly.

    Examples:
        spectomate git submodules              # Check for submodule issues
        spectomate git submodules --auto-fix   # Automatically fix detected issues
        spectomate git submodules --ignore venv --ignore node_modules  # Ignore specific directories
    """
    # Find the scripts directory
    scripts_dir = Path(__file__).parent.parent / "scripts"
    fix_submodules_script = scripts_dir / "fix_submodules.py"

    if not fix_submodules_script.exists():
        click.echo(
            f"Error: Submodule fix script not found at {fix_submodules_script}",
            err=True,
        )
        sys.exit(1)

    # Build the command
    cmd = ["python", str(fix_submodules_script)]

    # Add the repository path
    repo_path = get_project_root()
    cmd.extend(["--repo", str(repo_path)])

    # Add auto-fix flag if specified
    if auto_fix:
        cmd.append("--auto-fix")

    # Add ignore directories
    for dir_name in ignore:
        cmd.extend(["--ignore", dir_name])

    # Run the command
    click.echo(f"Checking for submodule issues in {repo_path}...")
    exit_code = run_command(cmd)

    if exit_code != 0:
        click.echo("Failed to check for submodule issues", err=True)
        sys.exit(exit_code)
