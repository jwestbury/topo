# Topogen

## Background

I have an average American garden - a quarter acre lot with a one-story house bifurcating the garden. The back garden is built on a slope, which presents challenges for site design. I didn't want to pay many thousands of dollars to a surveyor, but I wanted more granularity than the traditional A-frame contours would provide, and something I could capture digitally for posterity and ease of iteration.

I plotted my back garden by attaching hooks to the back fence every two feet. Then, using my trusty Little Giant ladder, I tied a taut line hitch at one end of a length of mason line, securing the other to my ladder. I slipped the taut line hitch over a hook along the back fence, placed my ladder at the opposite end of the garden, and adjusted the height to ensure the line was level (using a line level to ensure reasonable accuracy). On the first pass, I marked out my mason line at two-foot intervals, then walked the length of the line, taking height measurements every two feet. When one pass was done, I slid the ladder two feet further down the width of the garden, slipped my hitch over the next hook, and repeated the process. In the end, this produced a grid of measurements - how many inches the ground was below the mason line.

I then wrote Topogen, with extensive help from Cursor IDE - after all, I am not a civil engineer or a surveyor, and while I'm pretty good at reading a topographic map after years of hiking and backpacking - and I do not hide an abiding love of the UK's Ordnance Survey maps - I have no idea how to actually make one. At any rate, I implemented all the features I needed. In particular, I needed the tool to capture what I called my "zero point": Because the hooks along the back fence were above ground level for the entirety of their run, my mason line was never less than 18 inches above the ground! Thus, we needed to capture this fact, and then invert the measurements to convert them into a height map (rather than a depth map).

In the end, this tool produces topographic maps which are excellent for my own use, and I hope they will be excellent for someone else's use, too! Because I used AI to help with the bits I didn't have any preexisting knowledge of, there are likely some bugs; but the tests produce images which can be visually spot-checked to ensure the behavior is as expected, and I know the app to work well for my own garden.

Please do contribute if you think you can make this tool better; it takes only a bit of hard graft to produce the measurements, and topographic maps empower us to understand our gardens so much better than we do.

## Features

- Process CSV files containing elevation measurements
- Interpolate missing data points using neighbor averaging
- Convert between different measurement units (inches, feet, centimeters, meters)
- Generate contour maps with customizable visualization settings
- Support for boundary markers and data transformation

## Getting Started

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
   or:
   ```
   pip install .
   ```

2. Prepare your input CSV file with elevation measurements. The file should contain:
   - Numbers for elevation measurements
   - 'X' for missing data points (will be interpolated)
   - 'B' for boundary markers

3. Run the application:
   ```
   python -m topogen.cli input.csv --output map.png --units ft --grid-spacing 2.0
   ```

   Options:
   - `input.csv`: Path to your input CSV file
   - `--output`: Path to save the visualization (optional)
   - `--units`: Output units ('in', 'ft', 'cm', 'm'), default: ft
   - `--grid-spacing`: Distance between measurements in input units, default: 2.0

## Project Layout

- `src/topogen/`: Core package
  - `main.py`: Main processing pipeline
  - `data_processing/`: CSV parsing and data transformation
  - `interpolation/`: Missing data interpolation
  - `visualization/`: Contour map generation
  - `config/`: Configuration management
  - `cli.py`: Command-line interface
- `tests/`: Test files and test data
- `samples/`: Example input files
- `pyproject.toml`: Package configuration
- `requirements.txt`: Dependencies

