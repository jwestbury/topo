#!/usr/bin/env python3

from typing import List, Tuple
import numpy as np
from numpy.typing import NDArray
from ..config.config import TopoConfig
from ..data_processing.data_processing import NumericArray

def fill_missing_iterative(data: NumericArray, config: TopoConfig) -> NumericArray:
    """
    Iteratively fill np.nan cells by averaging over valid neighbors.
    Skips boundary cells marked as 'B'.
    
    Args:
        data: 2D NumPy array (dtype=object).
              float cells = numeric data, np.nan = missing, 'B' = boundary
        config: TopoConfig, which may include fill_max_iterations, fill_tolerance, etc.
    
    Returns:
        data (in-place)
        
    Raises:
        ValueError: If the data cannot be interpolated (e.g., all NaN or boundaries)
    """
    rows, cols = data.shape
    mode_8_neighbors = (config.fill_neighbor_mode == "8")
    
    # Convert to float array for faster operations, marking boundaries as NaN
    float_data = np.array([[
        val if isinstance(val, float) else np.nan
        for val in row
    ] for row in data], dtype=float)
    
    # Create a mask of boundary cells
    boundary_mask = np.array([[
        val == 'B'
        for val in row
    ] for row in data], dtype=bool)
    
    # Create neighbor offset arrays based on mode
    neighbor_offsets: List[Tuple[int, int]]
    if mode_8_neighbors:
        neighbor_offsets = [(-1, -1), (-1, 0), (-1, 1),
                           (0, -1),           (0, 1),
                           (1, -1),  (1, 0),  (1, 1)]
    else:
        neighbor_offsets = [(-1, 0), (0, -1), (0, 1), (1, 0)]
    
    # Check if we have any non-boundary cells to interpolate
    if np.all(boundary_mask):
        raise ValueError("All cells are boundaries - nothing to interpolate")
    
    # Check if we have any valid values to interpolate from
    if np.all(np.isnan(float_data)):
        raise ValueError("No valid values to interpolate from")
    
    for iteration in range(config.fill_max_iterations):
        old_data = float_data.copy()
        changed = False
        
        # Create arrays to store neighbor sums and counts
        neighbor_sums = np.zeros_like(float_data)
        neighbor_counts = np.zeros_like(float_data, dtype=int)
        
        # Calculate neighbor sums and counts
        for dr, dc in neighbor_offsets:
            # Shift the array to align with the current neighbor offset
            shifted_data = np.roll(np.roll(float_data, dr, axis=0), dc, axis=1)
            # For edges, set the wrapped values to NaN
            if dr > 0:
                shifted_data[:dr] = np.nan
            elif dr < 0:
                shifted_data[dr:] = np.nan
            if dc > 0:
                shifted_data[:, :dc] = np.nan
            elif dc < 0:
                shifted_data[:, dc:] = np.nan
            
            # Add to sums where the neighbor is not NaN
            valid_neighbors = ~np.isnan(shifted_data)
            neighbor_sums += np.where(valid_neighbors, shifted_data, 0)
            neighbor_counts += valid_neighbors.astype(int)
        
        # Calculate new values where we have missing data (NaN) and at least one neighbor
        missing_mask = np.isnan(float_data) & ~boundary_mask & (neighbor_counts > 0)
        if np.any(missing_mask):
            float_data[missing_mask] = neighbor_sums[missing_mask] / neighbor_counts[missing_mask]
            changed = True
        
        # Check convergence
        if changed:
            diff = np.nanmax(np.abs(float_data - old_data))
            if diff < config.fill_tolerance:
                print(f"[fill_missing_iterative] Converged after {iteration+1} iterations (diff={diff:.6f}).")
                break
        else:
            # No changes were made this iteration
            break
    
    # Update the original data array with interpolated values
    for r in range(rows):
        for c in range(cols):
            if not boundary_mask[r, c]:  # Don't update boundary cells
                data[r, c] = float_data[r, c]
    
    return data

def fill_missing(data: NumericArray, config: TopoConfig) -> None:
    """
    Dispatch to the appropriate fill method based on config.fill_method.
    
    Args:
        data: 2D NumPy array (dtype=object)
        config: TopoConfig with fill_method and related settings
        
    Raises:
        ValueError: If the fill_method is unknown or if interpolation fails
    """
    if config.fill_method == "iterative":
        fill_missing_iterative(data, config)
    elif config.fill_method == "none":
        # Do not fill missing data at all
        pass
    else:
        raise ValueError(f"Unknown fill_method '{config.fill_method}'.") 