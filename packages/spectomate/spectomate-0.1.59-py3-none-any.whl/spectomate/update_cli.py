import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import click


def analyze_project_issues() -> Dict[str, Dict[str, Any]]:
    """
    Analyze the project for potential issues that might need addressing during update.

    Returns:
        A dictionary of issue categories and their details
    """
    issues = {
        "tests": {"found": False, "count": 0, "description": ""},
        "lint": {"found": False, "count": 0, "description": ""},
        "mypy": {"found": False, "count": 0, "description": ""},
        "submodules": {"found": False, "count": 0, "description": ""},
        "git": {"found": False, "count": 0, "description": ""},
        "black_config": {"found": False, "count": 0, "description": ""},
    }

    # Check for test issues
    try:
        result = subprocess.run(
            ["pytest", "--collect-only", "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            test_count = (
                len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
            )
            issues["tests"]["found"] = test_count > 0
            issues["tests"]["count"] = test_count
            issues["tests"]["description"] = f"Found {test_count} tests to run"
    except Exception:
        pass

    # Check for lint issues
    try:
        result = subprocess.run(
            ["black", "--check", ".", "--quiet"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Count the number of files that would be reformatted
            files = [
                line
                for line in result.stderr.split("\n")
                if "would be reformatted" in line
            ]
            issues["lint"]["found"] = len(files) > 0
            issues["lint"]["count"] = len(files)
            issues["lint"][
                "description"
            ] = f"Found {len(files)} files with formatting issues"

            # Check if there might be Black configuration issues
            # This happens when local formatting is fine but CI fails
            try:
                # Check if pyproject.toml exists and has Black configuration
                if os.path.exists("pyproject.toml"):
                    with open("pyproject.toml", "r") as f:
                        content = f.read()
                        if "[tool.black]" not in content:
                            issues["black_config"]["found"] = True
                            issues["black_config"]["count"] = 1
                            issues["black_config"][
                                "description"
                            ] = "Missing Black configuration in pyproject.toml"
                        elif (
                            "line-length" not in content
                            or "target-version" not in content
                        ):
                            issues["black_config"]["found"] = True
                            issues["black_config"]["count"] = 1
                            issues["black_config"][
                                "description"
                            ] = "Incomplete Black configuration in pyproject.toml"
            except Exception:
                pass
    except Exception:
        pass

    # Check for mypy issues
    try:
        result = subprocess.run(
            ["mypy", "."],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            # Count the number of error lines
            error_lines = [
                line for line in result.stdout.split("\n") if "error:" in line
            ]
            issues["mypy"]["found"] = len(error_lines) > 0
            issues["mypy"]["count"] = len(error_lines)
            issues["mypy"][
                "description"
            ] = f"Found {len(error_lines)} type checking issues"
    except Exception:
        pass

    # Check for Git submodule issues
    try:
        # Find potential Git repositories that aren't properly configured as submodules
        result = subprocess.run(
            ["find", ".", "-type", "d", "-name", ".git", "-not", "-path", "./.git"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            potential_submodules = [
                path.replace("/.git", "")
                for path in result.stdout.strip().split("\n")
                if path
            ]

            # Check if these are already in .gitmodules
            configured_submodules = []
            if os.path.exists(".gitmodules"):
                with open(".gitmodules", "r") as f:
                    gitmodules_content = f.read()
                    for submodule in potential_submodules:
                        rel_path = submodule[2:]  # Remove leading ./
                        if f"path = {rel_path}" in gitmodules_content:
                            configured_submodules.append(submodule)

            unconfigured_submodules = [
                s for s in potential_submodules if s not in configured_submodules
            ]
            issues["submodules"]["found"] = len(unconfigured_submodules) > 0
            issues["submodules"]["count"] = len(unconfigured_submodules)
            issues["submodules"][
                "description"
            ] = f"Found {len(unconfigured_submodules)} unconfigured Git submodules"
            issues["submodules"]["details"] = unconfigured_submodules
    except Exception:
        pass

    # Check for Git issues (uncommitted changes)
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            uncommitted_changes = [
                line for line in result.stdout.strip().split("\n") if line
            ]
            issues["git"]["found"] = len(uncommitted_changes) > 0
            issues["git"]["count"] = len(uncommitted_changes)
            issues["git"][
                "description"
            ] = f"Found {len(uncommitted_changes)} uncommitted changes"
    except Exception:
        pass

    # Check for line ending issues in files with formatting problems
    if issues["lint"]["found"]:
        try:
            # Check a sample of files with formatting issues for CRLF line endings
            crlf_files = []
            for file_line in files[:5]:  # Check up to 5 files
                match = re.search(r"would reformat (.+)$", file_line)
                if match:
                    file_path = match.group(1)
                    with open(file_path, "rb") as f:
                        content = f.read()
                        if b"\r\n" in content:
                            crlf_files.append(file_path)

            if crlf_files:
                if not issues["black_config"]["found"]:
                    issues["black_config"]["found"] = True
                issues["black_config"]["count"] += len(crlf_files)
                issues["black_config"][
                    "description"
                ] += f" Found {len(crlf_files)} files with CRLF line endings"
                issues["black_config"]["details"] = crlf_files
        except Exception:
            pass

    return issues


def prompt_with_default(prompt_text: str, default: bool) -> bool:
    """
    Prompt the user with a yes/no question and handle keyboard interrupts gracefully.

    Args:
        prompt_text: The text to display in the prompt
        default: The default value if the user just presses Enter

    Returns:
        The user's choice (True for yes, False for no)
    """
    default_text = "Y/n" if default else "y/N"
    prompt = f"{prompt_text} [{default_text}]: "

    try:
        user_input = input(prompt).strip().lower()
        if not user_input:
            return default
        return user_input.startswith("y")
    except (KeyboardInterrupt, EOFError):
        # Handle keyboard interrupts (Ctrl+C) and EOF (Ctrl+D)
        print("\nInterrupted. Using default values.")
        return default


def interactive_update(verbose: bool = False) -> Tuple[bool, bool, bool, bool, bool]:
    """
    Interactive update process that analyzes the project and asks the user which steps to skip.

    Args:
        verbose: Whether to show verbose output

    Returns:
        Tuple of (skip_tests, skip_lint, skip_mypy, skip_publish, skip_submodules)
    """
    click.echo("Analyzing project for potential issues...")
    issues = analyze_project_issues()

    # Display analysis results
    click.echo("\nAnalysis results:")

    if issues["tests"]["found"]:
        click.echo(f"✓ Tests: {issues['tests']['description']}")
    else:
        click.echo("✗ Tests: No tests found")

    if issues["lint"]["found"]:
        click.echo(f"✗ Lint: {issues['lint']['description']}")
    else:
        click.echo("✓ Lint: No formatting issues found")

    if issues["mypy"]["found"]:
        click.echo(f"✗ MyPy: {issues['mypy']['description']}")
    else:
        click.echo("✓ MyPy: No type checking issues found")

    if issues["submodules"]["found"]:
        click.echo(f"✗ Submodules: {issues['submodules']['description']}")
        if verbose and "details" in issues["submodules"]:
            for submodule in issues["submodules"]["details"]:
                click.echo(f"  - {submodule}")
    else:
        click.echo("✓ Submodules: All Git submodules are properly configured")

    if issues["git"]["found"]:
        click.echo(f"✗ Git: {issues['git']['description']}")
    else:
        click.echo("✓ Git: No uncommitted changes")

    if issues["black_config"]["found"]:
        click.echo(f"✗ Black Config: {issues['black_config']['description']}")
        if verbose and "details" in issues["black_config"]:
            for file in issues["black_config"]["details"]:
                click.echo(f"  - {file}")
        click.echo(
            "  Tip: Run 'spectomate format black --fix-config' to fix Black configuration issues"
        )
    else:
        click.echo("✓ Black Config: Black configuration is properly set up")

    # Ask user which steps to skip
    click.echo("\nBased on the analysis, you can choose which steps to skip:")

    try:
        # Use our custom prompt function that handles interrupts
        run_tests = prompt_with_default("Run tests?", issues["tests"]["found"])
        run_lint = prompt_with_default("Run linting?", issues["lint"]["found"])
        run_mypy = prompt_with_default("Run type checking?", issues["mypy"]["found"])
        run_submodules = prompt_with_default(
            "Check and fix submodules?", issues["submodules"]["found"]
        )

        # If Black config issues were found, ask if they want to fix them
        if issues["black_config"]["found"]:
            fix_black_config = prompt_with_default("Fix Black configuration?", True)
            if fix_black_config:
                click.echo("Running Black configuration fix...")
                try:
                    # Find the scripts directory
                    scripts_dir = Path(__file__).parent.parent / "scripts"
                    fix_black_config_script = scripts_dir / "fix_black_config.py"

                    if fix_black_config_script.exists():
                        subprocess.run(
                            [
                                "python",
                                str(fix_black_config_script),
                                "--auto-format",
                                "--fix-line-endings",
                            ],
                            check=False,
                        )
                except Exception as e:
                    click.echo(f"Error fixing Black configuration: {e}")

        run_publish = prompt_with_default("Publish to PyPI and GitHub?", True)

        return (
            not run_tests,
            not run_lint,
            not run_mypy,
            not run_publish,
            not run_submodules,
        )
    except Exception as e:
        click.echo(f"\nError during interactive prompts: {e}")
        click.echo("Using recommended defaults based on analysis...")

        # Use sensible defaults based on the analysis
        return (
            not issues["tests"]["found"],  # Skip tests if none found
            not issues["lint"]["found"],  # Skip lint if no issues found
            not issues["mypy"]["found"],  # Skip mypy if no issues found
            False,  # Don't skip publish by default
            not issues["submodules"]["found"],  # Skip submodules if no issues found
        )


def run_update_script(
    skip_tests: bool = False,
    skip_lint: bool = False,
    skip_mypy: bool = False,
    skip_publish: bool = False,
    skip_submodules: bool = False,
    verbose: bool = False,
) -> int:
    """
    Uruchamia skrypt aktualizujący wersję pakietu.

    Args:
        skip_tests: Czy pominąć testy
        skip_lint: Czy pominąć sprawdzanie linterem
        skip_mypy: Czy pominąć sprawdzanie typów mypy
        skip_publish: Czy pominąć publikację do PyPI i GitHub
        skip_submodules: Czy pominąć sprawdzanie i naprawianie submodułów Git
        verbose: Czy wyświetlać szczegółowe informacje

    Returns:
        Kod wyjścia skryptu (0 oznacza sukces)
    """
    # Znajdź ścieżkę do katalogu update
    # Najpierw sprawdź, czy jesteśmy w projekcie spectomate
    spectomate_update_dir = Path(__file__).parent.parent / "update"

    # Jeśli nie jesteśmy w projekcie spectomate, sprawdź czy mamy dostęp do skryptów update
    # w bieżącym projekcie
    if spectomate_update_dir.exists():
        update_dir = spectomate_update_dir
    else:
        # Sprawdź, czy w bieżącym projekcie jest katalog update
        current_dir = Path.cwd()
        project_update_dir = current_dir / "update"

        if project_update_dir.exists():
            update_dir = project_update_dir
        else:
            click.echo(
                "Nie znaleziono katalogu update. Sprawdź, czy jesteś w katalogu projektu."
            )
            return 1

    version_script = update_dir / "version.sh"

    if not version_script.exists():
        click.echo(
            f"Nie znaleziono skryptu {version_script}. Sprawdź, czy jesteś w katalogu projektu."
        )
        return 1

    # Ustaw zmienne środowiskowe na podstawie parametrów
    env = os.environ.copy()

    # Ustaw zmienną TERM, jeśli nie jest ustawiona
    if "TERM" not in env:
        env["TERM"] = "xterm"

    if skip_tests:
        env["SKIP_TESTS"] = "1"

    if skip_lint:
        env["SKIP_LINT"] = "1"

    if skip_mypy:
        env["SKIP_MYPY"] = "1"

    if skip_publish:
        env["SKIP_PUBLISH"] = "1"

    if skip_submodules:
        env["SKIP_SUBMODULES"] = "1"

    if verbose:
        env["VERBOSE"] = "1"

    # Uruchom skrypt
    try:
        result = subprocess.run(
            ["bash", str(version_script)],
            env=env,
            check=False,
        )
        return result.returncode
    except subprocess.SubprocessError as e:
        click.echo(f"Błąd podczas uruchamiania skryptu: {e}", err=True)
        return 1


@click.command(name="update")
@click.option("--no-test", is_flag=True, help="Pomiń uruchamianie testów")
@click.option("--no-lint", is_flag=True, help="Pomiń sprawdzanie linterem")
@click.option("--no-mypy", is_flag=True, help="Pomiń sprawdzanie typów mypy")
@click.option("--no-publish", is_flag=True, help="Pomiń publikację do PyPI i GitHub")
@click.option(
    "--no-submodules",
    is_flag=True,
    help="Pomiń sprawdzanie i naprawianie submodułów Git",
)
@click.option("--verbose", is_flag=True, help="Wyświetlaj szczegółowe informacje")
@click.option(
    "--interactive",
    "-i",
    is_flag=True,
    help="Tryb interaktywny - analizuj projekt i pytaj o kroki do pominięcia",
)
@click.option(
    "--analyze-only",
    "-a",
    is_flag=True,
    help="Tylko analizuj projekt i wyświetl wyniki bez wykonywania aktualizacji",
)
def update_command(
    no_test: bool,
    no_lint: bool,
    no_mypy: bool,
    no_publish: bool,
    no_submodules: bool,
    verbose: bool,
    interactive: bool,
    analyze_only: bool,
) -> None:
    """Aktualizuje wersję pakietu i opcjonalnie publikuje go.

    Komenda automatycznie aktualizuje numer wersji w plikach projektu, uruchamia testy i publikuje pakiet.
    Można wyłączyć poszczególne etapy za pomocą opcji --no-*.

    Przykłady:
        spectomate update                  # Pełna aktualizacja z publikacją
        spectomate update --interactive    # Interaktywna aktualizacja z analizą projektu
        spectomate update --analyze-only   # Tylko analizuj projekt bez aktualizacji
        spectomate update --no-publish     # Aktualizacja bez publikacji
        spectomate update --no-mypy        # Aktualizacja bez sprawdzania typów mypy
        spectomate update --no-test        # Aktualizacja bez uruchamiania testów
        spectomate update --no-lint        # Aktualizacja bez sprawdzania linterem
        spectomate update --no-submodules  # Aktualizacja bez sprawdzania submodułów Git
        spectomate update --verbose        # Aktualizacja z wyświetlaniem szczegółowych informacji
    """
    # Pobierz nazwę projektu z bieżącego katalogu
    try:
        project_name = Path.cwd().name
    except Exception:
        project_name = "projekt"

    click.echo(f"Aktualizowanie pakietu {project_name}...")

    # If analyze-only mode is enabled, just run the analysis and exit
    if analyze_only:
        click.echo("Analyzing project for potential issues...")
        issues = analyze_project_issues()

        # Display analysis results
        click.echo("\nAnalysis results:")

        if issues["tests"]["found"]:
            click.echo(f"✓ Tests: {issues['tests']['description']}")
        else:
            click.echo("✗ Tests: No tests found")

        if issues["lint"]["found"]:
            click.echo(f"✗ Lint: {issues['lint']['description']}")
        else:
            click.echo("✓ Lint: No formatting issues found")

        if issues["mypy"]["found"]:
            click.echo(f"✗ MyPy: {issues['mypy']['description']}")
        else:
            click.echo("✓ MyPy: No type checking issues found")

        if issues["submodules"]["found"]:
            click.echo(f"✗ Submodules: {issues['submodules']['description']}")
            if verbose and "details" in issues["submodules"]:
                for submodule in issues["submodules"]["details"]:
                    click.echo(f"  - {submodule}")
        else:
            click.echo("✓ Submodules: All Git submodules are properly configured")

        if issues["git"]["found"]:
            click.echo(f"✗ Git: {issues['git']['description']}")
        else:
            click.echo("✓ Git: No uncommitted changes")

        if issues["black_config"]["found"]:
            click.echo(f"✗ Black Config: {issues['black_config']['description']}")
            if verbose and "details" in issues["black_config"]:
                for file in issues["black_config"]["details"]:
                    click.echo(f"  - {file}")
            click.echo(
                "  Tip: Run 'spectomate format black --fix-config' to fix Black configuration issues"
            )
        else:
            click.echo("✓ Black Config: Black configuration is properly set up")

        click.echo("\nAnalysis complete. No updates performed.")
        return

    # If interactive mode is enabled, analyze the project and ask which steps to skip
    if interactive:
        try:
            skip_tests, skip_lint, skip_mypy, skip_publish, skip_submodules = (
                interactive_update(verbose)
            )
            click.echo("\nUsing selected options for update...")
        except KeyboardInterrupt:
            click.echo("\nUpdate process interrupted. Exiting.")
            sys.exit(1)
    else:
        skip_tests = no_test
        skip_lint = no_lint
        skip_mypy = no_mypy
        skip_publish = no_publish
        skip_submodules = no_submodules

    try:
        exit_code = run_update_script(
            skip_tests=skip_tests,
            skip_lint=skip_lint,
            skip_mypy=skip_mypy,
            skip_publish=skip_publish,
            skip_submodules=skip_submodules,
            verbose=verbose,
        )

        if exit_code != 0:
            click.echo(
                "Aktualizacja nie powiodła się. Sprawdź komunikaty błędów powyżej.",
                err=True,
            )
            sys.exit(exit_code)
        else:
            click.echo("Aktualizacja zakończona pomyślnie!")
    except KeyboardInterrupt:
        click.echo("\nUpdate process interrupted. Exiting.")
        sys.exit(1)
