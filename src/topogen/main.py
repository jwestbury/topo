#!/usr/bin/env python3

from typing import TextIO
from .config.config import TopoConfig
from .data_processing.data_processing import parse_csv, transform_data
from .interpolation.interpolation import fill_missing
from .visualization.visualization import generate_topographic_map

def process_topography(file_like: TextIO, config: TopoConfig) -> None:
    """
    Process topographic data from a CSV file and generate visualization.
    
    Args:
        file_like: A file-like object containing the CSV data
        config: Configuration object with processing settings
        
    Raises:
        ValueError: If the data is invalid or cannot be processed
        RuntimeError: If there's an error during visualization
    """
    # Parse the CSV data
    data = parse_csv(file_like, config)
    
    # Transform the data (unit conversion, shifting, rounding)
    transform_data(data, config)
    
    # Fill missing data points if requested
    fill_missing(data, config)
    
    # Generate visualization
    generate_topographic_map(data, config) 