import numpy as np
import pytest
from matplotlib import pyplot as plt
from src.topogen.config import TopoConfig
from src.topogen.visualization.visualization import generate_topographic_map

def test_custom_colormap_visualization():
    """Test that custom colormaps are applied correctly in visualization."""
    # Create a simple 3x3 test grid with a clear gradient
    test_data = np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0]
    ], dtype=object)  # Match the expected NumericArray type
    
    # Test greyscale gradient (dark to light)
    grey_config = TopoConfig(
        grid_spacing=1.0,
        show_plot=False,  # Don't display during tests
        save_path="tests/output/custom_colormap_grey.png",
        custom_colormap=[(0.2, 0.2, 0.2), (0.8, 0.8, 0.8)],
        contour_spacing=1.0,
        figure_size=(8, 8),
        dpi=150,
        title="Custom Greyscale Gradient"
    )
    
    # Test colored gradient (blue to red)
    color_config = TopoConfig(
        grid_spacing=1.0,
        show_plot=False,
        save_path="tests/output/custom_colormap_color.png",
        custom_colormap=[(0.0, 0.0, 0.8), (0.8, 0.0, 0.0)],  # Blue to red
        contour_spacing=1.0,
        figure_size=(8, 8),
        dpi=150,
        title="Custom Color Gradient (Blue to Red)"
    )
    
    # Create plots with both colormaps
    plt.figure()
    generate_topographic_map(test_data, grey_config)
    plt.close()
    
    plt.figure()
    generate_topographic_map(test_data, color_config)
    plt.close()
    
    # Test invalid custom colormap (should raise ValueError)
    with pytest.raises(ValueError):
        invalid_config = TopoConfig(
            grid_spacing=1.0,
            show_plot=False,
            custom_colormap=[(0.2, 0.2, 0.2)]  # Only one color
        )
    
    # Test out-of-range RGB values
    with pytest.raises(ValueError):
        invalid_config = TopoConfig(
            grid_spacing=1.0,
            show_plot=False,
            custom_colormap=[(0.2, 0.2, 1.5), (0.8, 0.8, 0.8)]  # 1.5 is > 1.0
        ) 