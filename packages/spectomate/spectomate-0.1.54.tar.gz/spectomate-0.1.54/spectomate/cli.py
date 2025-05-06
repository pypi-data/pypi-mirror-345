"""
Interfejs wiersza poleceń dla Spectomate.
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

import click

from spectomate import __version__, registry
from spectomate.core.utils import get_available_formats
from spectomate.format_cli import format_cli
from spectomate.git_cli import git_cli
from spectomate.mypy_cli import mypy_cli
from spectomate.test_cli import test_cli
from spectomate.update_cli import update_command


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version and exit")
@click.pass_context
def cli(ctx: click.Context, version: bool):
    """Spectomate - modularny konwerter formatów pakietów Python."""
    if version:
        click.echo(f"Spectomate version: {__version__}")
        ctx.exit()

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@cli.command()
@click.option(
    "--input-format",
    "-i",
    help="Format wejściowy",
    type=click.Choice(get_available_formats("input")),
    required=True,
)
@click.option(
    "--output-format",
    "-o",
    help="Format wyjściowy",
    type=click.Choice(get_available_formats("output")),
    required=True,
)
@click.option(
    "--input-file",
    "-f",
    help="Plik wejściowy",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    required=True,
)
@click.option(
    "--output-file",
    "-t",
    help="Plik wyjściowy",
    type=click.Path(file_okay=True, dir_okay=False, writable=True),
    required=True,
)
def convert(input_format: str, output_format: str, input_file: str, output_file: str):
    """Konwertuje plik z jednego formatu na drugi."""
    # Sprawdź, czy istnieje konwerter dla podanej pary formatów
    if not registry.has_converter(input_format, output_format):
        click.echo(
            f"Nie znaleziono konwertera z formatu {input_format} do {output_format}",
            err=True,
        )
        sys.exit(1)

    # Pobierz konwerter
    converter = registry.get_converter(input_format, output_format)

    # Konwertuj plik
    try:
        converter.convert_file(input_file, output_file)
        click.echo(f"Pomyślnie skonwertowano {input_file} do {output_file}")
    except Exception as e:
        click.echo(f"Błąd podczas konwersji: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--input-format",
    "-i",
    help="Format wejściowy",
    type=click.Choice(get_available_formats("input")),
    required=False,
)
@click.option(
    "--output-format",
    "-o",
    help="Format wyjściowy",
    type=click.Choice(get_available_formats("output")),
    required=False,
)
def list_converters(input_format: Optional[str], output_format: Optional[str]):
    """Wyświetla listę dostępnych konwerterów."""
    converters = registry.get_converters(input_format, output_format)

    if not converters:
        if input_format and output_format:
            click.echo(
                f"Nie znaleziono konwerterów z formatu {input_format} do {output_format}",
                err=True,
            )
        elif input_format:
            click.echo(f"Nie znaleziono konwerterów z formatu {input_format}", err=True)
        elif output_format:
            click.echo(
                f"Nie znaleziono konwerterów do formatu {output_format}", err=True
            )
        else:
            click.echo("Nie znaleziono żadnych konwerterów", err=True)
        sys.exit(1)

    click.echo("Dostępne konwertery:")
    for converter in converters:
        click.echo(
            f"  {converter.input_format} -> {converter.output_format}: {converter.description}"
        )


# Dodaj komendy z innych modułów
cli.add_command(update_command)
cli.add_command(test_cli)
cli.add_command(mypy_cli)
cli.add_command(git_cli)
cli.add_command(format_cli)


def main():
    """Entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    sys.exit(main())
