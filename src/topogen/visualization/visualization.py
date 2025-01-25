#!/usr/bin/env python3

from typing import List, Optional
import numpy as np
from numpy.typing import NDArray
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter
from matplotlib.colors import LinearSegmentedColormap
from ..config.config import TopoConfig
from ..data_processing.data_processing import NumericArray, get_unit_conversion_factor

def generate_topographic_map(data: NumericArray, config: TopoConfig) -> None:
    """
    Generate a topographic map visualization from the processed data.
    
    Args:
        data: 2D NumPy array (dtype=object) with float values and 'B' for boundaries
        config: TopoConfig with plotting parameters
        
    Raises:
        ValueError: If the data is invalid (all NaN, too small, etc.)
        RuntimeError: If there's an error during plotting
    """
    try:
        rows, cols = data.shape
        
        # Validate grid size
        if rows < 2 or cols < 2:
            raise ValueError(f"Grid size {data.shape} is too small. Minimum size is 2x2.")
        
        # Convert to a pure float array for plotting (boundaries become np.nan)
        plot_data: NDArray[np.float64] = np.array([[
            val if isinstance(val, float) else np.nan
            for val in row
        ] for row in data])
        
        # Check if we have enough valid data to plot
        valid_count = np.sum(~np.isnan(plot_data))
        if valid_count < 4:  # Need at least 4 points for a meaningful contour
            raise ValueError(f"Not enough valid data points ({valid_count}). Need at least 4 points.")
        
        # Create the figure
        plt.figure(figsize=config.figure_size, dpi=config.dpi)
        
        # Create custom colormap if specified
        if config.custom_colormap is not None:
            start_color, end_color = config.custom_colormap
            cmap = LinearSegmentedColormap.from_list('custom', [start_color, end_color])
        else:
            cmap = config.contour_cmap
        
        # Convert grid spacing to output units if needed
        grid_spacing: float
        if config.input_units != config.output_units:
            grid_spacing = config.grid_spacing * get_unit_conversion_factor(config.input_units, config.output_units)
        else:
            grid_spacing = config.grid_spacing
            
        # Start coordinates from 0
        x = np.arange(0, cols * grid_spacing, grid_spacing)
        y = np.arange(0, rows * grid_spacing, grid_spacing)
        X, Y = np.meshgrid(x, y)
        
        # Calculate levels based on the specified spacing
        vmin = np.nanmin(plot_data)
        vmax = np.nanmax(plot_data)
        if np.isnan(vmin) or np.isnan(vmax):
            raise ValueError("Cannot determine contour levels: all values are NaN")
        if vmin == vmax:
            # If all values are the same, create artificial levels around it
            vmin = vmin - config.contour_spacing
            vmax = vmax + config.contour_spacing
        
        # Round vmin down and vmax up to nearest spacing
        vmin = np.floor(vmin / config.contour_spacing) * config.contour_spacing
        vmax = np.ceil(vmax / config.contour_spacing) * config.contour_spacing
        levels = np.arange(vmin, vmax + config.contour_spacing, config.contour_spacing)
        
        # Apply smoothing if requested
        if config.smooth_contours:
            # Convert NaN to mean value for smoothing
            mask = np.isnan(plot_data)
            plot_data_smooth = plot_data.copy()
            mean_val = np.nanmean(plot_data)
            if np.isnan(mean_val):
                raise ValueError("Cannot smooth: all values are NaN")
            plot_data_smooth[mask] = mean_val
            
            # Apply Gaussian smoothing
            sigma = 1.0 + 3.0 * config.smooth_factor  # Scale factor 0.5 -> sigma 2.5, etc.
            plot_data_smooth = gaussian_filter(plot_data_smooth, sigma=sigma)
            
            # Restore NaN values
            plot_data_smooth[mask] = np.nan
            plot_data = plot_data_smooth
        
        # Create filled contours first for the continuous color gradient
        contourf = plt.contourf(X, Y, plot_data, levels=levels,
                               cmap=cmap, extend='both')
        
        # Add contour lines with labels
        contour = plt.contour(X, Y, plot_data, levels=levels,
                             colors='black', alpha=0.3, linewidths=0.5)
        plt.clabel(contour, inline=True, fontsize=8, fmt='%.1f')
        
        # Add colorbar with the continuous gradient
        plt.colorbar(contourf, label=f'Height ({config.output_units})')
        
        # Customize the plot
        plt.xlabel(f"Distance ({config.output_units})")
        plt.ylabel(f"Distance ({config.output_units})")
        plt.title(config.title)
        plt.grid(True, linestyle=':', alpha=0.5)
        
        # Flip the y-axis to match CSV orientation (top-to-bottom)
        plt.gca().invert_yaxis()
        
        # Save if requested
        if config.save_path:
            try:
                plt.savefig(config.save_path, bbox_inches='tight')
            except Exception as e:
                raise RuntimeError(f"Failed to save figure to {config.save_path}: {str(e)}")
        
        # Show if requested
        if config.show_plot:
            plt.show()
        else:
            plt.close()
            
    except Exception as e:
        # Clean up on error
        plt.close()
        raise 