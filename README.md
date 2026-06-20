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

| Parameter          | Default         | Description                                            |
|--------------------|-----------------|--------------------------------------------------------|
| `--diameter`       | 120             | Outer top diameter (mm)                                |
| `--height`         | 100             | Total height (mm)                                      |
| `--wall`           | 3               | Wall thickness (mm)                                    |
| `--base`           | 4               | Base thickness (mm)                                    |
| `--drain-diameter` | 8               | Drainage hole diameter (mm), 0 to disable              |
| `--drains`         | 4               | Number of drainage holes (1 centered, >1 in a circle)  |
| `--taper`          | 5               | Wall draft angle (degrees)                             |
| `--rim-thickness`  | 2               | Extra rim thickness (mm)                               |
| `--rim-height`     | 5               | Rim height (mm)                                        |
| `--foot`           | 3               | Height of bottom ventilation feet (mm), 0 to disable   |
| `--rings`          | 2               | Number of concentric bottom ventilation rings          |
| `--format`         | stl             | Output format: step, stl, or all                       |
| `--summary`        | false           | Export parameter summary as JSON file                  |
| `filename`         | flowerpots.step | Output file path (extension added automatically)       |

## Features

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
# Small succulent pot (STL)
python3 flowerpot.py --diameter 80 --height 60 --wall 2.5 --drain-diameter 6 small_stl

# Large planter (STEP file)
python3 flowerpot.py --format step --diameter 200 --height 150 --wall 5 large_step

# Pot with custom drainage
python3 flowerpot.py --diameter 120 --height 100 --drains 6 --drain-diameter 5 custom_drains

# Ventilated pot with feet
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

## License

This project is licensed under Creative Commons CC0 1.0 Universal - see LICENSE file for details.
