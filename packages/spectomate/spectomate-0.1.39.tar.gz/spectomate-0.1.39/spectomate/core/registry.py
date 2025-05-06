"""
Rejestr konwerterów umożliwiający dynamiczne rejestrowanie i odnajdywanie dostępnych konwerterów.
"""

from typing import Dict, List, Optional, Set, Tuple, Type

from spectomate.core.base_converter import BaseConverter


class ConverterRegistry:
    """
    Rejestr konwerterów zarządzający dostępnymi konwerterami.
    """

    _converters: Dict[Tuple[str, str], Type[BaseConverter]] = {}

    @classmethod
    def register(cls, converter_class: Type[BaseConverter]) -> None:
        """
        Rejestruje klasę konwertera w rejestrze.

        Args:
            converter_class: Klasa konwertera do zarejestrowania
        """
        source_format = converter_class.get_source_format()
        target_format = converter_class.get_target_format()
        key = (source_format, target_format)

        cls._converters[key] = converter_class

    @classmethod
    def get_converter(
        cls, source_format: str, target_format: str
    ) -> Optional[Type[BaseConverter]]:
        """
        Zwraca klasę konwertera dla podanej pary formatów.

        Args:
            source_format: Format źródłowy
            target_format: Format docelowy

        Returns:
            Klasa konwertera lub None jeśli nie znaleziono
        """
        key = (source_format, target_format)
        return cls._converters.get(key)

    @classmethod
    def get_converters(cls) -> List[Tuple[str, str]]:
        """
        Zwraca listę wszystkich dostępnych konwersji.

        Returns:
            Lista par (format_źródłowy, format_docelowy)
        """
        return list(cls._converters.keys())

    @classmethod
    def get_source_formats(cls) -> Set[str]:
        """
        Zwraca zbiór wszystkich dostępnych formatów źródłowych.

        Returns:
            Zbiór nazw formatów źródłowych
        """
        return {source for source, _ in cls._converters.keys()}

    @classmethod
    def get_target_formats(cls) -> Set[str]:
        """
        Zwraca zbiór wszystkich dostępnych formatów docelowych.

        Returns:
            Zbiór nazw formatów docelowych
        """
        return {target for _, target in cls._converters.keys()}

    @classmethod
    def get_all_formats(cls) -> Set[str]:
        """
        Zwraca zbiór wszystkich dostępnych formatów (źródłowych i docelowych).

        Returns:
            Zbiór nazw formatów
        """
        sources = cls.get_source_formats()
        targets = cls.get_target_formats()
        return sources.union(targets)


def register_converter(converter_class: Type[BaseConverter]) -> Type[BaseConverter]:
    """
    Dekorator do rejestrowania konwerterów.

    Args:
        converter_class: Klasa konwertera do zarejestrowania

    Returns:
        Niezmieniona klasa konwertera
    """
    ConverterRegistry.register(converter_class)
    return converter_class
