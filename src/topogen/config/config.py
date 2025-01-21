#!/usr/bin/env python3

from typing import Tuple, Optional, Literal

class TopoConfig:
    """
    Holds configurable parameters for the entire topography workflow.
    Adjust defaults as needed, or pass values via constructor.
    
    Raises:
        ValueError: If any configuration parameter is invalid
    """

    # Valid units and their display names
    VALID_UNITS = {
        "in": "inches",
        "ft": "feet",
        "cm": "centimeters",
        "m": "meters"
    }
    
    # Valid fill methods
    VALID_FILL_METHODS = {"iterative", "none"}
    
    # Valid neighbor modes
    VALID_NEIGHBOR_MODES = {"4", "8"}

    def __init__(
        self,
        # Grid / Units
        grid_spacing: float = 1.0,         # distance between measurements in "input_units" 
        input_units: Literal["in", "ft", "cm", "m"] = "in",         # the raw measurement units in the CSV
        output_units: Literal["in", "ft", "cm", "m"] = "ft",        # final units for display (e.g., 'in', 'ft', 'cm')
        # Interpolation / Filling
        fill_method: Literal["iterative", "none"] = "iterative",  # "iterative", "none" (you can extend with "scipy", etc.)
        fill_max_iterations: int = 1000,
        fill_tolerance: float = 1e-6,
        fill_neighbor_mode: Literal["4", "8"] = "8",   # "4" or "8" neighbors
        # Transformation
        apply_transform: bool = True,     # whether to shift so lowest measurement is 0
        invert_values: bool = False,      # if True, treats values as depths below reference (highest value becomes 0)
        rounding: Optional[float] = 0.5,            # e.g. 0.5 to round to nearest 0.5 ft/in/etc. (None means no rounding)
        # Plotting
        contour_spacing: float = 1.0,     # spacing between contour lines in output_units (e.g., 12 inches)
        contour_cmap="RdYlGn_r",  # Red-Yellow-Green (reversed: green=low, red=high)
        smooth_contours: bool = False,    # whether to apply smoothing to contour lines
        smooth_factor: float = 0.0,        # amount of smoothing to apply (0.0 to 1.0, higher = smoother)
        figure_size: Tuple[float, float] = (10, 8),
        dpi: int = 300,
        show_plot: bool = True,           # display the interactive window
        save_path: Optional[str] = None,           # where to save the figure (None = no save)
        # Axis labeling
        x_label="Width",
        y_label="Height",
        title="Topographic Map"
    ):
        # Validate grid spacing
        if not isinstance(grid_spacing, (int, float)) or grid_spacing <= 0:
            raise ValueError("grid_spacing must be a positive number")
        
        # Validate units
        if input_units not in self.VALID_UNITS:
            raise ValueError(f"input_units must be one of: {', '.join(self.VALID_UNITS.keys())}")
        if output_units not in self.VALID_UNITS:
            raise ValueError(f"output_units must be one of: {', '.join(self.VALID_UNITS.keys())}")
        
        # Validate interpolation settings
        if fill_method not in self.VALID_FILL_METHODS:
            raise ValueError(f"fill_method must be one of: {', '.join(self.VALID_FILL_METHODS)}")
        if not isinstance(fill_max_iterations, int) or fill_max_iterations <= 0:
            raise ValueError("fill_max_iterations must be a positive integer")
        if not isinstance(fill_tolerance, (int, float)) or fill_tolerance <= 0:
            raise ValueError("fill_tolerance must be a positive number")
        if fill_neighbor_mode not in self.VALID_NEIGHBOR_MODES:
            raise ValueError(f"fill_neighbor_mode must be one of: {', '.join(self.VALID_NEIGHBOR_MODES)}")
        
        # Validate transformation settings
        if rounding is not None and (not isinstance(rounding, (int, float)) or rounding <= 0):
            raise ValueError("rounding must be None or a positive number")
        
        # Validate plotting settings
        if not isinstance(contour_spacing, (int, float)) or contour_spacing <= 0:
            raise ValueError("contour_spacing must be a positive number")
        if not isinstance(smooth_factor, (int, float)) or not 0 <= smooth_factor <= 1:
            raise ValueError("smooth_factor must be between 0 and 1")
        if not isinstance(figure_size, (tuple, list)) or len(figure_size) != 2 or \
           not all(isinstance(x, (int, float)) and x > 0 for x in figure_size):
            raise ValueError("figure_size must be a tuple of two positive numbers")
        if not isinstance(dpi, int) or dpi <= 0:
            raise ValueError("dpi must be a positive integer")
        if save_path is not None and not isinstance(save_path, str):
            raise ValueError("save_path must be None or a string")
        
        # Grid / Units
        self.grid_spacing = float(grid_spacing)
        self.input_units = input_units
        self.output_units = output_units
        
        # Interpolation / Filling
        self.fill_method = fill_method
        self.fill_max_iterations = int(fill_max_iterations)
        self.fill_tolerance = float(fill_tolerance)
        self.fill_neighbor_mode = fill_neighbor_mode

        # Transformation
        self.apply_transform = bool(apply_transform)
        self.invert_values = bool(invert_values)
        self.rounding = float(rounding) if rounding is not None else None

        # Plotting
        self.contour_spacing = float(contour_spacing)
        self.contour_cmap = str(contour_cmap)
        self.smooth_contours = bool(smooth_contours)
        self.smooth_factor = float(smooth_factor)
        self.figure_size = tuple(float(x) for x in figure_size)
        self.dpi = int(dpi)
        self.show_plot = bool(show_plot)
        self.save_path = str(save_path) if save_path is not None else None
        self.x_label = str(x_label)
        self.y_label = str(y_label)
        self.title = str(title) 