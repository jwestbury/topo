#!/usr/bin/env python3

from typing import Callable, TextIO, Union, List
import csv
import numpy as np
from numpy.typing import NDArray
from ..config.config import TopoConfig

# Type aliases
NumericArray = NDArray[np.object_]  # Array that can contain floats, 'B', or np.nan

def parse_csv(file_like: TextIO, config: TopoConfig) -> NumericArray:
    """
    Read a CSV (file-like object) into a 2D NumPy array of objects.
    
    Args:
        file_like: A file-like object containing the CSV data
        config: TopoConfig instance with parsing settings
        
    Returns:
        np.ndarray: A 2D array with:
            - float for numeric entries
            - np.nan for 'X' (missing) or invalid numeric values
            - 'B' for boundary markers
            
    Raises:
        ValueError: If the file is empty or rows have inconsistent lengths
    """
    data_rows: List[List[Union[float, str]]] = []
    expected_cols: Union[int, None] = None
    reader = csv.reader(file_like)
    
    # Check if file is empty
    try:
        first_row = next(reader)
    except StopIteration:
        raise ValueError("Input CSV file is empty")
    
    # Process first row and set expected column count
    parsed_row: List[Union[float, str]] = []
    for cell in first_row:
        cell = cell.strip().upper()
        if cell == 'X':
            parsed_row.append(np.nan)
        elif cell == 'B':
            parsed_row.append('B')
        else:
            try:
                val = float(cell)
                parsed_row.append(val)
            except ValueError:
                parsed_row.append(np.nan)
    
    expected_cols = len(parsed_row)
    if expected_cols == 0:
        raise ValueError("First row is empty")
    data_rows.append(parsed_row)
    
    # Process remaining rows
    for row_idx, row in enumerate(reader, start=2):  # 2 because we already read row 1
        if len(row) != expected_cols:
            raise ValueError(f"Row {row_idx} has {len(row)} columns, expected {expected_cols}")
        
        parsed_row = []
        for cell in row:
            cell = cell.strip().upper()
            if cell == 'X':
                parsed_row.append(np.nan)
            elif cell == 'B':
                parsed_row.append('B')
            else:
                try:
                    val = float(cell)
                    parsed_row.append(val)
                except ValueError:
                    parsed_row.append(np.nan)
        data_rows.append(parsed_row)
    
    result = np.array(data_rows, dtype=object)
    
    # Validate minimum grid size
    if result.shape[0] < 2 or result.shape[1] < 2:
        raise ValueError(f"Grid size {result.shape} is too small. Minimum size is 2x2.")
    
    return result

def apply_to_numeric_values(data: NumericArray, func: Callable[[float], float]) -> NumericArray:
    """
    Apply a function to all numeric values in the array, ignoring boundaries ('B') and np.nan.
    
    Args:
        data: 2D NumPy array (dtype=object) containing numeric values, 'B' for boundaries, and np.nan
        func: Function to apply to each numeric value
        
    Returns:
        The modified array (modified in-place)
    """
    rows, cols = data.shape
    for r in range(rows):
        for c in range(cols):
            val = data[r, c]
            if isinstance(val, float) and not np.isnan(val):
                data[r, c] = func(val)
    return data

def find_min_value(data: NumericArray) -> float:
    """
    Find the minimum numeric value in the array, ignoring boundaries ('B') and np.nan.
    
    Args:
        data: 2D NumPy array (dtype=object)
        
    Returns:
        float: The minimum value found
        
    Raises:
        ValueError: If no valid numeric data is found
    """
    valid_values: List[float] = []
    rows, cols = data.shape
    for r in range(rows):
        for c in range(cols):
            val = data[r, c]
            if isinstance(val, float) and not np.isnan(val):
                valid_values.append(val)
    
    if not valid_values:
        raise ValueError("No valid numeric data found to determine minimum.")
    
    return min(valid_values)

def get_unit_conversion_factor(from_unit: str, to_unit: str) -> float:
    """
    Get the conversion factor between different units of measurement.
    Returns a factor that when multiplied by a value in from_unit gives the equivalent in to_unit.
    
    Args:
        from_unit: The source unit of measurement
        to_unit: The target unit of measurement
        
    Returns:
        float: The conversion factor to multiply by
        
    Raises:
        ValueError: If either unit is not supported
        
    Example:
        inches to feet: factor = 1/12 (divide by 12)
        feet to inches: factor = 12 (multiply by 12)
        cm to inches: factor = 1/2.54
        inches to cm: factor = 2.54
    """
    # Define conversion factors to convert TO inches
    to_inches = {
        "in": 1.0,      # 1 inch = 1 inch
        "ft": 12.0,     # 1 foot = 12 inches
        "cm": 0.393701, # 1 cm = 0.393701 inches
        "m": 39.3701,   # 1 m = 39.3701 inches
    }
    
    if from_unit not in to_inches or to_unit not in to_inches:
        raise ValueError(f"Unsupported unit conversion: {from_unit} -> {to_unit}")
    
    # First convert from source unit to inches, then from inches to target unit
    # If converting A -> B:
    # 1. Convert A to inches: multiply by to_inches[A]
    # 2. Convert inches to B: divide by to_inches[B]
    return to_inches[from_unit] / to_inches[to_unit]

def find_max_value(data: NumericArray) -> float:
    """
    Find the maximum numeric value in the array, ignoring boundaries ('B') and np.nan.
    
    Args:
        data: 2D NumPy array (dtype=object)
        
    Returns:
        float: The maximum value found
        
    Raises:
        ValueError: If no valid numeric data is found
    """
    valid_values: List[float] = []
    rows, cols = data.shape
    for r in range(rows):
        for c in range(cols):
            val = data[r, c]
            if isinstance(val, float) and not np.isnan(val):
                valid_values.append(val)
    
    if not valid_values:
        raise ValueError("No valid numeric data found to determine maximum.")
    
    return max(valid_values)

def transform_data(data: NumericArray, config: TopoConfig) -> None:
    """Transform the data according to configuration settings.
    
    This includes:
    - Converting units from input to output units
    - Shifting values so minimum is 0 (if config.apply_transform is True)
    - Rounding to specified precision (if config.rounding is not None)
    
    Args:
        data: 2D NumPy array of elevation data
        config: Configuration object with transformation settings
        
    Raises:
        ValueError: If no valid numeric data is found in the array
    """
    # Validate that we have at least one numeric value
    try:
        find_min_value(data)  # Just to check if we have numeric data
    except ValueError as e:
        raise ValueError("No valid numeric data found to transform.") from e
    
    # Convert units first (e.g. from inches to feet)
    conversion_factor = get_unit_conversion_factor(config.input_units, config.output_units)
    if conversion_factor != 1.0:
        apply_to_numeric_values(data, lambda x: x * conversion_factor)
    
    if config.invert_values:
        # Find the maximum value (which will become zero)
        max_val = find_max_value(data)
        apply_to_numeric_values(data, lambda x: max_val - x)
    
    if config.apply_transform:
        # Subtract min
        min_val = find_min_value(data)
        apply_to_numeric_values(data, lambda x: x - min_val)

    if config.rounding is not None and config.rounding > 0:
        # Round numeric values to the nearest increment (e.g. 0.5, 1.0, etc.)
        apply_to_numeric_values(data, lambda x: config.rounding * round(x / config.rounding)) 