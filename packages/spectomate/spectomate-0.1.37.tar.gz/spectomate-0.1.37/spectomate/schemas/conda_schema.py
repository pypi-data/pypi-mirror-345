"""
Schemat dla formatu conda (environment.yml).
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml


class CondaSchema:
    """
    Klasa definiująca schemat dla formatu conda (environment.yml).
    """

    @staticmethod
    def parse_file(file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Parsuje plik environment.yml.

        Args:
            file_path: Ścieżka do pliku environment.yml

        Returns:
            Słownik z informacjami o środowisku conda
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise FileNotFoundError(f"Plik nie istnieje: {file_path}")

        with open(file_path, "r") as f:
            try:
                conda_env = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise ValueError(f"Błąd parsowania pliku YAML: {e}")

        # Sprawdzamy, czy plik ma wymagane pola
        if not isinstance(conda_env, dict):
            raise ValueError("Plik environment.yml musi zawierać słownik")

        # Dodajemy domyślne wartości, jeśli brakuje kluczy
        if "name" not in conda_env:
            conda_env["name"] = "myenv"

        if "channels" not in conda_env:
            conda_env["channels"] = ["defaults"]

        if "dependencies" not in conda_env:
            conda_env["dependencies"] = []

        # Dodajemy informację o formacie
        conda_env["format"] = "conda"

        return conda_env

    @staticmethod
    def extract_pip_dependencies(conda_env: Dict[str, Any]) -> List[str]:
        """
        Wyodrębnia zależności pip z środowiska conda.

        Args:
            conda_env: Słownik z informacjami o środowisku conda

        Returns:
            Lista zależności pip
        """
        pip_deps = []

        dependencies = conda_env.get("dependencies", [])

        for dep in dependencies:
            if isinstance(dep, dict) and "pip" in dep:
                pip_deps.extend(dep["pip"])
                break

        return pip_deps

    @staticmethod
    def extract_conda_dependencies(conda_env: Dict[str, Any]) -> List[str]:
        """
        Wyodrębnia zależności conda z środowiska conda.

        Args:
            conda_env: Słownik z informacjami o środowisku conda

        Returns:
            Lista zależności conda
        """
        conda_deps = []

        dependencies = conda_env.get("dependencies", [])

        for dep in dependencies:
            if isinstance(dep, str):
                conda_deps.append(dep)

        return conda_deps

    @staticmethod
    def generate_environment_yml(data: Dict[str, Any]) -> str:
        """
        Generuje zawartość pliku environment.yml na podstawie danych.

        Args:
            data: Dane w formacie schematu conda

        Returns:
            Zawartość pliku environment.yml
        """
        # Tworzymy kopię danych, aby nie modyfikować oryginału
        env_data = data.copy()

        # Usuwamy pole format, które nie jest częścią standardowego pliku environment.yml
        if "format" in env_data:
            del env_data["format"]

        # Konwertujemy dane do YAML
        return yaml.dump(env_data, default_flow_style=False, sort_keys=False)

    @staticmethod
    def write_environment_yml(
        data: Dict[str, Any], output_path: Union[str, Path]
    ) -> Path:
        """
        Zapisuje dane do pliku environment.yml.

        Args:
            data: Dane w formacie schematu conda
            output_path: Ścieżka do pliku wyjściowego

        Returns:
            Ścieżka do zapisanego pliku
        """
        output_path = Path(output_path)

        # Tworzymy katalogi, jeśli nie istnieją
        output_path.parent.mkdir(parents=True, exist_ok=True)

        content = CondaSchema.generate_environment_yml(data)

        with open(output_path, "w") as f:
            f.write(content)

        return output_path

    @staticmethod
    def merge_environments(
        env1: Dict[str, Any], env2: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Łączy dwa środowiska conda.

        Args:
            env1: Pierwsze środowisko
            env2: Drugie środowisko

        Returns:
            Połączone środowisko
        """
        # Tworzymy kopię pierwszego środowiska
        merged_env = env1.copy()

        # Łączymy kanały
        channels1 = set(env1.get("channels", []))
        channels2 = set(env2.get("channels", []))
        merged_env["channels"] = list(channels1.union(channels2))

        # Łączymy zależności conda
        conda_deps1 = set(CondaSchema.extract_conda_dependencies(env1))
        conda_deps2 = set(CondaSchema.extract_conda_dependencies(env2))

        # Łączymy zależności pip
        pip_deps1 = set(CondaSchema.extract_pip_dependencies(env1))
        pip_deps2 = set(CondaSchema.extract_pip_dependencies(env2))

        # Tworzymy nową listę zależności
        merged_deps = list(conda_deps1.union(conda_deps2))
        merged_pip_deps = list(pip_deps1.union(pip_deps2))

        if merged_pip_deps:
            merged_deps.append({"pip": merged_pip_deps})

        merged_env["dependencies"] = merged_deps

        return merged_env
