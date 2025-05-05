# pytwincatparser
A Python package for parsing TwinCAT PLC files (TcPOU, TcDUT, TcIO).

## Description

This package provides tools to parse and work with TwinCAT PLC files. It uses xsdata to handle XML parsing. Be aware, that this is a python lib written by a beginner with help of AI assisted programming. My main work task is to design and program industrial machines, not develop python programms!

## Features

- Parse TwinCAT PLC files (.TcPOU, .TcDUT, .TcIO)
- Access POU (Program Organization Units), DUT (Data Unit Types), and ITF (Interfaces)
- Extract declarations, implementations, methods, and properties
- Extract VAR Blocks
- Extract Return Values
- Extract Comments
- Generate HTML documentation for TwinCAT objects

## Installation

This project uses [uv](https://github.com/astral-sh/uv) as its package manager. To set up the development environment:

### Windows

```powershell
# Install uv if you don't have it
pip install uv

# Run the setup script
.\setup_uv.ps1
```


## Usage

```python
from pytwincatparser.TwincatParser import TwinCatLoader

# Initialize the loader with the path to TwinCAT files
loader = TwinCatLoader(search_path="path/to/twincat/files")

# Load all TwinCAT files
loader.load()

# Get a specific object by name
pou = loader.getItemByName("FB_Base")

# Get a method by name
method = loader.getItemByName("FB_Base._ConfigureAlarm")

# Get a property by name
property = loader.getItemByName("FB_Base.DesignationName")

# Get all loaded objects
all_objects = loader.getAllItems()
```

Look in the example folder!

### Generating Documentation

You can generate HTML documentation for your TwinCAT objects using the `generate_docs` module:

```python
from pytwincatparser.generate_docs import generate_documentation

# Generate documentation
generate_documentation(
    search_path="path/to/twincat/files",
    output_dir="path/to/output/directory",
    templates_dir="path/to/templates"  # Optional, defaults to 'templates' in the package directory
)
```

This will generate HTML documentation for all TwinCAT objects found in the search path. The documentation includes:

- Object details (name, type, etc.)
- Documentation comments
- Variable sections
- Methods and properties
- Implementation code

See the `examples/generate_documentation.py` script for a complete example.

## Requirements

- Python 3.11
- lxml >= 5.3.0
- xsdata[lxml] >= 24.12
- jinja2 >= 3.1.6

## License

MIT
