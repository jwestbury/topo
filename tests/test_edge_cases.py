import pytest
import numpy as np
import io
from src.topogen import TopoConfig, process_topography
from src.topogen.data_processing.data_processing import parse_csv, find_min_value, get_unit_conversion_factor, transform_data
from src.topogen.interpolation.interpolation import fill_missing, fill_missing_iterative
from src.topogen.visualization.visualization import generate_topographic_map
import matplotlib.pyplot as plt

def test_parse_csv_invalid_data():
    """Test CSV parsing with invalid data formats"""
    config = TopoConfig()
    
    # Test with empty file
    with io.StringIO("") as f:
        with pytest.raises(ValueError, match="Input CSV file is empty"):
            parse_csv(f, config)
    
    # Test with empty row
    with io.StringIO("\n") as f:
        with pytest.raises(ValueError, match="First row is empty"):
            parse_csv(f, config)
    
    # Test with inconsistent row lengths
    csv_data = "1.0,2.0,3.0\n4.0,5.0\n6.0,7.0,8.0"
    with io.StringIO(csv_data) as f:
        with pytest.raises(ValueError, match="Row 2 has 2 columns, expected 3"):
            parse_csv(f, config)
    
    # Test with non-numeric, non-special characters
    csv_data = "1.0,abc,3.0\nB,def,4.0\n5.0,6.0,ghi"
    with io.StringIO(csv_data) as f:
        result = parse_csv(f, config)
        assert np.isnan(result[0, 1])  # 'abc' should become nan
        assert result[1, 0] == 'B'     # 'B' should stay as 'B'
        assert np.isnan(result[1, 1])  # 'def' should become nan
        assert np.isnan(result[2, 2])  # 'ghi' should become nan

def test_transform_data_edge_cases():
    """Test data transformation edge cases"""
    # Test with all special values (no numeric data)
    data = np.array([
        ['B', 'B', 'B'],
        ['B', np.nan, 'B'],
        ['B', 'B', 'B']
    ], dtype=object)
    
    config = TopoConfig(
        rounding=None,  # Disable rounding for this test
        input_units="in",
        output_units="ft",
        apply_transform=False  # Don't shift values to zero
    )
    
    with pytest.raises(ValueError, match="No valid numeric data found"):
        transform_data(data.copy(), config)
    
    # Test unit conversion with small numbers
    data = np.array([
        [12.0, 24.0, 36.0],  # These values in inches
        [48.0, 60.0, 72.0],
        [84.0, 96.0, 108.0]
    ], dtype=object)
    result = data.copy()
    transform_data(result, config)
    
    # Values should be converted to feet (divide by 12)
    assert result[0, 0] == 1.0   # 12 inches = 1 foot
    assert result[0, 1] == 2.0   # 24 inches = 2 feet
    assert result[1, 0] == 4.0   # 48 inches = 4 feet

    # Test with rounding after unit conversion
    config = TopoConfig(
        rounding=0.5,  # Round to nearest 0.5 feet
        input_units="in",
        output_units="ft",
        apply_transform=False  # Don't shift values to zero
    )
    result = data.copy()
    transform_data(result, config)
    assert result[0, 0] == 1.0   # 12 inches = 1 foot (no rounding needed)
    assert result[0, 1] == 2.0   # 24 inches = 2 feet (no rounding needed)
    assert result[0, 2] == 3.0   # 36 inches = 3 feet (no rounding needed)

def test_interpolation_edge_cases():
    """Test interpolation edge cases"""
    # Test with unknown fill method
    data = np.array([[1.0, np.nan]], dtype=object)
    with pytest.raises(ValueError, match=r"fill_method must be one of: (?:iterative|none)(?:, (?:iterative|none))*"):
        config = TopoConfig(fill_method="invalid_method")
    
    # Test with all missing data
    data = np.array([
        [np.nan, np.nan, np.nan],
        [np.nan, np.nan, np.nan]
    ], dtype=float)  # Use float dtype for np.isnan compatibility
    config = TopoConfig(fill_method="iterative")
    with pytest.raises(ValueError, match="No valid values to interpolate from"):
        fill_missing_iterative(data.copy(), config)
    
    # Test with single missing value surrounded by boundaries
    data = np.array([
        ['B', 'B', 'B'],
        ['B', np.nan, 'B'],
        ['B', 'B', 'B']
    ], dtype=object)
    with pytest.raises(ValueError, match="No valid values to interpolate from"):
        fill_missing_iterative(data.copy(), config)

def test_visualization_edge_cases(monkeypatch):
    """Test edge cases for visualization functionality."""
    # Mock plt.show to prevent display
    monkeypatch.setattr(plt, 'show', lambda: None)
    
    # Test with minimal valid grid (2x2)
    data = np.array([[1.0, 2.0], [3.0, 4.0]])
    config = TopoConfig(
        show_plot=False,
        save_path=None,
        contour_spacing=1.0,  # Small spacing for our small test data
        figure_size=(4, 4),   # Smaller figure for faster rendering
        dpi=72                # Lower DPI for faster rendering
    )
    
    # Basic visualization should work
    generate_topographic_map(data, config)
    plt.close()  # Clean up
    
    # Test with extreme values but ensure they're not all identical
    data = np.array([[1e6, 1e6], [1e6, 1e6 + 1]])  # Add small difference
    generate_topographic_map(data, config)
    plt.close()
    
    # Test with very small values but ensure they're not all identical
    data = np.array([[1e-6, 1e-6], [1e-6, 1e-6 + 1e-7]])  # Add small difference
    generate_topographic_map(data, config)
    plt.close()
    
    # Test with some NaN values (should still work if not all NaN)
    data = np.array([
        [np.nan, 2.0, 3.0],
        [4.0, 5.0, 6.0]
    ])  # 5 valid points, enough for contours
    generate_topographic_map(data, config)
    plt.close()
    
    # Test with too few valid points
    data = np.array([
        [np.nan, 2.0],
        [3.0, np.nan]
    ])  # Only 2 valid points
    with pytest.raises(ValueError, match="Not enough valid data points"):
        generate_topographic_map(data, config) 