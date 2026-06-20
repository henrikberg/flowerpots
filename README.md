# Parametric Flowerpot Generator

Generates STEP files for 3D-printable flowerpots using [CadQuery](https://cadquery.readthedocs.io/).

## Install

```bash
pip install -r requirements.txt
```

## Generate a pot

```bash
python generator.py --diameter 120 --height 100 --wall 3 --base 4 --output pot.step
```

## Available parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--diameter` | 120 | Outer top diameter (mm) |
| `--height` | 100 | Total height (mm) |
| `--wall` | 3 | Wall thickness (mm) |
| `--base` | 4 | Base thickness (mm) |
| `--drain-diameter` | 8 | Drainage hole diameter (mm), 0 to disable |
| `--number-of-drains` | 4 | Number of drainage holes (1 centered, >1 in a circle) |
| `--taper` | 5 | Wall draft angle (degrees) |
| `--rim-thickness` | 2 | Extra rim thickness (mm) |
| `--rim-height` | 5 | Rim height (mm) |
| `--foot-height` | 5 | Height of bottom ventilation feet (mm), 0 to disable |
| `--foot-ring-count` | 1 | Number of concentric bottom ventilation rings |
| `--foot-ring-width` | 8 | Width of each bottom ring (mm) |
| `--output` | flowerpots.step | Output STEP file path |

## Example batch

```bash
python generator.py --diameter 100 --height 80 --output small.step
python generator.py --diameter 150 --height 120 --wall 4 --output large.step
python generator.py --diameter 120 --height 100 --number-of-drains 4 --drain-diameter 6 --output four_holes.step
python generator.py --diameter 120 --height 100 --foot-height 6 --foot-ring-count 2 --foot-ring-width 8 --output ventilated.step
```
