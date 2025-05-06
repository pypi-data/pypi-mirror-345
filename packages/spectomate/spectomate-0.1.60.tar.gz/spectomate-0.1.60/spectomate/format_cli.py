#!/usr/bin/env python3
"""
CLI commands for code formatting and style checking.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

import click

from spectomate.core.utils import get_project_root


def run_command(cmd: List[str]) -> int:
    """Run a command and return its exit code."""
    try:
        result = subprocess.run(cmd, check=False)
        return result.returncode
    except Exception as e:
        click.echo(f"Error running command: {e}", err=True)
        return 1


@click.group()
def format_cli():
    """Commands for code formatting and style checking."""
    pass


@format_cli.command("black")
@click.option(
    "--check", is_flag=True, help="Check if files are formatted without changing them"
)
@click.option(
    "--fix-config", is_flag=True, help="Fix Black configuration in pyproject.toml"
)
@click.option("--fix-line-endings", is_flag=True, help="Fix line endings (CRLF -> LF)")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def black_command(
    check: bool,
    fix_config: bool,
    fix_line_endings: bool,
    verbose: bool,
    paths: List[str],
):
    """Format Python code using Black.

    If no paths are specified, the current directory is used.

    Examples:
        spectomate format black              # Format all Python files in the current directory
        spectomate format black --check      # Check formatting without making changes
        spectomate format black --fix-config # Fix Black configuration in pyproject.toml
        spectomate format black src tests    # Format specific directories
    """
    # If no paths are provided, use the current directory
    if not paths:
        paths = ["."]

    # If fix-config is specified, run the fix_black_config script
    if fix_config:
        # Find the scripts directory
        scripts_dir = Path(__file__).parent.parent / "scripts"
        fix_black_config_script = scripts_dir / "fix_black_config.py"

        if not fix_black_config_script.exists():
            click.echo(
                f"Error: Black config fix script not found at {fix_black_config_script}",
                err=True,
            )
            sys.exit(1)

        # Build the command
        cmd = ["python", str(fix_black_config_script)]

        # Add auto-format flag if not in check mode
        if not check:
            cmd.append("--auto-format")

        # Add fix-line-endings flag if specified
        if fix_line_endings:
            cmd.append("--fix-line-endings")

        # Add directory
        cmd.extend(["--directory", str(get_project_root())])

        # Run the command
        if verbose:
            click.echo(f"Running: {' '.join(cmd)}")

        exit_code = run_command(cmd)
        sys.exit(exit_code)

    # Otherwise, run Black directly
    cmd = ["black"]

    # Add check flag if specified
    if check:
        cmd.append("--check")

    # Add verbose flag if specified
    if verbose:
        cmd.append("--verbose")

    # Add paths
    cmd.extend(paths)

    # Run the command
    if verbose:
        click.echo(f"Running: {' '.join(cmd)}")

    exit_code = run_command(cmd)

    # If check mode is on and there are formatting issues, suggest fixing the config
    if check and exit_code != 0:
        click.echo(
            "\nTip: If you're having formatting issues between environments, try:"
        )
        click.echo("  spectomate format black --fix-config")
        click.echo(
            "This will ensure consistent Black configuration across environments."
        )

    sys.exit(exit_code)


@format_cli.command("isort")
@click.option(
    "--check", is_flag=True, help="Check if imports are sorted without changing them"
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def isort_command(check: bool, verbose: bool, paths: List[str]):
    """Sort Python imports using isort.

    If no paths are specified, the current directory is used.

    Examples:
        spectomate format isort              # Sort imports in all Python files
        spectomate format isort --check      # Check import sorting without making changes
        spectomate format isort src tests    # Sort imports in specific directories
    """
    # If no paths are provided, use the current directory
    if not paths:
        paths = ["."]

    # Build the command
    cmd = ["isort"]

    # Add check flag if specified
    if check:
        cmd.append("--check")

    # Add verbose flag if specified
    if verbose:
        cmd.append("--verbose")

    # Add paths
    cmd.extend(paths)

    # Run the command
    if verbose:
        click.echo(f"Running: {' '.join(cmd)}")

    exit_code = run_command(cmd)
    sys.exit(exit_code)


@format_cli.command("all")
@click.option("--check", is_flag=True, help="Check formatting without making changes")
@click.option(
    "--fix-config", is_flag=True, help="Fix formatting configurations in pyproject.toml"
)
@click.option("--fix-line-endings", is_flag=True, help="Fix line endings (CRLF -> LF)")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def format_all_command(
    check: bool,
    fix_config: bool,
    fix_line_endings: bool,
    verbose: bool,
    paths: List[str],
):
    """Run all formatters (isort, black) on the code.

    If no paths are specified, the current directory is used.

    Examples:
        spectomate format all              # Run all formatters
        spectomate format all --check      # Check formatting without making changes
        spectomate format all --fix-config # Fix formatting configurations
        spectomate format all src tests    # Format specific directories
    """
    # If no paths are provided, use the current directory
    if not paths:
        paths = ["."]

    # First run isort
    click.echo("Running isort...")
    cmd = ["isort"]

    # Add check flag if specified
    if check:
        cmd.append("--check")

    # Add verbose flag if specified
    if verbose:
        cmd.append("--verbose")

    # Add paths
    cmd.extend(paths)

    # Run isort
    if verbose:
        click.echo(f"Running: {' '.join(cmd)}")

    isort_exit_code = run_command(cmd)

    # Then run black
    click.echo("\nRunning black...")

    # If fix-config is specified, run the fix_black_config script
    if fix_config:
        # Find the scripts directory
        scripts_dir = Path(__file__).parent.parent / "scripts"
        fix_black_config_script = scripts_dir / "fix_black_config.py"

        if not fix_black_config_script.exists():
            click.echo(
                f"Error: Black config fix script not found at {fix_black_config_script}",
                err=True,
            )
            black_exit_code = 1
        else:
            # Build the command
            cmd = ["python", str(fix_black_config_script)]

            # Add auto-format flag if not in check mode
            if not check:
                cmd.append("--auto-format")

            # Add fix-line-endings flag if specified
            if fix_line_endings:
                cmd.append("--fix-line-endings")

            # Add directory
            cmd.extend(["--directory", str(get_project_root())])

            # Run the command
            if verbose:
                click.echo(f"Running: {' '.join(cmd)}")

            black_exit_code = run_command(cmd)
    else:
        # Run Black directly
        cmd = ["black"]

        # Add check flag if specified
        if check:
            cmd.append("--check")

        # Add verbose flag if specified
        if verbose:
            cmd.append("--verbose")

        # Add paths
        cmd.extend(paths)

        # Run the command
        if verbose:
            click.echo(f"Running: {' '.join(cmd)}")

        black_exit_code = run_command(cmd)

    # Determine overall exit code
    if isort_exit_code != 0 or black_exit_code != 0:
        if check:
            click.echo("\nFormatting issues found. To fix them, run:")
            click.echo("  spectomate format all")
            click.echo(
                "\nIf you're having formatting issues between environments, try:"
            )
            click.echo("  spectomate format all --fix-config")
        sys.exit(1)
    else:
        click.echo("\nAll formatting checks passed!")
        sys.exit(0)
