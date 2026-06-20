# Parametric Flowerpot Generator

Generates STEP and STL files for 3D-printable flowerpots using [CadQuery](https://cadquery.readthedocs.io/).

## Install

```bash
pip3 install -r requirements.txt
```

## Generate a pot

### Basic usage (STL output for 3D printing)
```bash
python3 flowerpot.py --diameter 120 --height 100 --wall 3 --base 4 pot
```

### Preset configurations
```bash
# List available presets (built-in and saved)
python3 flowerpot.py --list-presets

# Use built-in pot styles
python3 flowerpot.py --preset succulent succulent_pot
python3 flowerpot.py --preset herb herb_pot
python3 flowerpot.py --preset tree tree_pot

# Save current parameters as a named preset
python3 flowerpot.py --diameter 150 --height 120 --drains 6 --save-preset my_large_pot

# Use saved preset
python3 flowerpot.py --preset my_large_pot loaded_pot
```

### Advanced geometry options
```bash
# Different pot shapes
python3 flowerpot.py --shape square --diameter 100 --height 80 square_pot
python3 flowerpot.py --shape rectangular --diameter 120 --width 80 --height 100 rect_pot

# Decorative patterns
python3 flowerpot.py --pattern lines --pattern-depth 1.0 lined_pot
python3 flowerpot.py --pattern dots --pattern-depth 0.8 dotted_pot
python3 flowerpot.py --pattern waves --pattern-depth 1.2 wave_pot

# Modular stackable sections
python3 flowerpot.py --modular --sections 3 --diameter 120 --height 150 modular_pot

# Combine features
python3 flowerpot.py --shape square --pattern lines --modular --sections 2 complex_pot
```

### Available output formats
```bash
# STL file (default, for 3D printing)
python3 flowerpot.py --format stl --diameter 120 --height 100 pot

# STEP file (for CAD software)
python3 flowerpot.py --format step --diameter 120 --height 100 pot

# Both formats
python3 flowerpot.py --format all --diameter 120 --height 100 pot

# Export parameter summary
python3 flowerpot.py --summary --diameter 120 --height 100 pot
```

## Available parameters

| Parameter          | Default   | Description                                            |
|--------------------|-----------|--------------------------------------------------------|
| `--diameter`       | 120       | Outer top diameter (mm)                                |
| `--height`         | 100       | Total height (mm)                                      |
| `--wall`           | 3         | Wall thickness (mm)                                    |
| `--base`           | 4         | Base thickness (mm)                                    |
| `--drain-diameter` | 8         | Drainage hole diameter (mm), 0 to disable              |
| `--drains`         | 4         | Number of drainage holes (1 centered, >1 in a circle)  |
| `--taper`          | 5         | Wall draft angle (degrees)                             |
| `--rim-thickness`  | 2         | Extra rim thickness (mm)                               |
| `--rim-height`     | 5         | Rim height (mm)                                        |
| `--foot`           | 3         | Height of bottom ventilation feet (mm), 0 to disable   |
| `--rings`          | 2         | Number of concentric bottom ventilation rings          |
| `--format`         | stl       | Output format: step, stl, or all                       |
| `--summary`        | false     | Export parameter summary as JSON file                  |
| `--preset`         | -         | Use preset (built-in or saved preset name)             |
| `--save-preset`    | -         | Save current parameters as a named preset              |
| `--list-presets`   | false     | List all available presets and exit                    |
| `--shape`          | circular  | Pot shape: circular, square, or rectangular            |
| `--width`          | 0.0       | Width for rectangular pots (0 = 0.7 × diameter)        |
| `--pattern`        | none      | Decorative pattern: none, lines, dots, or waves        |
| `--pattern-depth`  | 0.5       | Depth of decorative patterns (mm)                      |
| `--modular`        | false     | Create stackable modular sections                      |
| `--sections`       | 1         | Number of modular sections                             |
| `filename`         | flowerpot | Output file path (extension added automatically)       |

## Features

### Preset Configurations
- **Built-in pot styles**: succulent, herb, and tree presets optimized for different plant types
- **Custom presets**: Save and load your favorite parameter combinations
- **Unified preset system**: Single command to use any preset (built-in or saved)
- **Batch generation**: Easily reproduce favorite designs

### Advanced Geometry 🚧
- **Multiple shapes**: Circular, square, and rectangular pot designs
- **Decorative patterns**: Lines, dots, and wave patterns with customizable depth
- **Modular system**: Stackable sections with interlocking connectors
- **Feature combinations**: Mix shapes, patterns, and modular designs

### Output Options
- **STL files** for 3D printing (default)
- **STEP files** for CAD software
- **Parameter summaries** with calculated dimensions and printing recommendations
- **Batch export** of multiple formats

### Input Validation
- Automatic validation of geometric constraints
- Prevents impossible configurations
- Clear error messages for invalid parameters

### Parameter Summary
When using `--summary`, a JSON file is generated with:
- All input parameters
- Calculated dimensions (radii, volumes)
- 3D printing recommendations
- Material usage estimates

## Example batch

```bash
# Using built-in presets
python3 flowerpot.py --preset succulent succulent_pot
python3 flowerpot.py --preset herb --summary herb_with_summary
python3 flowerpot.py --preset tree --format step large_tree_step

# Save and use custom presets
python3 flowerpot.py --diameter 150 --height 120 --drains 6 --save-preset my_custom
python3 flowerpot.py --preset my_custom loaded_custom

# Advanced geometry examples
python3 flowerpot.py --shape square --diameter 100 --height 80 square_planter
python3 flowerpot.py --shape rectangular --diameter 140 --width 90 --height 100 window_box
python3 flowerpot.py --pattern lines --pattern-depth 1.5 decorative_pot
python3 flowerpot.py --pattern dots --diameter 80 dotted_succulent
python3 flowerpot.py --pattern waves --pattern-depth 1.0 wave_design
python3 flowerpot.py --modular --sections 3 --diameter 120 --height 150 stackable_tower

# Combined features
python3 flowerpot.py --shape square --pattern dots --modular --sections 2 complex_modular

# Manual parameter examples
python3 flowerpot.py --diameter 80 --height 60 --wall 2.5 --drain-diameter 6 small_stl
python3 flowerpot.py --format step --diameter 200 --height 150 --wall 5 large_step
python3 flowerpot.py --diameter 120 --height 100 --drains 6 --drain-diameter 5 custom_drains
python3 flowerpot.py --diameter 120 --height 100 --foot 6 --rings 3 ventilated

# Complete export with summary
python3 flowerpot.py --format all --summary --diameter 120 --height 100 complete_pot
```

## Error Handling

The generator includes comprehensive error handling:
- Parameter validation with clear error messages
- Automatic adjustment of wall thickness when needed
- Graceful handling of export failures
- Informative logging for troubleshooting

## File Output

- **STL files**: Ready for 3D printing slicers
- **STEP files**: Compatible with CAD software (Fusion 360, SolidWorks, etc.)
- **JSON summaries**: Human-readable parameter documentation
- **Presets**: Saved in `presets/` directory for easy reuse and sharing

## License

This project is licensed under Creative Commons CC0 1.0 Universal - see LICENSE file for details.
