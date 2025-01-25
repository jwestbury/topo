#!/usr/bin/env python3

import pytest
from pathlib import Path
from src.topogen.cli import parse_args

def test_default_colormap():
    """Test that default colormap is RdYlGn_r when no colormap option is specified."""
    args = parse_args(["input.csv"])
    assert args.colormap == "RdYlGn_r"
    assert args.colormap_custom is None

def test_builtin_colormap():
    """Test that built-in colormap options are accepted."""
    for cmap in ["RdYlGn_r", "gray", "gray_r", "gist_yarg", "bone"]:
        args = parse_args(["input.csv", "--colormap", cmap])
        assert args.colormap == cmap
        assert args.colormap_custom is None

def test_custom_colormap():
    """Test that custom colormap is parsed correctly."""
    custom_map = "0.2,0.2,0.2:0.8,0.8,0.8"
    args = parse_args(["input.csv", "--colormap-custom", custom_map])
    assert args.colormap == "RdYlGn_r"  # Default value is preserved but not used
    assert args.colormap_custom == custom_map

def test_mutually_exclusive_colormaps():
    """Test that colormap and colormap-custom cannot be used together."""
    with pytest.raises(SystemExit):
        parse_args(["input.csv", "--colormap", "gray", "--colormap-custom", "0.2,0.2,0.2:0.8,0.8,0.8"])

def test_invalid_custom_colormap_format():
    """Test that invalid custom colormap formats are caught during config creation."""
    from src.topogen.cli import main
    
    # Invalid number of values
    with pytest.raises(ValueError):
        main(["input.csv", "--colormap-custom", "0.2,0.2"])
    
    # Invalid RGB values (out of range)
    with pytest.raises(ValueError):
        main(["input.csv", "--colormap-custom", "0.2,0.2,1.5:0.8,0.8,0.8"])
    
    # Invalid format (missing colon)
    with pytest.raises(ValueError):
        main(["input.csv", "--colormap-custom", "0.2,0.2,0.2,0.8,0.8,0.8"])

def test_other_arguments_with_colormap():
    """Test that colormap options work with other arguments."""
    args = parse_args([
        "input.csv",
        "--colormap", "gray",
        "--grid-spacing", "2.0",
        "--invert",
        "--smooth"
    ])
    assert args.colormap == "gray"
    assert args.grid_spacing == 2.0
    assert args.invert is True
    assert args.smooth is True

def test_input_file_required():
    """Test that input file argument is required."""
    with pytest.raises(SystemExit):
        parse_args([])

def test_input_file_path():
    """Test that input file is converted to Path."""
    args = parse_args(["input.csv"])
    assert isinstance(args.input_file, Path)
    assert str(args.input_file) == "input.csv" 