"""
Interfejs wiersza poleceń dla funkcji aktualizacji Spectomate.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click


def run_update_script(
    skip_tests: bool = False,
    skip_lint: bool = False,
    skip_mypy: bool = False,
    skip_publish: bool = False,
    verbose: bool = False,
) -> int:
    """
    Uruchamia skrypt aktualizacji z odpowiednimi opcjami.

    Args:
        skip_tests: Czy pominąć testy
        skip_lint: Czy pominąć sprawdzanie linterem
        skip_mypy: Czy pominąć sprawdzanie typów mypy
        skip_publish: Czy pominąć publikację do PyPI i GitHub
        verbose: Czy wyświetlać szczegółowe informacje

    Returns:
        Kod wyjścia (0 dla sukcesu, >0 dla błędu)
    """
    # Określ ścieżkę do głównego katalogu projektu
    project_root = Path(__file__).parent.parent.absolute()
    update_script = project_root / "update" / "version.sh"

    if not update_script.exists():
        click.echo(
            f"Błąd: Nie znaleziono skryptu aktualizacji: {update_script}", err=True
        )
        return 1

    # Przygotuj argumenty dla skryptu aktualizacji
    env = os.environ.copy()

    if skip_tests:
        env["SKIP_TESTS"] = "1"

    if skip_lint:
        env["SKIP_LINT"] = "1"

    if skip_mypy:
        env["SKIP_MYPY"] = "1"

    if skip_publish:
        env["SKIP_PUBLISH"] = "1"

    if verbose:
        env["VERBOSE"] = "1"

    # Uruchom skrypt aktualizacji
    try:
        click.echo("Uruchamianie procesu aktualizacji...")

        process = subprocess.Popen(
            ["bash", str(update_script)], env=env, cwd=str(project_root)
        )

        return process.wait()
    except Exception as e:
        click.echo(
            f"Błąd podczas uruchamiania skryptu aktualizacji: {str(e)}", err=True
        )
        return 1


@click.command()
@click.option("--no-test", is_flag=True, help="Pomiń uruchamianie testów")
@click.option("--no-lint", is_flag=True, help="Pomiń sprawdzanie linterem")
@click.option("--skip-mypy", is_flag=True, help="Pomiń sprawdzanie typów mypy")
@click.option("--no-publish", is_flag=True, help="Pomiń publikację do PyPI i GitHub")
@click.option("--verbose", is_flag=True, help="Wyświetlaj szczegółowe informacje")
def update_command(
    no_test: bool, no_lint: bool, skip_mypy: bool, no_publish: bool, verbose: bool
) -> None:
    """Aktualizuje wersję pakietu i opcjonalnie publikuje go.

    Domyślnie uruchamia pełny proces aktualizacji, włączając testy, sprawdzanie linterem i publikację.
    Można wyłączyć poszczególne etapy za pomocą opcji --no-*.
    """
    exit_code = run_update_script(
        skip_tests=no_test,
        skip_lint=no_lint,
        skip_mypy=skip_mypy,
        skip_publish=no_publish,
        verbose=verbose,
    )

    if exit_code != 0:
        click.echo("Aktualizacja zakończona niepowodzeniem.", err=True)
        sys.exit(exit_code)
    else:
        click.echo("Aktualizacja zakończona pomyślnie!")
