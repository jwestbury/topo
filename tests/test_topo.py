import pytest
import numpy as np
import io
from src.topogen import TopoConfig, process_topography
from src.topogen.data_processing.data_processing import parse_csv, find_min_value, get_unit_conversion_factor
from src.topogen.interpolation.interpolation import fill_missing_iterative

def test_config_defaults():
    """Test that TopoConfig initializes with correct defaults"""
    config = TopoConfig()
    assert config.grid_spacing == 1.0
    assert config.input_units == "in"
    assert config.output_units == "ft"
    assert config.fill_method == "iterative"

def test_parse_csv():
    """Test CSV parsing with different types of data"""
    csv_data = "1.0,X,3.0\nB,2.0,4.0\n5.0,6.0,X"
    config = TopoConfig()
    
    with io.StringIO(csv_data) as f:
        result = parse_csv(f, config)
    
    assert result.shape == (3, 3)
    assert np.isnan(result[0, 1])  # X becomes nan
    assert result[1, 0] == 'B'     # B stays as B
    assert result[0, 2] == 3.0     # Numbers parsed correctly

def test_find_min_value():
    """Test finding minimum value while ignoring boundaries and NaN"""
    data = np.array([
        [1.0, np.nan, 3.0],
        ['B', 2.0, 4.0],
        [5.0, 6.0, np.nan]
    ], dtype=object)
    
    min_val = find_min_value(data)
    assert min_val == 1.0

def test_unit_conversion():
    """Test unit conversion factors"""
    # Test inches to feet
    assert get_unit_conversion_factor("in", "ft") == 1/12.0
    
    # Test feet to inches
    assert get_unit_conversion_factor("ft", "in") == 12.0
    
    # Test invalid units
    with pytest.raises(ValueError):
        get_unit_conversion_factor("invalid", "ft")

def test_fill_missing_iterative():
    """Test iterative filling of missing values"""
    data = np.array([
        [1.0, np.nan, 3.0],
        [4.0, np.nan, 6.0],
        [7.0, 8.0, 9.0]
    ], dtype=object)
    
    config = TopoConfig(
        fill_method="iterative",
        fill_max_iterations=10,
        fill_tolerance=1e-6,
        fill_neighbor_mode="4"
    )
    
    filled_data = fill_missing_iterative(data.copy(), config)
    
    # Check that no NaN values remain
    assert not any(np.isnan(x) for x in filled_data.ravel() if isinstance(x, float))

def test_end_to_end():
    """Test the complete workflow with a small dataset"""
    csv_data = "1.0,2.0,3.0\n4.0,X,6.0\n7.0,8.0,9.0"
    config = TopoConfig(
        grid_spacing=1.0,
        input_units="in",
        output_units="in",  # Keep same units to simplify validation
        show_plot=False,    # Don't display plot during tests
        save_path=None      # Don't save the plot
    )
    
    with io.StringIO(csv_data) as f:
        # process_topography doesn't return anything, it just processes the data
        process_topography(f, config)
