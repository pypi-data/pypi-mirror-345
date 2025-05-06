"""
Schemat dla formatu poetry (pyproject.toml).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import toml


class PoetrySchema:
    """
    Klasa definiująca schemat dla formatu poetry (pyproject.toml).
    """

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parsuje plik pyproject.toml.

        Args:
            file_path: Ścieżka do pliku pyproject.toml

        Returns:
            Słownik z informacjami o projekcie poetry
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

        try:
            pyproject_data = toml.load(file_path)
        except Exception as e:
            raise ValueError(f"Błąd parsowania pliku TOML: {e}")

        # Sprawdzamy, czy plik ma sekcję [tool.poetry]
        if "tool" not in pyproject_data or "poetry" not in pyproject_data["tool"]:
            raise ValueError("Plik pyproject.toml nie zawiera sekcji [tool.poetry]")

        # Pobieramy sekcję poetry
        poetry_data = pyproject_data["tool"]["poetry"]

        # Dodajemy domyślne wartości, jeśli brakuje kluczy
        if "name" not in poetry_data:
            poetry_data["name"] = "myproject"

        if "version" not in poetry_data:
            poetry_data["version"] = "0.1.0"

        if "description" not in poetry_data:
            poetry_data["description"] = ""

        if "dependencies" not in poetry_data:
            poetry_data["dependencies"] = {}

        if "dev-dependencies" not in poetry_data and "group" not in poetry_data:
            poetry_data["dev-dependencies"] = {}

        # Dodajemy informację o formacie
        poetry_data["format"] = "poetry"

        return poetry_data

    @staticmethod
    def extract_dependencies(
        poetry_data: Dict[str, Any], include_dev: bool = False
    ) -> List[str]:
        """
        Wyodrębnia zależności z danych poetry.

        Args:
            poetry_data: Słownik z informacjami o projekcie poetry
            include_dev: Czy uwzględnić zależności deweloperskie

        Returns:
            Lista zależności w formacie pip
        """
        dependencies = []

        # Pobieramy zależności główne
        main_deps = poetry_data.get("dependencies", {})
        for name, constraint in main_deps.items():
            # Pomijamy python jako zależność
            if name.lower() == "python":
                continue

            if isinstance(constraint, str):
                # Prosty przypadek: "package = "version""
                dependencies.append(f"{name}{constraint}")
            elif isinstance(constraint, dict):
                # Złożony przypadek: "package = {version = "version", extras = [...]}"
                if "version" in constraint:
                    version = constraint["version"]
                    if "extras" in constraint:
                        extras = ",".join(constraint["extras"])
                        dependencies.append(f"{name}[{extras}]{version}")
                    else:
                        dependencies.append(f"{name}{version}")
                elif "git" in constraint:
                    # Zależność z git
                    git_url = constraint["git"]
                    if "rev" in constraint:
                        rev = constraint["rev"]
                        dependencies.append(f"git+{git_url}@{rev}#egg={name}")
                    else:
                        dependencies.append(f"git+{git_url}#egg={name}")
                elif "url" in constraint:
                    # Zależność z URL
                    url = constraint["url"]
                    dependencies.append(f"{name} @ {url}")
            else:
                # Nieznany format, dodajemy samą nazwę
                dependencies.append(name)

        # Pobieramy zależności deweloperskie, jeśli wymagane
        if include_dev:
            # Sprawdzamy, czy używamy starego formatu (dev-dependencies) czy nowego (group.dev.dependencies)
            if "dev-dependencies" in poetry_data:
                dev_deps = poetry_data.get("dev-dependencies", {})
                for name, constraint in dev_deps.items():
                    if isinstance(constraint, str):
                        dependencies.append(f"{name}{constraint}")
                    elif isinstance(constraint, dict) and "version" in constraint:
                        dependencies.append(f"{name}{constraint['version']}")
                    else:
                        dependencies.append(name)
            elif "group" in poetry_data and "dev" in poetry_data["group"]:
                dev_deps = poetry_data["group"]["dev"].get("dependencies", {})
                for name, constraint in dev_deps.items():
                    if isinstance(constraint, str):
                        dependencies.append(f"{name}{constraint}")
                    elif isinstance(constraint, dict) and "version" in constraint:
                        dependencies.append(f"{name}{constraint['version']}")
                    else:
                        dependencies.append(name)

        return dependencies

    @staticmethod
    def generate_pyproject_toml(data: Dict[str, Any]) -> str:
        """
        Generuje zawartość pliku pyproject.toml na podstawie danych.

        Args:
            data: Dane w formacie schematu poetry

        Returns:
            Zawartość pliku pyproject.toml
        """
        # Tworzymy kopię danych, aby nie modyfikować oryginału
        poetry_data = data.copy()

        # Usuwamy pole format, które nie jest częścią standardowego pliku pyproject.toml
        if "format" in poetry_data:
            del poetry_data["format"]

        # Tworzymy strukturę pyproject.toml
        pyproject = {
            "tool": {"poetry": poetry_data},
            "build-system": {
                "requires": ["poetry-core>=1.0.0"],
                "build-backend": "poetry.core.masonry.api",
            },
        }

        # Konwertujemy dane do TOML
        return toml.dumps(pyproject)

    @staticmethod
    def write_pyproject_toml(
        data: Dict[str, Any], output_path: Union[str, Path]
    ) -> Path:
        """
        Zapisuje dane do pliku pyproject.toml.

        Args:
            data: Dane w formacie schematu poetry
            output_path: Ścieżka do pliku wyjściowego

        Returns:
            Ścieżka do zapisanego pliku
        """
        output_path = Path(output_path)

        # Tworzymy katalogi, jeśli nie istnieją
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = PoetrySchema.generate_pyproject_toml(data)

        with open(output_path, "w") as f:
            f.write(content)

        return output_path

    @staticmethod
    def convert_from_pip(
        pip_data: Dict[str, Any],
        project_name: str = "myproject",
        version: str = "0.1.0",
    ) -> Dict[str, Any]:
        """
        Konwertuje dane z formatu pip do formatu poetry.

        Args:
            pip_data: Dane w formacie pip
            project_name: Nazwa projektu
            version: Wersja projektu

        Returns:
            Dane w formacie poetry
        """
        # Tworzymy podstawową strukturę danych poetry
        poetry_data = {
            "name": project_name,
            "version": version,
            "description": "",
            "authors": ["Your Name <your.email@example.com>"],
            "readme": "README.md",
            "dependencies": {},
            "dev-dependencies": {},
            "format": "poetry",
        }

        # Pobieramy zależności - obsługujemy zarówno klucz "dependencies" jak i "requirements"
        dependencies = pip_data.get("requirements", pip_data.get("dependencies", []))

        # Konwertujemy zależności
        for dep in dependencies:
            # Obsługa przypadku, gdy dep jest słownikiem (rozszerzony format zależności)
            if isinstance(dep, dict):
                if dep.get("type") == "package":
                    package_name = dep["name"]

                    # Sprawdzamy, czy jest specyfikacja wersji
                    if "version_spec" in dep:
                        operator = dep["version_spec"]["operator"]
                        version_val = dep["version_spec"]["version"]
                        poetry_data["dependencies"][
                            package_name
                        ] = f"{operator}{version_val}"
                    else:
                        poetry_data["dependencies"][package_name] = "*"

                # Pomijamy komentarze i opcje
                continue

            # Obsługa przypadku, gdy dep jest stringiem (prosty format zależności)
            # Pomijamy komentarze
            if isinstance(dep, str):
                if dep.startswith("#"):
                    continue

                # Parsujemy zależność
                if "==" in dep:
                    name, version_val = dep.split("==", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f"=={version_val.strip()}"
                elif ">=" in dep:
                    name, version_val = dep.split(">=", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f">={version_val.strip()}"
                elif "<=" in dep:
                    name, version_val = dep.split("<=", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f"<={version_val.strip()}"
                elif ">" in dep:
                    name, version_val = dep.split(">", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f">{version_val.strip()}"
                elif "<" in dep:
                    name, version_val = dep.split("<", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f"<{version_val.strip()}"
                elif "~=" in dep:
                    name, version_val = dep.split("~=", 1)
                    poetry_data["dependencies"][
                        name.strip()
                    ] = f"~{version_val.strip()}"
                elif "@" in dep:
                    # URL dependency
                    name, url = dep.split("@", 1)
                    poetry_data["dependencies"][name.strip()] = {"url": url.strip()}
                elif dep.startswith("git+"):
                    # Git dependency
                    url = dep[4:]
                    if "#egg=" in url:
                        url, egg = url.split("#egg=", 1)
                        name = egg.strip()
                        if "@" in url:
                            url, rev = url.split("@", 1)
                            poetry_data["dependencies"][name] = {"git": url, "rev": rev}
                        else:
                            poetry_data["dependencies"][name] = {"git": url}
                    else:
                        # Nieznany format git, dodajemy jako string
                        poetry_data["dependencies"][dep] = "*"
                else:
                    # Prosta zależność bez wersji
                    poetry_data["dependencies"][dep.strip()] = "*"

        return poetry_data
