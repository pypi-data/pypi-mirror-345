"""
Schemat dla formatu pip (requirements.txt).
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union


class PipSchema:
    """
    Klasa definiująca schemat dla formatu pip (requirements.txt).
    """

    @staticmethod
    def parse_requirement(req_line: str) -> Dict[str, Any]:
        """
        Parsuje linię z pliku requirements.txt.

        Args:
            req_line: Linia z pliku requirements.txt

        Returns:
            Słownik z informacjami o zależności
        """
        # Usuwamy komentarze i białe znaki
        line = req_line.split("#")[0].strip()

        if not line or line.startswith("#"):
            return {"type": "comment", "content": req_line}

        if line.startswith("-"):
            return {"type": "option", "content": line}

        # Obsługa specyfikacji wersji
        # Przykłady: package==1.0.0, package>=1.0.0, package<=1.0.0
        package_pattern = (
            r"([a-zA-Z0-9_\-\.]+)(?:\s*([<>=!~]{1,2})\s*([a-zA-Z0-9_\-\.]+))?"
        )
        match = re.match(package_pattern, line)

        if match:
            package_name = match.group(1)
            operator = match.group(2)
            version = match.group(3)

            result = {
                "type": "package",
                "name": package_name,
            }

            if operator and version:
                result["version_spec"] = {"operator": operator, "version": version}

            return result

        # Jeśli nie pasuje do żadnego wzorca, traktujemy jako prosty pakiet
        return {"type": "package", "name": line}

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parsuje plik requirements.txt.

        Args:
            file_path: Ścieżka do pliku requirements.txt

        Returns:
            Słownik z listą zależności
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

        requirements = []

        with open(file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line:  # Pomijamy puste linie
                    req = PipSchema.parse_requirement(line)
                    requirements.append(req)

        return {"format": "pip", "requirements": requirements}

    @staticmethod
    def generate_requirements_txt(data: Dict[str, Any]) -> str:
        """
        Generuje zawartość pliku requirements.txt na podstawie danych.

        Args:
            data: Dane w formacie schematu pip

        Returns:
            Zawartość pliku requirements.txt
        """
        if "requirements" not in data:
            raise ValueError("Brak wymaganych zależności w danych")

        lines = []

        for req in data["requirements"]:
            # Obsługa przypadku, gdy req jest stringiem (prosty format zależności)
            if isinstance(req, str):
                lines.append(req)
                continue

            # Obsługa przypadku, gdy req jest słownikiem (rozszerzony format zależności)
            req_type = req.get("type")

            if req_type == "comment":
                lines.append(req["content"])

            elif req_type == "option":
                lines.append(req["content"])

            elif req_type == "package":
                package_line = req["name"]

                if "version_spec" in req:
                    spec = req["version_spec"]
                    package_line += f"{spec['operator']}{spec['version']}"

                lines.append(package_line)

        return "\n".join(lines)

    @staticmethod
    def write_requirements_txt(
        data: Dict[str, Any], output_path: Union[str, Path]
    ) -> Path:
        """
        Zapisuje dane do pliku requirements.txt.

        Args:
            data: Dane w formacie schematu pip
            output_path: Ścieżka do pliku wyjściowego

        Returns:
            Ścieżka do zapisanego pliku
        """
        output_path = Path(output_path)

        # Tworzymy katalogi, jeśli nie istnieją
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = PipSchema.generate_requirements_txt(data)

        with open(output_path, "w") as f:
            f.write(content)

        return output_path
