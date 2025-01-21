# Sample Topographic Data Files

This directory contains example data files demonstrating different use cases for the topographic mapping tool.

## File Format

All files are CSV format with the following conventions:
- Numeric values represent height measurements
- `B` represents boundary points
- `X` represents missing measurements that will be interpolated

## Sample Files

### simple_hill.csv
- A simple hill pattern with measurements in inches
- Peak height of 60 inches (5 feet)
- Regular grid with 12-inch (1 foot) spacing between measurements
- No missing data
- Good for basic testing and visualization

### valley_with_missing.csv
- A valley pattern with measurements in inches
- Depth range from 6 to 54 inches
- Contains several missing measurements (marked with X)
- Demonstrates interpolation capabilities
- Irregular terrain with gentle slopes

### ridge_cm.csv
- A ridge pattern with measurements in centimeters
- Peak height of 600 cm (6 meters)
- Grid spacing of 30 cm between measurements
- Demonstrates using metric measurements
- Symmetrical pattern with realistic slopes
- Good for testing unit conversion (e.g., display in meters or feet)

## Usage Examples

To process any of these files:

```python
from topogen import TopoConfig, process_topography

# Configure the processing
config = TopoConfig(
    grid_spacing=2.0,
    input_units="in",
    output_units="ft"
)

# Process the data
with open("input.csv", "r") as f:
    process_topography(f, config)
```

## Grid Spacing and Scale

The sample files use realistic proportions:
- For imperial measurements: 12-inch (1 foot) spacing between points
- For metric measurements: 30cm spacing between points
- Height variations are gradual, reflecting natural terrain
- Slopes are typically less than 45 degrees 