---
title: "Spectomate - Python Package Management Format Converter"
description: "A tool for converting projects between different Python package management formats (pip, conda, poetry)"
author: "Tom Sapletta"
keywords: "python, package management, pip, conda, poetry, converter, requirements.txt, environment.yml, pyproject.toml"
lang: "en"
image: "https://github.com/spectomate/python/raw/main/docs/diagrams/logo.png"
---

# Spectomate

Spectomate is a tool for converting projects between different Python package management formats (pip, conda, poetry).

## Key Features of Spectomate:

1. **Modular architecture** - each converter is a separate module implementing a common interface
2. **Support for existing tools** - ability to integrate with external conversion tools
3. **Flexible extension system** - easy addition of new converters without modifying the base code
4. **Comprehensive format support**:
   - pip (requirements.txt)
   - conda (environment.yml)
   - poetry (pyproject.toml)
5. **Project management tools**:
   - Package version updating
   - Testing and linting automation
   - Publication to PyPI

## Installation

```bash
# Basic installation
pip install spectomate
```

## How to Use Spectomate:

### Command Line Interface (CLI)

#### Format Conversion

```bash
# Display available converters
spectomate --list

# Convert from pip to conda
spectomate -s pip -t conda -i requirements.txt -o environment.yml --env-name myproject

# Convert from conda to pip
spectomate -s conda -t pip -i environment.yml -o requirements.txt

# Convert from pip to poetry
spectomate -s pip -t poetry -i requirements.txt -o pyproject.toml --project-name "my-project" --version "0.1.0"
```

#### Package Update and Management

```bash
# Full package update with publication
spectomate update

# Interactive update with project analysis
spectomate update --interactive

# Only analyze project without updating
spectomate update --analyze-only

# Update without publishing to PyPI
spectomate update --no-publish

# Update without type checking
spectomate update --no-mypy

# Update without running tests
spectomate update --no-test

# Update without linting
spectomate update --no-lint

# Update without checking Git submodules
spectomate update --no-submodules

# Update with verbose output
spectomate update --verbose
```

### Programmatic Usage

```python
from spectomate.converters.pip_to_conda import PipToCondaConverter

# Convert from pip to conda
converter = PipToCondaConverter(
    source_file="requirements.txt",
    target_file="environment.yml",
    options={"env_name": "myproject"}
)
result_path = converter.execute()
print(f"Output file: {result_path}")
```

## Project Structure

```
spectomate/
├── __init__.py                  # Package initialization
├── cli.py                       # Command line interface
├── core/                        # Core components
│   ├── __init__.py
│   ├── base_converter.py        # Base class for converters
│   ├── registry.py              # Converter registration system
│   └── utils.py                 # Helper functions
├── converters/                  # Converter implementations
│   ├── __init__.py
│   ├── conda_to_pip.py          # Converter from conda to pip
│   ├── pip_to_conda.py          # Converter from pip to conda
│   ├── pip_to_poetry.py         # Converter from pip to poetry
│   └── ...
└── schemas/                     # Data schemas for formats
    ├── __init__.py
    ├── conda_schema.py          # Schema for conda format
    ├── pip_schema.py            # Schema for pip format
    ├── poetry_schema.py         # Schema for poetry format
    └── ...
```

## Documentation

Detailed documentation is available in the `docs/` directory:

- [Architecture](docs/ARCHITECTURE.md) - description of the system architecture
- [Converters](docs/CONVERTERS.md) - description of available converters and their implementation
- [Schemas](docs/SCHEMAS.md) - description of data schemas for different formats

### Diagrams

Visual documentation in the form of Mermaid diagrams:

- [Architecture Diagram](docs/diagrams/ARCHITECTURE_DIAGRAM.md) - class structure and relationships between components
- [Data Flow Diagram](docs/diagrams/DATA_FLOW_DIAGRAM.md) - data flow during the conversion process
- [Sequence Diagram](docs/diagrams/SEQUENCE_DIAGRAM.md) - interactions between components during conversion
- [Extension Diagram](docs/diagrams/EXTENSION_DIAGRAM.md) - process of adding new converters and formats

*Note: Polish documentation is available in the [docs/pl/](docs/pl/) directory.*

## Extending Spectomate

Spectomate is designed as a modular system that can be easily extended with new formats and converters. To add a new converter:

1. Create a new converter class inheriting from `BaseConverter`
2. Implement the required abstract methods:
   - `get_source_format()` - returns the source format identifier
   - `get_target_format()` - returns the target format identifier
   - `read_source()` - reads the source file
   - `convert()` - converts the data
   - `write_target()` - writes the data to the target file
3. Register the converter using the `@register_converter` decorator

Detailed information on creating custom converters can be found in the [converters documentation](docs/CONVERTERS.md).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
