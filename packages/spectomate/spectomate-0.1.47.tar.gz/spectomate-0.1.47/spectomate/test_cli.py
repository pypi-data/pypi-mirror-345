"""
CLI commands for testing and code quality checks.
"""

import sys
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group(name="test")
def test_cli() -> None:
    """Commands for testing and code quality checks."""
    pass


@test_cli.command("black")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--check", is_flag=True, help="Only check formatting without modifying files"
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def black_command(paths: List[str], check: bool, verbose: bool) -> None:
    """Run black code formatter on specified paths."""
    import subprocess

    from rich.panel import Panel

    if not paths:
        paths = ["."]

    console.print(Panel("Running black code formatter", style="blue"))

    cmd = ["black"]
    if check:
        cmd.append("--check")
    if verbose:
        cmd.append("--verbose")
    cmd.extend(paths)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            console.print("[green]Code formatting check passed![/green]")
        else:
            console.print("[yellow]Code formatting issues found:[/yellow]")
            console.print(result.stdout)
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error running black: {e}[/red]")
        sys.exit(1)


@test_cli.command("isort")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option(
    "--check", is_flag=True, help="Only check import sorting without modifying files"
)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def isort_command(paths: List[str], check: bool, verbose: bool) -> None:
    """Run isort import sorter on specified paths."""
    import subprocess

    from rich.panel import Panel

    if not paths:
        paths = ["."]

    console.print(Panel("Running isort import sorter", style="blue"))

    cmd = ["isort"]
    if check:
        cmd.append("--check-only")
    if verbose:
        cmd.append("--verbose")
    cmd.extend(["--profile", "black"])
    cmd.extend(paths)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode == 0:
            console.print("[green]Import sorting check passed![/green]")
        else:
            console.print("[yellow]Import sorting issues found:[/yellow]")
            console.print(result.stdout)
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error running isort: {e}[/red]")
        sys.exit(1)


@test_cli.command("flake8")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def flake8_command(paths: List[str], verbose: bool) -> None:
    """Run flake8 linting on specified paths."""
    import subprocess

    from rich.panel import Panel

    if not paths:
        paths = ["."]

    console.print(Panel("Running flake8 linting", style="blue"))

    # Run flake8 for syntax errors and undefined names
    cmd = [
        "flake8",
        "--count",
        "--select=E9,F63,F7,F82",
        "--show-source",
        "--statistics",
    ]
    cmd.extend(paths)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            console.print("[red]Critical linting errors found:[/red]")
            console.print(result.stdout)
            sys.exit(1)

        # Run flake8 for warnings (exit-zero)
        cmd = [
            "flake8",
            "--count",
            "--exit-zero",
            "--max-complexity=10",
            "--max-line-length=127",
            "--statistics",
        ]
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.stdout.strip() and verbose:
            console.print("[yellow]Linting warnings found (non-critical):[/yellow]")
            console.print(result.stdout)

        console.print("[green]Flake8 checks passed![/green]")
    except Exception as e:
        console.print(f"[red]Error running flake8: {e}[/red]")
        sys.exit(1)


@test_cli.command("pytest")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
@click.option("--coverage", "-c", is_flag=True, help="Run with coverage report")
def pytest_command(paths: List[str], verbose: bool, coverage: bool) -> None:
    """Run pytest unit tests on specified paths."""
    import subprocess

    from rich.panel import Panel

    if not paths:
        paths = ["."]

    console.print(Panel("Running pytest unit tests", style="blue"))

    cmd = ["pytest"]

    if verbose:
        cmd.append("-v")

    if coverage:
        cmd.extend(["--cov", "--cov-report", "term"])

    cmd.extend(paths)

    try:
        result = subprocess.run(cmd, capture_output=False, text=True, check=False)

        if result.returncode != 0:
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error running pytest: {e}[/red]")
        sys.exit(1)


@test_cli.command("all")
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
@click.option("--fix", is_flag=True, help="Fix issues automatically where possible")
@click.option("--skip-lint", is_flag=True, help="Skip linting checks")
@click.option("--skip-tests", is_flag=True, help="Skip unit tests")
@click.option("--skip-mypy", is_flag=True, help="Skip mypy type checking")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def test_all_command(
    paths: List[str],
    fix: bool,
    skip_lint: bool,
    skip_tests: bool,
    skip_mypy: bool,
    verbose: bool,
) -> None:
    """Run all tests and code quality checks."""
    import subprocess

    from rich.panel import Panel

    if not paths:
        paths = ["."]

    results = {}

    console.print(Panel("Running all tests and code quality checks", style="blue"))

    if not skip_lint:
        # Run black
        console.print("\n[bold]Running black code formatter...[/bold]")
        cmd = ["black"]
        if not fix:
            cmd.append("--check")
        if verbose:
            cmd.append("--verbose")
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results["black"] = {
            "success": result.returncode == 0,
            "message": (
                "Code formatting passed"
                if result.returncode == 0
                else "Code formatting issues found"
            ),
        }

        # Run isort
        console.print("\n[bold]Running isort import sorter...[/bold]")
        cmd = ["isort"]
        if not fix:
            cmd.append("--check-only")
        if verbose:
            cmd.append("--verbose")
        cmd.extend(["--profile", "black"])
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results["isort"] = {
            "success": result.returncode == 0,
            "message": (
                "Import sorting passed"
                if result.returncode == 0
                else "Import sorting issues found"
            ),
        }

        # Run flake8
        console.print("\n[bold]Running flake8 linting...[/bold]")
        cmd = [
            "flake8",
            "--count",
            "--select=E9,F63,F7,F82",
            "--show-source",
            "--statistics",
        ]
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results["flake8"] = {
            "success": result.returncode == 0,
            "message": (
                "Flake8 checks passed"
                if result.returncode == 0
                else "Critical linting errors found"
            ),
        }

    if not skip_mypy:
        # Run mypy
        console.print("\n[bold]Running mypy type checking...[/bold]")
        cmd = ["mypy", "--ignore-missing-imports"]
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results["mypy"] = {
            "success": result.returncode == 0,
            "message": (
                "Type checking passed"
                if result.returncode == 0
                else "Type checking issues found"
            ),
        }

    if not skip_tests:
        # Run pytest
        console.print("\n[bold]Running pytest unit tests...[/bold]")
        cmd = ["pytest"]
        if verbose:
            cmd.append("-v")
        cmd.extend(paths)

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        results["pytest"] = {
            "success": result.returncode == 0,
            "message": (
                "Unit tests passed" if result.returncode == 0 else "Unit tests failed"
            ),
        }

    # Display summary
    console.print("\n[bold]Test Summary:[/bold]")
    table = Table(show_header=True, header_style="bold")
    table.add_column("Test")
    table.add_column("Status")
    table.add_column("Message")

    all_success = True

    for test_name, result in results.items():
        status = "[green]PASS[/green]" if result["success"] else "[red]FAIL[/red]"
        table.add_row(test_name, status, result["message"])
        if not result["success"]:
            all_success = False

    console.print(table)

    if not all_success:
        console.print("[red]Some tests failed![/red]")
        sys.exit(1)
    else:
        console.print("[green]All tests passed![/green]")
