"""
Moduł zawierający funkcje pomocnicze dla Spectomate.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Importujemy ConverterRegistry dopiero w funkcji get_available_formats,
# aby uniknąć cyklicznych importów
# from spectomate.core.registry import ConverterRegistry


def get_available_formats(format_type: Optional[str] = None) -> Set[str]:
    """
    Zwraca zbiór wszystkich dostępnych formatów.

    Args:
        format_type: Optional filter for format type ('input', 'output', or None for all)

    Returns:
        Zbiór nazw formatów
    """
    from spectomate.core.registry import ConverterRegistry

    if format_type is None:
        return ConverterRegistry.get_all_formats()
    elif format_type == "input":
        return ConverterRegistry.get_input_formats()
    elif format_type == "output":
        return ConverterRegistry.get_output_formats()
    else:
        raise ValueError(
            f"Unknown format type: {format_type}. Use 'input', 'output', or None."
        )


def get_default_output_file(source_file: Path, target_format: str) -> Path:
    """
    Generuje domyślną nazwę pliku wyjściowego na podstawie formatu docelowego.

    Args:
        source_file: Ścieżka do pliku źródłowego
        target_format: Format docelowy

    Returns:
        Ścieżka do pliku wyjściowego
    """
    format_extensions = {
        "pip": "requirements.txt",
        "conda": "environment.yml",
        "poetry": "pyproject.toml",
        "pipenv": "Pipfile",
        "pdm": "pyproject.toml",
    }

    if target_format not in format_extensions:
        raise ValueError(f"Nieznany format docelowy: {target_format}")

    return source_file.parent / format_extensions[target_format]


def check_package_in_conda(package_name: str) -> bool:
    """
    Sprawdza, czy pakiet jest dostępny w repozytoriach conda.

    Args:
        package_name: Nazwa pakietu do sprawdzenia

    Returns:
        True jeśli pakiet jest dostępny, False w przeciwnym wypadku
    """
    try:
        # Usuwamy specyfikację wersji, jeśli istnieje
        if "==" in package_name:
            package_name = package_name.split("==")[0]
        elif ">=" in package_name:
            package_name = package_name.split(">=")[0]
        elif "<=" in package_name:
            package_name = package_name.split("<=")[0]

        # Sprawdzamy dostępność pakietu w conda
        result = subprocess.run(
            ["conda", "search", package_name, "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            return False

        import json

        data = json.loads(result.stdout)

        # Jeśli pakiet istnieje, dane będą zawierały klucz z nazwą pakietu
        return package_name in data
    except Exception:
        # W przypadku błędu zakładamy, że pakiet nie jest dostępny
        return False


def run_subprocess(cmd: List[str], capture_output: bool = True) -> Tuple[int, str, str]:
    """
    Uruchamia polecenie w podprocesie.

    Args:
        cmd: Lista elementów polecenia
        capture_output: Czy przechwytywać wyjście

    Returns:
        Krotka (kod_wyjścia, stdout, stderr)
    """
    try:
        if capture_output:
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            return process.returncode, process.stdout, process.stderr
        else:
            process = subprocess.run(cmd, check=False)
            return process.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)


def is_external_tool_available(tool_name: str) -> bool:
    """
    Sprawdza, czy zewnętrzne narzędzie jest dostępne w systemie.

    Args:
        tool_name: Nazwa narzędzia do sprawdzenia

    Returns:
        True jeśli narzędzie jest dostępne, False w przeciwnym wypadku
    """
    try:
        subprocess.run(
            [tool_name, "--version"],
            capture_output=True,
            check=False,
        )
        return True
    except FileNotFoundError:
        return False


def get_project_root() -> Path:
    """
    Find the root directory of the project.

    The function looks for common project files like pyproject.toml, setup.py,
    or .git directory to determine the project root.

    Returns:
        Path to the project root directory
    """
    # Start from the current working directory
    current_dir = Path.cwd()

    # Go up the directory tree until we find a project root indicator
    while current_dir != current_dir.parent:
        # Check for common project root indicators
        if any(
            (current_dir / marker).exists()
            for marker in [
                "pyproject.toml",
                "setup.py",
                "setup.cfg",
                ".git",
                "requirements.txt",
            ]
        ):
            return current_dir

        # Move up one directory
        current_dir = current_dir.parent

    # If we can't find a project root, return the current directory
    return Path.cwd()
