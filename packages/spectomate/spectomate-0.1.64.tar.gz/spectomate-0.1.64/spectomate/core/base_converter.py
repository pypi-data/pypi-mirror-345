"""
Moduł bazowy konwertera definiujący interfejs dla wszystkich konwerterów.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union


class BaseConverter(ABC):
    """
    Klasa bazowa dla wszystkich konwerterów formatów pakietów.

    Każdy konwerter musi implementować metody read_source, convert, i write_target.
    """

    def __init__(
        self,
        source_file: Optional[Union[str, Path]] = None,
        target_file: Optional[Union[str, Path]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Inicjalizacja konwertera.

        Args:
            source_file: Ścieżka do pliku źródłowego
            target_file: Ścieżka do pliku docelowego
            options: Dodatkowe opcje konfiguracyjne
        """
        self.source_file = Path(source_file) if source_file else None
        self.target_file = Path(target_file) if target_file else None
        self.options = options or {}
        self.source_data = None
        self.target_data = None

    @property
    def source_format(self) -> str:
        """Format źródłowy obsługiwany przez konwerter."""
        return self.get_source_format()

    @property
    def target_format(self) -> str:
        """Format docelowy obsługiwany przez konwerter."""
        return self.get_target_format()

    @staticmethod
    @abstractmethod
    def get_source_format() -> str:
        """Zwraca identyfikator formatu źródłowego."""
        pass

    @staticmethod
    @abstractmethod
    def get_target_format() -> str:
        """Zwraca identyfikator formatu docelowego."""
        pass

    @abstractmethod
    def read_source(self) -> Dict[str, Any]:
        """
        Odczytuje dane z pliku źródłowego.

        Returns:
            Odczytane dane w ustandaryzowanym formacie słownikowym
        """
        pass

    @abstractmethod
    def convert(self, source_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Konwertuje dane ze źródłowego formatu na docelowy.

        Args:
            source_data: Dane w formacie źródłowym (opcjonalnie, jeśli nie podano używa self.source_data)

        Returns:
            Przekonwertowane dane w formacie docelowym
        """
        pass

    @abstractmethod
    def write_target(self, target_data: Optional[Dict[str, Any]] = None) -> Path:
        """
        Zapisuje przekonwertowane dane do pliku docelowego.

        Args:
            target_data: Dane w formacie docelowym (opcjonalnie, jeśli nie podano używa self.target_data)

        Returns:
            Ścieżka do zapisanego pliku
        """
        pass

    def execute(self) -> Path:
        """
        Wykonuje pełny proces konwersji: odczyt, konwersja, zapis.

        Returns:
            Ścieżka do zapisanego pliku docelowego
        """
        self.source_data = self.read_source()
        self.target_data = self.convert(self.source_data)
        return self.write_target(self.target_data)
