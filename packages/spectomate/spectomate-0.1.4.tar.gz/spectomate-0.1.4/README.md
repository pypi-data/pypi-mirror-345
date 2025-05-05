# Spectomate

Spectomate to narzędzie do konwersji projektów między różnymi formatami zarządzania pakietami w Pythonie (pip, conda, poetry).

## Kluczowe cechy Spectomate:

1. **Modułowa architektura** - każdy konwerter jest oddzielnym modułem implementującym wspólny interfejs
2. **Wsparcie dla istniejących narzędzi** - możliwość integracji z zewnętrznymi narzędziami konwersji
3. **Elastyczny system rozszerzeń** - łatwe dodawanie nowych konwerterów bez modyfikacji kodu bazowego
4. **Kompleksowe wsparcie formatów**:
   - pip (requirements.txt)
   - conda (environment.yml)
   - poetry (pyproject.toml)

## Instalacja

```bash
# Instalacja podstawowa
pip install spectomate
```

## Jak używać Spectomate:

### Interfejs wiersza poleceń (CLI)

```bash
# Wyświetlenie dostępnych konwerterów
spectomate --list

# Konwersja z pip do conda
spectomate -s pip -t conda -i requirements.txt -o environment.yml --env-name myproject

# Konwersja z conda do pip
spectomate -s conda -t pip -i environment.yml -o requirements.txt

# Konwersja z pip do poetry
spectomate -s pip -t poetry -i requirements.txt -o pyproject.toml --project-name "mój-projekt" --version "0.1.0"
```

### Użycie programistyczne

```python
from spectomate.converters.pip_to_conda import PipToCondaConverter

# Konwersja z pip do conda
converter = PipToCondaConverter(
    source_file="requirements.txt",
    target_file="environment.yml",
    options={"env_name": "myproject"}
)
result_path = converter.execute()
print(f"Plik wyjściowy: {result_path}")
```

## Struktura projektu

```
spectomate/
├── __init__.py
├── cli.py
├── core/
│   ├── __init__.py
│   ├── base_converter.py
│   ├── registry.py
│   └── utils.py
├── converters/
│   ├── __init__.py
│   ├── pip_to_conda.py
│   ├── pip_to_poetry.py
│   ├── conda_to_pip.py
│   └── ...
├── schemas/
│   ├── __init__.py
│   ├── pip_schema.py
│   ├── conda_schema.py
│   ├── poetry_schema.py
│   └── ...
└── tests/
    ├── __init__.py
    ├── test_pip_to_conda.py
    ├── test_conda_to_pip.py
    └── ...
```

## Rozszerzalność

Spectomate pozwala na łatwe dodawanie nowych konwerterów przez:
1. Utworzenie nowego modułu w katalogu `converters/`
2. Implementację klasy dziedziczącej po `BaseConverter`
3. Implementację metod `read_source`, `convert` i `write_target`
4. Rejestrację konwertera w `ConverterRegistry`

## Rozwój projektu

### Wymagania dla deweloperów

```bash
# Klonowanie repozytorium
git clone https://github.com/spectomate/python.git
cd python

# Instalacja w trybie deweloperskim
pip install -e .
```

### Aktualizacja wersji i publikacja

Projekt wykorzystuje skrypty w katalogu `update/` do zarządzania wersjami i publikacji:

```bash
# Aktualizacja wersji i publikacja
bash update/version.sh
```

Skrypt wykonuje następujące operacje:
1. Aktualizuje numer wersji w plikach źródłowych
2. Generuje wpis w CHANGELOG.md
3. Publikuje zmiany na GitHub
4. Publikuje pakiet na PyPI

Więcej informacji na temat procesu publikacji znajduje się w [update/README.md](update/README.md).

## Licencja

Ten projekt jest udostępniany na licencji MIT. Szczegółowe informacje znajdują się w pliku LICENSE.
