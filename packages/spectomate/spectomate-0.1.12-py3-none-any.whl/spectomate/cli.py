"""
Interfejs wiersza poleceń dla Spectomate.
"""

import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import click

from spectomate import __version__, registry
from spectomate.core.utils import get_available_formats
from spectomate.update_cli import update_command


@click.group(invoke_without_command=True)
@click.version_option(version=__version__)
@click.pass_context
def cli(ctx: click.Context) -> None:
    """Spectomate - modularny konwerter formatów pakietów Python.

    Narzędzie do konwersji między różnymi formatami zarządzania pakietami w Pythonie.
    """
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
def list_formats() -> None:
    """Wyświetla listę dostępnych formatów i konwerterów."""
    formats = get_available_formats()

    click.echo("Dostępne formaty:")
    for format_name in sorted(formats):
        click.echo(f"  - {format_name}")

    click.echo("\nDostępne konwersje:")
    for converter_key in sorted(registry.get_converters()):
        source_format, target_format = converter_key
        click.echo(f"  - {source_format} -> {target_format}")


@cli.command()
@click.option(
    "-s",
    "--source-format",
    required=True,
    help="Format źródłowy (np. pip, conda, poetry)",
)
@click.option(
    "-t",
    "--target-format",
    required=True,
    help="Format docelowy (np. pip, conda, poetry)",
)
@click.option(
    "-i",
    "--input-file",
    required=True,
    type=click.Path(exists=True),
    help="Ścieżka do pliku wejściowego",
)
@click.option(
    "-o", "--output-file", type=click.Path(), help="Ścieżka do pliku wyjściowego"
)
@click.option("--env-name", help="Nazwa środowiska (dla formatów conda)")
@click.option("--project-name", help="Nazwa projektu (dla formatów poetry/pdm)")
@click.option(
    "--use-external/--no-external",
    default=False,
    help="Użyj zewnętrznych narzędzi do konwersji jeśli dostępne",
)
@click.option(
    "--verbose/--quiet", default=False, help="Wyświetlaj szczegółowe informacje"
)
def convert(
    source_format: str,
    target_format: str,
    input_file: str,
    output_file: Optional[str] = None,
    env_name: Optional[str] = None,
    project_name: Optional[str] = None,
    use_external: bool = False,
    verbose: bool = False,
) -> None:
    """Konwertuje plik pakietów z jednego formatu na inny."""
    try:
        options: Dict[str, Any] = {
            "verbose": verbose,
        }

        if env_name:
            options["env_name"] = env_name

        if project_name:
            options["project_name"] = project_name

        if use_external:
            options["use_external"] = True

        # Pobierz odpowiedni konwerter
        converter_cls = registry.get_converter(source_format, target_format)
        if converter_cls is None:
            click.echo(
                f"Błąd: Nie znaleziono konwertera z {source_format} do {target_format}",
                err=True,
            )
            sys.exit(1)

        # Utwórz instancję konwertera
        converter = converter_cls(
            source_file=input_file,
            target_file=output_file,
            options=options,
        )

        # Wykonaj konwersję
        if verbose:
            click.echo(f"Konwersja z {source_format} do {target_format}...")
            click.echo(f"Plik wejściowy: {input_file}")

        result_path = converter.execute()

        click.echo(f"Konwersja zakończona pomyślnie. Wynik zapisano w: {result_path}")

    except Exception as e:
        click.echo(f"Błąd podczas konwersji: {str(e)}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


# Rejestracja komendy update
cli.add_command(update_command, name="update")


def main(args: Optional[List[str]] = None) -> int:
    """
    Główna funkcja interfejsu wiersza poleceń.

    Args:
        args: Lista argumentów wiersza poleceń (opcjonalnie)

    Returns:
        Kod wyjścia (0 dla sukcesu, >0 dla błędu)
    """
    try:
        cli(args)
        return 0
    except Exception as e:
        click.echo(f"Błąd: {str(e)}", err=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
