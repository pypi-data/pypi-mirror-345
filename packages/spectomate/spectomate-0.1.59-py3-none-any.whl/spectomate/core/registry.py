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
    def get_converters(
        cls, input_format: Optional[str] = None, output_format: Optional[str] = None
    ) -> List[Type[BaseConverter]]:
        """
        Zwraca listę wszystkich dostępnych konwerterów, opcjonalnie filtrowanych według formatu.

        Args:
            input_format: Opcjonalny filtr formatu wejściowego
            output_format: Opcjonalny filtr formatu wyjściowego

        Returns:
            Lista konwerterów spełniających kryteria
        """
        converters = []

        for (source, target), converter_class in cls._converters.items():
            if input_format is not None and source != input_format:
                continue
            if output_format is not None and target != output_format:
                continue
            converters.append(converter_class)

        return converters

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

    @classmethod
    def get_input_formats(cls) -> Set[str]:
        """
        Zwraca zbiór wszystkich dostępnych formatów wejściowych.

        Alias dla get_source_formats().

        Returns:
            Zbiór nazw formatów wejściowych
        """
        return cls.get_source_formats()

    @classmethod
    def get_output_formats(cls) -> Set[str]:
        """
        Zwraca zbiór wszystkich dostępnych formatów wyjściowych.

        Alias dla get_target_formats().

        Returns:
            Zbiór nazw formatów wyjściowych
        """
        return cls.get_target_formats()

    @classmethod
    def has_converter(cls, source_format: str, target_format: str) -> bool:
        """
        Sprawdza, czy istnieje konwerter dla podanej pary formatów.

        Args:
            source_format: Format źródłowy
            target_format: Format docelowy

        Returns:
            True jeśli konwerter istnieje, False w przeciwnym wypadku
        """
        return cls.get_converter(source_format, target_format) is not None


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
