# dccQuantities

dccQuantities is a Python library designed for users of PTB’s Digital Calibration Certificates (DCC) in XML format. It provides an object‑oriented interface to parse, serialize, and manipulate calibration data with full support for uncertainties and units. Arithmetic works naturally on scalars, scalar‑vector mixes, and same‑length vectors element‑wise, preserving uncertainty propagation and metadata throughout.

---

## Key Features

- **DCC XML Parsing & Serialization**  
  Import certificates from XML into Python objects and export back to XML, JSON, CSV, Excel, or pandas DataFrames.

- **Uncertainty & Unit Awareness**  
  All quantity objects wrap values as `ufloat` (via `metas_unclib`) and units via `dsiUnits`, ensuring correct propagation in calculations.

- **Object‑Oriented Arithmetic**  
  Standard operators (`+`, `-`, `*`, `/`, `**`) are overloaded on:
  - **`DccQuantityType`**: single or tabulated quantities
  - **`SiRealList`**, **`SiComplexList`**, **`SiHybrid`**: 1D/2D arrays

- **Tables & Fancy Indexing**
The classes `DccLongTable` and `DccFlatTable` transparently implement numpy like indexing on efficient table structures described in the [table document](doc/tabellen/tables-de.md). Fancy indexing is supported, return type are always new tables.
---

## Installation

From PyPI (core functionality):
```bash
pip install dccQuantities
```

For development and testing:
```bash
git clone https://gitlab1.ptb.de/digitaldynamicmeasurement/dccQuantities.git
cd dccQuantities
pip install -e .[testing]
```

## Under the Hood (Test‑Driven Behavior)

The library’s design is guided by its test suite:

1. **Core Parsing** (`tests/test_parser.py`): reads `<DccQuantityTable>` and `<DccQuantityType>` elements, building Python objects.
2. **Naming** (`tests/test_dccName.py`): parses and normalizes `<DccName>` entries for multilingual support.
3. **Quantity Discovery** (`tests/test_quantityTypeCollector.py`): auto‑registers data handlers via `AbstractQuantityTypeData` subclasses.
5. **List Types** (`tests/test_SiRealList_*.py`): handles real, complex, and hybrid lists, including broadcasting and label merging.
6. **Table Flattening** (`tests/test_tables.py`): cover the tables.
7. **Round‑Trip Serialization** (`tests/test_serilizer.py`): ensures parse→serialize yields equivalent XML.
8. **JSON Interchange** (`tests/test_dccQuantTabJSONDumpingAndLoadingFromFile.json`): lossless JSON dump/load.

---

## Contributing & Contact

We welcome improvements, bug reports, and new features. To contribute:

1. **Fork** the repository.  
2. **Create** a feature branch.  
3. **Add** tests for new functionality.  
4. **Submit** a merge request.

We highly encourage direct personal contact for design discussions or questions. Feel free to create Issues, even if you think your question/comment is not worth an issue, it is allways!

Or reach out to the maintainer:
- **Benedikt Seeger**: benedikt.seeger@ptb.de
directly

## License

This project is licensed under the [LGPL‑2.1‑or‑later](LICENSE).

