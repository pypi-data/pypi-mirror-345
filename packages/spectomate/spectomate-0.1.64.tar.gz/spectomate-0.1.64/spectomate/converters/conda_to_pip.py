"""
Konwerter z formatu conda (environment.yml) do formatu pip (requirements.txt).
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from spectomate.core.base_converter import BaseConverter
from spectomate.schemas.conda_schema import CondaSchema
from spectomate.schemas.pip_schema import PipSchema


class CondaToPipConverter(BaseConverter):
    """
    Konwerter z formatu conda (environment.yml) do formatu pip (requirements.txt).
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
            source_file: Ścieżka do pliku environment.yml
            target_file: Ścieżka do pliku requirements.txt
            options: Opcje konwersji
        """
        super().__init__(source_file, target_file, options)

        # Ustawiamy domyślne opcje
        if self.options is None:
            self.options = {}

    @staticmethod
    def get_source_format() -> str:
        """Zwraca identyfikator formatu źródłowego."""
        return "conda"

    @staticmethod
    def get_target_format() -> str:
        """Zwraca identyfikator formatu docelowego."""
        return "pip"

    def read_source(self) -> Dict[str, Any]:
        """
        Odczytuje plik environment.yml.

        Returns:
            Słownik z informacjami o środowisku conda
        """
        if self.source_file is None:
            raise ValueError("Nie podano ścieżki do pliku źródłowego")

        return CondaSchema.parse_file(self.source_file)

    def convert(self, source_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konwertuje dane z formatu conda do formatu pip.

        Args:
            source_data: Dane w formacie conda

        Returns:
            Dane w formacie pip
        """
        # Inicjalizujemy dane wyjściowe
        target_data = {
            "format": "pip",
            "requirements": [],  # Używamy klucza "requirements" zamiast "dependencies"
        }

        # Pobieramy zależności conda
        conda_deps = CondaSchema.extract_conda_dependencies(source_data)

        # Pobieramy zależności pip
        pip_deps = CondaSchema.extract_pip_dependencies(source_data)

        # Konwertujemy zależności conda na format pip
        for dep in conda_deps:
            # Usuwamy specyfikację kanału, jeśli istnieje
            if "::" in dep:
                _, dep = dep.split("::", 1)

            # Dodajemy zależność do listy
            target_data["requirements"].append(dep)

        # Dodajemy zależności pip
        target_data["requirements"].extend(pip_deps)

        # Sortujemy zależności
        target_data["requirements"].sort()

        return target_data

    def write_target(self, target_data: Dict[str, Any]) -> Path:
        """
        Zapisuje dane do pliku requirements.txt.

        Args:
            target_data: Dane w formacie pip

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
            self.target_file = source_path.parent / "requirements.txt"

        return PipSchema.write_requirements_txt(target_data, self.target_file)

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
