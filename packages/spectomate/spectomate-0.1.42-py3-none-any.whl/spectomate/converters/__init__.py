"""
Moduł zawierający implementacje konwerterów dla różnych formatów pakietów.
"""

from spectomate.converters.conda_to_pip import CondaToPipConverter

# Importujemy wszystkie konwertery, aby zarejestrowały się w ConverterRegistry
from spectomate.converters.pip_to_conda import PipToCondaConverter
from spectomate.converters.pip_to_poetry import PipToPoetryConverter

# Tymczasowo usunięto import nieistniejących konwerterów
# from spectomate.converters.pip_to_pipenv import PipToPipenvConverter
# from spectomate.converters.pip_to_pdm import PipToPdmConverter
# from spectomate.converters.poetry_to_pip import PoetryToPipConverter
# from spectomate.converters.poetry_to_conda import PoetryToCondaConverter

# Importujemy zewnętrzne konwertery
try:
    from spectomate.converters.external_converters import (
        ExternalDephellConverter,
        ExternalPoetry2CondaConverter,
        ExternalReq2TomlConverter,
    )
except ImportError:
    pass  # Zewnętrzne konwertery są opcjonalne
