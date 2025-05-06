"""
Konwerter z formatu pip (requirements.txt) do formatu poetry (pyproject.toml).
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from spectomate.core.base_converter import BaseConverter
from spectomate.schemas.pip_schema import PipSchema
from spectomate.schemas.poetry_schema import PoetrySchema


class PipToPoetryConverter(BaseConverter):
    """
    Konwerter z formatu pip (requirements.txt) do formatu poetry (pyproject.toml).
    """

    def __init__(
        self,
        source_file: Optional[Union[str, Path]] = None,
        target_file: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicjalizuje konwerter.

        Args:
            source_file: Ścieżka do pliku requirements.txt
            target_file: Ścieżka do pliku pyproject.toml
            options: Opcje konwersji
        """
        super().__init__(source_file, target_file, options)

        # Ustawiamy domyślne opcje
        if self.options is None:
            self.options = {}

    @staticmethod
    def get_source_format() -> str:
        """Zwraca identyfikator formatu źródłowego."""
        return "pip"

    @staticmethod
    def get_target_format() -> str:
        """Zwraca identyfikator formatu docelowego."""
        return "poetry"

    def read_source(self) -> Dict[str, Any]:
        """
        Odczytuje plik requirements.txt.

        Returns:
            Słownik z zależnościami pip
        """
        if self.source_file is None:
            raise ValueError("Nie podano ścieżki do pliku źródłowego")

        data = PipSchema.parse_file(self.source_file)

        # Filtrujemy tylko rzeczywiste zależności (pakiety) i pomijamy komentarze i opcje
        if "requirements" in data:
            package_deps = [
                dep
                for dep in data["requirements"]
                if isinstance(dep, dict) and dep.get("type") == "package"
            ]

            # Konwertujemy słowniki pakietów na stringi dla testów
            dependencies = []
            for dep in package_deps:
                if "version_spec" in dep:
                    dependencies.append(
                        f"{dep['name']}{dep['version_spec']['operator']}{dep['version_spec']['version']}"
                    )
                else:
                    dependencies.append(dep["name"])

            # Ustawiamy klucz "dependencies" dla zachowania kompatybilności z testami
            data["dependencies"] = dependencies

        return data

    def convert(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje dane z formatu pip do formatu poetry.

        Args:
            source_data: Dane w formacie pip

        Returns:
            Dane w formacie poetry
        """
        # Sprawdzamy, czy dane są w odpowiednim formacie
        if source_data.get("format") != "pip":
            raise ValueError("Dane źródłowe nie są w formacie pip")

        # Pobieramy opcje
        project_name = self.options.get("project_name", "myproject")
        version = self.options.get("version", "0.1.0")

        # Konwertujemy dane
        return PoetrySchema.convert_from_pip(source_data, project_name, version)

    def write_target(self, target_data: Dict[str, Any]) -> Path:
        """
        Zapisuje dane do pliku pyproject.toml.

        Args:
            target_data: Dane w formacie poetry

        Returns:
            Ścieżka do zapisanego pliku
        """
        if self.target_file is None:
            # Jeśli nie podano ścieżki do pliku docelowego, tworzymy ją na podstawie pliku źródłowego
            if self.source_file is None:
                raise ValueError(
                    "Nie podano ścieżki do pliku docelowego ani źródłowego"
                )

            source_path = Path(self.source_file)
            self.target_file = source_path.parent / "pyproject.toml"

        return PoetrySchema.write_pyproject_toml(target_data, self.target_file)

    def execute(self) -> Path:
        """
        Wykonuje pełny proces konwersji.

        Returns:
            Ścieżka do zapisanego pliku
        """
        # Odczytujemy plik źródłowy
        source_data = self.read_source()

        # Konwertujemy dane
        target_data = self.convert(source_data)

        # Zapisujemy dane do pliku docelowego
        return self.write_target(target_data)
