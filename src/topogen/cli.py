#!/usr/bin/env python3

"""
Command-line interface for topo.
"""

import argparse
from pathlib import Path
from typing import List, Optional
from .config.config import TopoConfig
from .main import process_topography

def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Args:
        args: Optional list of command line arguments. If None, uses sys.argv[1:].
        
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="Generate topographic maps from CSV data.")
    parser.add_argument("input_file", type=Path, help="Path to input CSV file")
    parser.add_argument("--output", "-o", type=Path, help="Path to save output plot")
    parser.add_argument("--grid-spacing", type=float, default=1.0, help="Distance between measurements")
    parser.add_argument("--input-units", choices=["in", "ft", "cm", "m"], default="in", help="Input measurement units")
    parser.add_argument("--output-units", choices=["in", "ft", "cm", "m"], default="ft", help="Output display units")
    parser.add_argument("--contour-spacing", type=float, default=1.0, help="Spacing between contour lines")
    parser.add_argument("--no-show", action="store_true", help="Don't display the plot window")
    parser.add_argument("--invert", action="store_true", help="Invert values (e.g., for depth measurements)")
    parser.add_argument("--smooth", action="store_true", help="Enable contour smoothing")
    parser.add_argument("--smooth-factor", type=float, default=0.5, help="Smoothing factor (0.0-1.0, higher = smoother)")
    parser.add_argument("--figure-width", type=float, default=10.0, help="Figure width in inches")
    parser.add_argument("--figure-height", type=float, default=8.0, help="Figure height in inches")
    parser.add_argument("--dpi", type=int, default=150, help="DPI (dots per inch) for output image")
    
    # Create a mutually exclusive group for colormaps
    colormap_group = parser.add_mutually_exclusive_group()
    colormap_group.add_argument("--colormap", 
                              choices=["RdYlGn_r", "gray", "gray_r", "gist_yarg", "bone"],
                              default="RdYlGn_r",
                              help="Color scheme: RdYlGn_r (red-yellow-green), gray/gray_r (full greyscale), "
                                   "gist_yarg (light to dark), bone (blue-tinted greys)")
    colormap_group.add_argument("--colormap-custom", type=str, 
                              help="Custom colormap defined as two RGB colors for gradient, each color as R,G,B values between 0-1. "
                                   "Format: 'start_r,start_g,start_b:end_r,end_g,end_b' "
                                   "e.g. '0.2,0.2,0.2:0.8,0.8,0.8' for dark grey to light grey")
    return parser.parse_args(args)

def main(args: Optional[List[str]] = None) -> None:
    """
    Main entry point for the CLI.
    
    Args:
        args: Optional list of command line arguments. If None, uses sys.argv[1:].
    """
    parsed_args = parse_args(args)
    
    config = TopoConfig(
        grid_spacing=parsed_args.grid_spacing,
        input_units=parsed_args.input_units,
        output_units=parsed_args.output_units,
        contour_spacing=parsed_args.contour_spacing,
        show_plot=not parsed_args.no_show,
        save_path=str(parsed_args.output) if parsed_args.output else None,
        invert_values=parsed_args.invert,
        smooth_contours=parsed_args.smooth,
        smooth_factor=parsed_args.smooth_factor,
        figure_size=(parsed_args.figure_width, parsed_args.figure_height),
        dpi=parsed_args.dpi,
        contour_cmap=parsed_args.colormap if not parsed_args.colormap_custom else None,
        custom_colormap=[tuple(float(x) for x in color.split(',')) 
                        for color in parsed_args.colormap_custom.split(':')]
        if parsed_args.colormap_custom else None
    )
    
    with open(parsed_args.input_file) as f:
        process_topography(f, config)

if __name__ == "__main__":
    main()
