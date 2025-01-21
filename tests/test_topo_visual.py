import pytest
import numpy as np
import io
import os
from src.topogen import TopoConfig, process_topography

def ensure_output_dir():
    """Ensure the output directory exists"""
    output_dir = "tests/output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def test_simple_hill():
    """Generate a simple hill pattern for visual inspection"""
    # Create a simple hill pattern
    # Using 2-foot grid spacing (24 inches)
    size = 15  # This will create a 28x28 foot area
    x = np.arange(size) * 2.0  # x coordinates in feet
    y = np.arange(size) * 2.0  # y coordinates in feet
    X, Y = np.meshgrid(x, y)
    # Create a hill with peak height of 5 feet (60 inches)
    center_x, center_y = 14.0, 14.0  # Center in feet
    Z = 60.0 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 50.0)  # Height in inches
    
    # Convert to CSV format
    csv_lines = []
    for row in Z:
        csv_lines.append(",".join(f"{val:.1f}" for val in row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    # Raw version (no smoothing)
    config_raw = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        smooth_contours=False,
        title="Simple Hill (2ft grid, No Smoothing)",
        show_plot=False,
        save_path=f"{output_dir}/simple_hill_raw.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_raw)
    
    # Smoothed version
    config_smooth = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        smooth_contours=True,
        smooth_factor=0.5,  # Medium smoothing
        title="Simple Hill (2ft grid, Smoothed)",
        show_plot=False,
        save_path=f"{output_dir}/simple_hill_smooth.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_smooth)

def test_unit_conversion_display():
    """Generate the same hill pattern but with different input and output units"""
    # Create a hill pattern using metric measurements
    # Using 0.5m (50cm) grid spacing
    size = 15  # This will create a 7.5m x 7.5m area
    x = np.arange(size) * 0.5  # x coordinates in meters
    y = np.arange(size) * 0.5  # y coordinates in meters
    X, Y = np.meshgrid(x, y)
    # Create a hill with peak height of 1.5m (150cm)
    center_x, center_y = 3.5, 3.5  # Center in meters
    Z = 150.0 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 4.0)  # Height in cm
    
    # Convert to CSV format
    csv_lines = []
    for row in Z:
        csv_lines.append(",".join(f"{val:.1f}" for val in row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    # First version: cm to meters
    config_meters = TopoConfig(
        grid_spacing=50.0,  # 50cm grid spacing
        input_units="cm",   # Input in centimeters
        output_units="m",   # Display in meters
        contour_spacing=0.25,  # 25cm contours
        title="Hill Pattern (50cm grid, meters)",
        show_plot=False,
        save_path=f"{output_dir}/hill_cm_to_m.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_meters)

def test_valley_with_boundaries():
    """Generate a valley pattern with boundary markers"""
    # Using 2-foot grid spacing (24 inches)
    size = 15  # This will create a 28x28 foot area
    x = np.arange(size) * 2.0  # x coordinates in feet
    y = np.arange(size) * 2.0  # y coordinates in feet
    X, Y = np.meshgrid(x, y)
    # Create a valley with depth range of 2-5 feet (24-60 inches)
    center_x, center_y = 14.0, 14.0  # Center in feet
    Z = 60.0 - 36.0 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 50.0)  # Height in inches
    
    # Convert to CSV format with boundaries
    csv_lines = []
    for i, row in enumerate(Z):
        csv_row = []
        for j, val in enumerate(row):
            if i == 0 or i == size-1 or j == 0 or j == size-1:
                csv_row.append("B")  # Add boundaries around the edges
            else:
                csv_row.append(f"{val:.1f}")
        csv_lines.append(",".join(csv_row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    config = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        title="Valley with Boundaries (2ft grid)",
        show_plot=False,
        save_path=f"{output_dir}/valley_with_boundaries.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config)

def test_missing_data_interpolation():
    """Generate a pattern with missing data to test interpolation"""
    # Using 2-foot grid spacing (24 inches)
    size = 20  # This will create a 38x38 foot area
    x = np.arange(size) * 2.0  # x coordinates in feet
    y = np.arange(size) * 2.0  # y coordinates in feet
    X, Y = np.meshgrid(x, y)
    # Create undulating terrain with heights between 2-6 feet (24-72 inches)
    Z = 48.0 + 24.0 * np.sin(X/5.0) * np.cos(Y/5.0)  # Height in inches
    
    # Convert to CSV format with missing data
    csv_lines = []
    for i, row in enumerate(Z):
        csv_row = []
        for j, val in enumerate(row):
            if (i + j) % 3 == 0:  # Create a pattern of missing data
                csv_row.append("X")
            else:
                csv_row.append(f"{val:.1f}")
        csv_lines.append(",".join(csv_row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    config = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        title="Interpolated Pattern (2ft grid)",
        show_plot=False,
        save_path=f"{output_dir}/interpolated_pattern.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config)

def test_complex_terrain():
    """Test processing of complex terrain data from file"""
    output_dir = ensure_output_dir()
    
    # Raw contours (no smoothing)
    config_raw = TopoConfig(
        grid_spacing=24.0,  # 2 feet (24 inches) between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        invert_values=True,  # Values represent depths below reference
        smooth_contours=False,
        title="Complex Terrain (No Smoothing)",
        show_plot=False,
        save_path=f"{output_dir}/complex_raw.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with open("samples/complex.csv") as f:
        process_topography(f, config_raw)
    
    # Light smoothing
    config_light = TopoConfig(
        grid_spacing=24.0,
        input_units="in",
        output_units="ft",
        contour_spacing=1.0,
        invert_values=True,
        smooth_contours=True,
        smooth_factor=0.3,  # Light smoothing
        title="Complex Terrain (Light Smoothing)",
        show_plot=False,
        save_path=f"{output_dir}/complex_light_smooth.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with open("samples/complex.csv") as f:
        process_topography(f, config_light)
    
    # Medium smoothing
    config_medium = TopoConfig(
        grid_spacing=24.0,
        input_units="in",
        output_units="ft",
        contour_spacing=1.0,
        invert_values=True,
        smooth_contours=True,
        smooth_factor=0.6,  # Medium smoothing
        title="Complex Terrain (Medium Smoothing)",
        show_plot=False,
        save_path=f"{output_dir}/complex_medium_smooth.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with open("samples/complex.csv") as f:
        process_topography(f, config_medium)
    
    # Heavy smoothing
    config_heavy = TopoConfig(
        grid_spacing=24.0,
        input_units="in",
        output_units="ft",
        contour_spacing=1.0,
        invert_values=True,
        smooth_contours=True,
        smooth_factor=0.9,  # Heavy smoothing
        title="Complex Terrain (Heavy Smoothing)",
        show_plot=False,
        save_path=f"{output_dir}/complex_heavy_smooth.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with open("samples/complex.csv") as f:
        process_topography(f, config_heavy)

def test_inverted_values():
    """Test processing of values that represent depths below a reference point"""
    # Using 2-foot grid spacing (24 inches)
    size = 15  # This will create a 28x28 foot area
    x = np.arange(size) * 2.0  # x coordinates in feet
    y = np.arange(size) * 2.0  # y coordinates in feet
    X, Y = np.meshgrid(x, y)
    
    # Create a bowl shape where higher numbers mean deeper
    # Values will range from 0 (at edges) to 60 inches (at center)
    center_x, center_y = 14.0, 14.0  # Center in feet
    Z = 60.0 * np.exp(-((X - center_x)**2 + (Y - center_y)**2) / 50.0)  # Depth in inches
    
    # Convert to CSV format
    csv_lines = []
    for row in Z:
        csv_lines.append(",".join(f"{val:.1f}" for val in row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    # First, process as-is (higher numbers = deeper)
    config_raw = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        invert_values=False,  # Process values as-is
        title="Bowl Shape (Raw Values - Higher = Deeper)",
        show_plot=False,
        save_path=f"{output_dir}/bowl_raw.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_raw)
    
    # Now process inverted (higher numbers = lower elevation)
    config_inverted = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=1.0,  # 1-foot contours
        invert_values=True,  # Treat values as depths below reference
        title="Bowl Shape (Inverted - Higher = Lower)",
        show_plot=False,
        save_path=f"{output_dir}/bowl_inverted.png",
        figure_size=(10, 8),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_inverted)

def test_garden_smoothing():
    """Test contour smoothing for garden-like terrain"""
    # Using 2-foot grid spacing (24 inches)
    size = 20  # This will create a 38x38 foot area
    x = np.arange(size) * 2.0  # x coordinates in feet
    y = np.arange(size) * 2.0  # y coordinates in feet
    X, Y = np.meshgrid(x, y)
    
    # Create a complex garden-like terrain with multiple features
    # Base terrain with gentle slope
    Z = Y / 4.0  # Gentle slope, rising 1 foot every 8 feet
    # Add some mounds and depressions
    for cx, cy, height, spread in [
        (16.0, 16.0, 24.0, 12.0),  # Main hill
        (8.0, 24.0, -12.0, 8.0),   # Depression
        (24.0, 8.0, 18.0, 10.0),   # Secondary hill
    ]:
        Z += height * np.exp(-((X - cx)**2 + (Y - cy)**2) / spread**2)
    
    # Convert to inches
    Z = Z * 12.0  # Convert feet to inches for input
    
    # Convert to CSV format
    csv_lines = []
    for row in Z:
        csv_lines.append(",".join(f"{val:.1f}" for val in row))
    csv_data = "\n".join(csv_lines)
    
    output_dir = ensure_output_dir()
    
    # Generate raw contours
    config_raw = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=0.5,  # 6-inch contours
        smooth_contours=False,
        title="Garden Terrain (Raw Contours)",
        show_plot=False,
        save_path=f"{output_dir}/garden_raw.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_raw)
    
    # Generate smoothed contours
    config_smooth = TopoConfig(
        grid_spacing=24.0,  # 2 feet between measurements
        input_units="in",
        output_units="ft",  # Display in feet for readability
        contour_spacing=0.5,  # 6-inch contours
        smooth_contours=True,
        smooth_factor=0.7,  # Significant smoothing
        title="Garden Terrain (Smoothed Contours)",
        show_plot=False,
        save_path=f"{output_dir}/garden_smooth.png",
        figure_size=(12, 10),
        dpi=150
    )
    
    with io.StringIO(csv_data) as f:
        process_topography(f, config_smooth) 