# GeoCleanr

<p align="center">
  <img src="assets/geocleanr_logo.jpg" alt="GeoCleanr logo" width="220">
</p>

A Lightweight Python Library for Cleaning Geospatial Coordinates

## Overview
GeoCleanr is a lightweight, educational Python library for validating, fixing, reporting, and visualizing latitude/longitude data in raw tabular datasets (e.g. CSV files).
It is designed for students and researchers working with real-world, messy geospatial data before using full GIS tools.

GeoCleanr focuses specifically on coordinate-level data quality, a common problem not directly addressed by generic data libraries or heavy GIS frameworks.

## Key Features
- **Validation**: Detects missing, invalid, out-of-range, or swapped latitude/longitude values
- **Automatic fixing**: Clips coordinates to valid bounds, swaps axes when needed, and applies fallback values
- **Reporting**: Generates human-readable summaries of detected issues (Markdown/text)
- **Visualization**: Provides a simple ASCII heatmap for spatial overview
- **CLI support**: Run validation and reporting from the terminal on CSV or NDJSON data
- **Testing**: Includes automated tests for core functionality

## Typical Workflow
1. Load a CSV or tabular dataset
2. Validate latitude/longitude fields
3. Automatically fix common coordinate issues
4. Generate a summary report
5. Export cleaned data for further analysis (e.g. GIS, pandas)

## Installation
Using pip
```bash
pip install -r requirements.txt
pip install -e .
```

Using conda
```bash
conda env create -f environment.yml
conda activate geocleanr
pip install -e .
```

## Quick Verification (for reviewers)
To quickly verify that the project works:
```bash
pip install -r requirements.txt
pip install -e .
python -m pytest
```

All tests should pass.

For a functional demonstration, open:

`examples/GeoCleanr_quickstart.md`

or the example Jupyter notebook in the `examples/` folder.

## Example Usage (Python)
```python
from geocleanr import GeometryValidator, CoordinateFixer

validator = GeometryValidator(lat_field="latitude", lon_field="longitude")
issues = validator.validate(rows)

fixer = CoordinateFixer(lat_field="latitude", lon_field="longitude")
cleaned = [fixer.fix_record(r).record for r in rows]
```

## Project Structure
```
GeoCleanr/
|-- src/            # Core library code
|-- tests/          # Automated tests
|-- examples/       # Example notebook and usage guide
|-- assets/         # Supporting assets
|-- environment.yml # Conda environment
|-- requirements.txt
|-- pyproject.toml
`-- README.md
```

## Intended Audience
GeoCleanr is intended for students, researchers, and analysts who need to clean and validate geospatial coordinates in raw CSV or tabular data before further analysis or GIS processing.

## Limitations
GeoCleanr focuses on coordinate-level validation and does not replace full GIS or CRS-aware validation tools such as GeoPandas or QGIS.

## License
This project is released under the MIT License.
