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
    Uruchamia skrypt aktualizujący wersję pakietu.

    Args:
        skip_tests: Czy pominąć testy
        skip_lint: Czy pominąć sprawdzanie linterem
        skip_mypy: Czy pominąć sprawdzanie typów mypy
        skip_publish: Czy pominąć publikację do PyPI i GitHub
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


@click.command()
@click.option("--no-test", is_flag=True, help="Pomiń uruchamianie testów")
@click.option("--no-lint", is_flag=True, help="Pomiń sprawdzanie linterem")
@click.option("--no-mypy", is_flag=True, help="Pomiń sprawdzanie typów mypy")
@click.option("--no-publish", is_flag=True, help="Pomiń publikację do PyPI i GitHub")
@click.option("--verbose", is_flag=True, help="Wyświetlaj szczegółowe informacje")
def update_command(
    no_test: bool, no_lint: bool, no_mypy: bool, no_publish: bool, verbose: bool
) -> None:
    """Aktualizuje wersję pakietu i opcjonalnie publikuje go.

    Komenda automatycznie aktualizuje numer wersji w plikach projektu, uruchamia testy i publikuje pakiet.
    Można wyłączyć poszczególne etapy za pomocą opcji --no-*.

    Przykłady:
        spectomate update                  # Pełna aktualizacja z publikacją
        spectomate update --no-publish     # Aktualizacja bez publikacji
        spectomate update --no-mypy        # Aktualizacja bez sprawdzania typów mypy
        spectomate update --no-test        # Aktualizacja bez uruchamiania testów
        spectomate update --no-lint        # Aktualizacja bez sprawdzania linterem
        spectomate update --verbose        # Aktualizacja z wyświetlaniem szczegółowych informacji
    """
    # Pobierz nazwę projektu z bieżącego katalogu
    try:
        project_name = Path.cwd().name
    except Exception:
        project_name = "projekt"

    click.echo(f"Aktualizowanie pakietu {project_name}...")

    exit_code = run_update_script(
        skip_tests=no_test,
        skip_lint=no_lint,
        skip_mypy=no_mypy,
        skip_publish=no_publish,
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
