"""
Command-line interface for mypy helper tools.

This module provides CLI commands to help users identify and fix mypy issues.
"""

import os
from pathlib import Path
from typing import Optional

import click
from rich.console import Console

from spectomate.core.mypy_helper import (
    add_type_ignore_comments,
    apply_monkeytype,
    create_mypy_config,
    display_mypy_issues,
    fix_common_mypy_issues,
    generate_stubs_for_module,
    run_mypy,
)

# Initialize rich console
console = Console()


@click.group()
def mypy_cli():
    """Tools to help with mypy type checking issues."""
    pass


@mypy_cli.command("check")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--config", "-c", type=click.Path(exists=True), help="Path to mypy config file"
)
@click.option("--strict", is_flag=True, help="Run mypy in strict mode")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.option(
    "--ignore-missing-imports/--no-ignore-missing-imports",
    default=True,
    help="Ignore missing imports (default: True)",
)
def check_command(
    path: str,
    config: Optional[str],
    strict: bool,
    verbose: bool,
    ignore_missing_imports: bool,
):
    """Run mypy and display issues with suggested fixes."""
    success, issues = run_mypy(
        target_path=path,
        config_file=config,
        strict=strict,
        verbose=verbose,
        ignore_missing_imports=ignore_missing_imports,
    )

    if success:
        console.print("[green]No mypy issues found![/green]")
    else:
        display_mypy_issues(issues, verbose=verbose)


@mypy_cli.command("fix")
@click.argument("path", type=click.Path(exists=True))
@click.option("--auto", is_flag=True, help="Automatically apply fixes where possible")
@click.option(
    "--interactive", "-i", is_flag=True, help="Interactively prompt for fixes"
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def fix_command(path: str, auto: bool, interactive: bool, verbose: bool):
    """Attempt to fix common mypy issues."""
    if not auto and not interactive:
        interactive = True  # Default to interactive mode if neither is specified

    fixed = fix_common_mypy_issues(
        target_path=path, auto_fix=auto, interactive=interactive, verbose=verbose
    )

    if fixed:
        console.print("[green]All mypy issues fixed![/green]")
    else:
        console.print(
            "[yellow]Some mypy issues could not be fixed automatically.[/yellow]"
        )


@mypy_cli.command("ignore")
@click.argument("path", type=click.Path(exists=True))
@click.option(
    "--selective",
    "-s",
    is_flag=True,
    help="Only add ignores for certain types of issues",
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def ignore_command(path: str, selective: bool, verbose: bool):
    """Add # type: ignore comments to lines with mypy issues."""
    # First run mypy to get issues
    success, issues = run_mypy(target_path=path, verbose=verbose)

    if success:
        console.print("[green]No mypy issues found![/green]")
        return

    # Add type: ignore comments
    comments_added = add_type_ignore_comments(
        target_path=path, issues=issues, selective=selective
    )

    console.print(f"[green]Added {comments_added} type: ignore comments[/green]")


@mypy_cli.command("stubs")
@click.argument("module_name")
@click.option("--output", "-o", type=click.Path(), help="Output directory for stubs")
def stubs_command(module_name: str, output: Optional[str]):
    """Generate stub files for a module."""
    output_path = Path(output) if output else None
    success = generate_stubs_for_module(module_name, output_path)

    if success:
        console.print(f"[green]Successfully generated stubs for {module_name}[/green]")
    else:
        console.print(f"[red]Failed to generate stubs for {module_name}[/red]")


@mypy_cli.command("monkeytype")
@click.argument("script_path", type=click.Path(exists=True))
@click.option("--module", "-m", help="Module name to apply types to")
@click.option("--apply", is_flag=True, help="Apply the generated types")
def monkeytype_command(script_path: str, module: Optional[str], apply: bool):
    """Run monkeytype on a script to generate type annotations."""
    success = apply_monkeytype(script_path=script_path, module_name=module, apply=apply)

    if success and not apply:
        console.print("[green]Successfully ran script with monkeytype[/green]")
        console.print("To apply the generated types, run:")
        console.print(
            f"  spectomate mypy monkeytype {script_path} --module {module or 'MODULE_NAME'} --apply"
        )


@mypy_cli.command("config")
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--strict", is_flag=True, help="Enable strict mode")
@click.option(
    "--ignore-missing-imports",
    is_flag=True,
    default=True,
    help="Ignore missing imports",
)
@click.option(
    "--disallow-untyped-defs",
    is_flag=True,
    help="Disallow untyped function definitions",
)
@click.option(
    "--disallow-incomplete-defs",
    is_flag=True,
    help="Disallow incomplete function definitions",
)
def config_command(
    directory: str,
    strict: bool,
    ignore_missing_imports: bool,
    disallow_untyped_defs: bool,
    disallow_incomplete_defs: bool,
):
    """Create a mypy configuration file."""
    config_path = create_mypy_config(
        target_dir=directory,
        strict=strict,
        ignore_missing_imports=ignore_missing_imports,
        disallow_untyped_defs=disallow_untyped_defs,
        disallow_incomplete_defs=disallow_incomplete_defs,
    )

    console.print(f"[green]Created mypy config file at {config_path}[/green]")


if __name__ == "__main__":
    mypy_cli()
