"""
Spectomate - modularny konwerter pakietów Python

Narzędzie do konwersji między różnymi formatami zarządzania pakietami w Pythonie.
"""

__version__ = "0.1.4"
__author__ = "Spectomate Team"

from spectomate.core.base_converter import BaseConverter
from spectomate.core.registry import ConverterRegistry

# Inicjalizacja rejestru konwerterów
registry = ConverterRegistry()

# Importy dla wygodnego dostępu do API
from spectomate.converters import *  # noqa
