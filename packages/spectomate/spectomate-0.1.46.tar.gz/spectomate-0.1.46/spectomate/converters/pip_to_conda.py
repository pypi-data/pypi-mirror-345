"""
Konwerter z formatu pip (requirements.txt) do formatu conda (environment.yml).
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from spectomate.core.base_converter import BaseConverter
from spectomate.core.registry import register_converter
from spectomate.core.utils import check_package_in_conda, get_default_output_file


@register_converter
class PipToCondaConverter(BaseConverter):
    """
    Konwerter z formatu pip (requirements.txt) do formatu conda (environment.yml).
    """

    @staticmethod
    def get_source_format() -> str:
        """Zwraca identyfikator formatu źródłowego."""
        return "pip"

    @staticmethod
    def get_target_format() -> str:
        """Zwraca identyfikator formatu docelowego."""
        return "conda"

    def read_source(self) -> Dict[str, Any]:
        """
        Odczytuje plik requirements.txt.

        Returns:
            Słownik z listą zależności
        """
        if not self.source_file or not self.source_file.exists():
            raise FileNotFoundError(f"Plik źródłowy nie istnieje: {self.source_file}")

        dependencies = []
        with open(self.source_file, "r") as f:
            for line in f:
                line = line.strip()

                # Pomijamy komentarze i puste linie
                if not line or line.startswith("#"):
                    continue

                # Pomijamy linie opcji (np. --find-links)
                if line.startswith("-"):
                    continue

                # Usuwamy komentarze na końcu linii
                if "#" in line:
                    line = line.split("#")[0].strip()

                dependencies.append(line)

        return {"dependencies": dependencies}

    def convert(self, source_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Konwertuje zależności z formatu pip na format conda.

        Args:
            source_data: Dane w formacie źródłowym (opcjonalnie)

        Returns:
            Dane w formacie docelowym
        """
        if source_data is None:
            if self.source_data is None:
                raise ValueError("Brak danych źródłowych do konwersji")
            source_data = self.source_data

        # Pobieramy nazwę środowiska z opcji lub używamy domyślnej
        env_name = self.options.get("env_name", "myenv")

        # Przygotowujemy strukturę pliku environment.yml
        conda_data = {
            "name": env_name,
            "channels": ["defaults", "conda-forge"],
            "dependencies": [],
            "pip": [],
        }

        # Konwertujemy zależności
        for dep in source_data["dependencies"]:
            # Sprawdzamy, czy pakiet jest dostępny w conda
            package_name = dep.split("=")[0].split("<")[0].split(">")[0].strip()

            if check_package_in_conda(package_name):
                conda_data["dependencies"].append(dep)
            else:
                conda_data["pip"].append(dep)

        # Dodajemy pakiet pip do zależności conda, jeśli mamy jakieś pakiety pip
        if conda_data["pip"]:
            if "pip" not in conda_data["dependencies"]:
                conda_data["dependencies"].append("pip")
        else:
            # Usuwamy pustą sekcję pip
            del conda_data["pip"]

        return conda_data

    def write_target(self, target_data: Optional[Dict[str, Any]] = None) -> Path:
        """
        Zapisuje dane do pliku environment.yml.

        Args:
            target_data: Dane w formacie docelowym (opcjonalnie)

        Returns:
            Ścieżka do zapisanego pliku
        """
        if target_data is None:
            if self.target_data is None:
                raise ValueError("Brak danych docelowych do zapisu")
            target_data = self.target_data

        # Jeśli nie podano pliku docelowego, generujemy domyślną nazwę
        if self.target_file is None:
            if self.source_file is None:
                self.target_file = Path("environment.yml")
            else:
                self.target_file = get_default_output_file(self.source_file, "conda")

        # Zapisujemy dane do pliku YAML
        with open(self.target_file, "w") as f:
            yaml.dump(target_data, f, default_flow_style=False, sort_keys=False)

        return self.target_file
