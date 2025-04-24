# Topogen

A Python package for processing and visualizing topographic survey data. Convert raw elevation measurements into beautiful contour maps with support for interpolation, unit conversion, and customizable visualization options.

Written with extensive help from Cursor IDE, since I'm not a civil engineer or surveyor. Tests are written to generate maps which can be sanity-checked by eye; there may be bugs I haven't spotted, though, so *caveat emptor*.

## Features

- Process CSV files containing elevation measurements
- Interpolate missing data points using neighbor averaging
- Convert between different measurement units (inches, feet, centimeters, meters)
- Generate contour maps with customizable visualization settings
- Support for boundary markers and data transformation

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   or:
   ```
   pip install .
   ```

2. Prepare your input CSV file with elevation measurements. The file should contain:
   - Numbers for elevation measurements
   - 'X' for missing data points (will be interpolated)
   - 'B' for boundary markers

3. Run the application:
   ```
   python -m topogen.cli input.csv --output map.png --units ft --grid-spacing 2.0
   ```

   Options:
   - `input.csv`: Path to your input CSV file
   - `--output`: Path to save the visualization (optional)
   - `--units`: Output units ('in', 'ft', 'cm', 'm'), default: ft
   - `--grid-spacing`: Distance between measurements in input units, default: 2.0

## Project Layout

- `src/topogen/`: Core package
  - `main.py`: Main processing pipeline
  - `data_processing/`: CSV parsing and data transformation
  - `interpolation/`: Missing data interpolation
  - `visualization/`: Contour map generation
  - `config/`: Configuration management
  - `cli.py`: Command-line interface
- `tests/`: Test files and test data
- `samples/`: Example input files
- `pyproject.toml`: Package configuration
- `requirements.txt`: Dependencies

