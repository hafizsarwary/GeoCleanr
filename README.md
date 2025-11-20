# GeoCleanr

<p align="center">
  <img src="assets/geocleanr_logo.jpg" alt="GeoCleanr logo" width="220">
</p>

GeoCleanr is a lightweight toolkit that demonstrates how to validate, repair, report on, and visualize simple geospatial coordinate data. The project intentionally keeps dependencies minimal so it can run anywhere while still modeling a clean package layout.

## Features
- **Validation**: Catch missing coordinates, impossible latitude/longitude ranges, and inconsistent precision with `geocleanr.validator`.
- **Fixing**: Auto-correct obvious coordinate issues such as swapped axes or clipped values using `geocleanr.fixer`.
- **Reporting**: Produce concise summaries or Markdown reports that can be shared with analysts and engineers.
- **Visualization**: Render a quick ASCII heatmap for exploratory checks without pulling heavy plotting libraries.
- **CLI**: Run validations and fixes from the terminal against newline-delimited JSON or CSV data.

## Project layout
```
geocleanr/
|-- README.md
|-- LICENSE
|-- requirements.txt
|-- environment.yml
|-- pyproject.toml
|-- src/
|   `-- geocleanr/
|       |-- __init__.py
|       |-- validator.py
|       |-- fixer.py
|       |-- reporter.py
|       |-- visualizer.py
|       `-- cli.py
|-- tests/
|   |-- __init__.py
|   |-- test_validator.py
|   |-- test_fixer.py
|   `-- test_end_to_end.py
`-- examples/
    `-- GeoCleanr_quickstart.md
```

## Getting started
1. Create a virtual environment and install the package:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the CLI against a CSV file containing `lat` and `lon` columns:
   ```bash
   python -m geocleanr.cli --input sample.csv --format csv --report report.md
   ```
3. Explore the quickstart in `examples/GeoCleanr_quickstart.md` for a guided workflow.

## Development
- Install the project in editable mode with `pip install -e .` for rapid iteration.
- Run tests with `pytest`.
- The codebase follows a simple service-object style so new validators or fixers can be added without touching the CLI.
