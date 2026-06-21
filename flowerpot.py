import cadquery as cq
import argparse
import json
import logging
import math
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FlowerpotParams:
    """Data class containing all parameters for flowerpot generation."""
    top_diameter: float = 120.0
    bottom_diameter: float = 0.0
    taper_angle: float = 5.0
    height: float = 100.0
    wall_thickness: float = 3.0
    base_thickness: float = 4.0
    drain_diameter: float = 8.0
    number_of_drains: int = 4
    rim_thickness: float = 2.0
    rim_height: float = 5.0
    foot_height: float = 3.0
    foot_ring_count: int = 2
    # Advanced geometry parameters
    shape: str = "circular"  # circular, square, rectangular
    width: float = 0.0  # For rectangular shapes (0 = use diameter)
    pattern: str = "none"  # none, lines, dots, waves
    pattern_depth: float = 0.5  # Depth of decorative patterns
    modular: bool = False  # Create stackable sections
    sections: int = 1  # Number of modular sections


# Predefined pot style presets
PRESETS = {
    "succulent": {
        "description": "Small, shallow pot for succulents and cacti",
        "params": FlowerpotParams(
            top_diameter=80.0,
            bottom_diameter=60.0,
            taper_angle=3.0,
            height=60.0,
            wall_thickness=2.5,
            base_thickness=3.0,
            drain_diameter=6.0,
            number_of_drains=1,
            rim_thickness=1.5,
            rim_height=3.0,
            foot_height=2.0,
            foot_ring_count=1,
        ),
    },
    "herb": {
        "description": "Medium-sized standard pot for herbs and general use",
        "params": FlowerpotParams(
            top_diameter=120.0,
            bottom_diameter=0.0,
            taper_angle=5.0,
            height=100.0,
            wall_thickness=3.0,
            base_thickness=4.0,
            drain_diameter=8.0,
            number_of_drains=4,
            rim_thickness=2.0,
            rim_height=5.0,
            foot_height=3.0,
            foot_ring_count=2,
        ),
    },
    "tree": {
        "description": "Large, sturdy pot for trees and large plants",
        "params": FlowerpotParams(
            top_diameter=200.0,
            bottom_diameter=150.0,
            taper_angle=2.0,
            height=180.0,
            wall_thickness=5.0,
            base_thickness=8.0,
            drain_diameter=12.0,
            number_of_drains=6,
            rim_thickness=3.0,
            rim_height=8.0,
            foot_height=5.0,
            foot_ring_count=3,
        ),
    },
}


def list_presets() -> None:
    """List all available presets with their descriptions."""
    print("Available presets:")

    for name, preset_data in PRESETS.items():
        print(f"  {name:<10} - {preset_data['description']}")
    
    # Saved presets
    presets_dir = Path("presets")
    if presets_dir.exists():
        saved_presets = list(presets_dir.glob("*.json"))
        if saved_presets:
            for preset_file in sorted(saved_presets):
                try:
                    with open(preset_file, 'r') as f:
                        config = json.load(f)
                    height = config.get("height", 0)
                    diameter = config.get("top_diameter", 0)
                    name = preset_file.stem
                    print(f"  {name:<10} - {diameter}mm diameter, {height}mm height")
                except (json.JSONDecodeError, KeyError):
                    print(f"  {preset_file.stem:<10} - (invalid preset file)")


def load_preset(preset_name: str) -> FlowerpotParams:
    """Load a preset by name (built-in or saved)."""
    # Check if it's a built-in preset
    if preset_name in PRESETS:
        return PRESETS[preset_name]["params"]
    
    # Check if it's a saved preset file
    preset_path = Path(f"presets/{preset_name}.json")
    if preset_path.exists():
        try:
            with open(preset_path, 'r') as f:
                config = json.load(f)
            
            # Extract parameters from config, using defaults for missing values
            return FlowerpotParams(
                top_diameter=config.get("top_diameter", 120.0),
                bottom_diameter=config.get("bottom_diameter", 0.0),
                taper_angle=config.get("taper_angle", 5.0),
                height=config.get("height", 100.0),
                wall_thickness=config.get("wall_thickness", 3.0),
                base_thickness=config.get("base_thickness", 4.0),
                drain_diameter=config.get("drain_diameter", 8.0),
                number_of_drains=config.get("number_of_drains", 4),
                rim_thickness=config.get("rim_thickness", 2.0),
                rim_height=config.get("rim_height", 5.0),
                foot_height=config.get("foot_height", 3.0),
                foot_ring_count=config.get("foot_ring_count", 2),
                shape=config.get("shape", "circular"),
                width=config.get("width", 0.0),
                pattern=config.get("pattern", "none"),
                pattern_depth=config.get("pattern_depth", 0.5),
                modular=config.get("modular", False),
                sections=config.get("sections", 1),
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in preset file '{preset_name}': {e}")
    
    # Not found
    built_in = ", ".join(PRESETS.keys())
    raise ValueError(f"Unknown preset '{preset_name}'. Built-in presets: {built_in}")


def save_preset(preset_name: str, params: FlowerpotParams) -> None:
    """Save current parameters as a named preset."""
    presets_dir = Path("presets")
    presets_dir.mkdir(exist_ok=True)
    
    preset_path = presets_dir / f"{preset_name}.json"
    config = {
        "top_diameter": params.top_diameter,
        "bottom_diameter": params.bottom_diameter,
        "taper_angle": params.taper_angle,
        "height": params.height,
        "wall_thickness": params.wall_thickness,
        "base_thickness": params.base_thickness,
        "drain_diameter": params.drain_diameter,
        "number_of_drains": params.number_of_drains,
        "rim_thickness": params.rim_thickness,
        "rim_height": params.rim_height,
        "foot_height": params.foot_height,
        "foot_ring_count": params.foot_ring_count,
        "shape": params.shape,
        "width": params.width,
        "pattern": params.pattern,
        "pattern_depth": params.pattern_depth,
        "modular": params.modular,
        "sections": params.sections,
    }
    
    try:
        with open(preset_path, 'w') as f:
            json.dump(config, f, indent=2)
        logging.info(f"Preset saved to {preset_path}")
    except Exception as e:
        logging.error(f"Failed to save preset: {e}")


def calculate_printing_guidance(params: FlowerpotParams) -> dict:
    """Calculate 3D printing recommendations and material usage."""
    import math
    
    # Calculate approximate volume (simplified for different shapes)
    if params.shape == "circular":
        # Approximate as frustum of cone
        radius_top = params.top_diameter / 2
        radius_bottom = params.bottom_diameter / 2 if params.bottom_diameter > 0 else radius_top - params.height * math.tan(math.radians(params.taper_angle))
        volume = (1/3) * math.pi * params.height * (radius_top**2 + radius_top*radius_bottom + radius_bottom**2)
        # Subtract inner volume
        inner_radius_top = radius_top - params.wall_thickness
        inner_radius_bottom = radius_bottom - params.wall_thickness
        inner_height = params.height - params.base_thickness
        inner_volume = (1/3) * math.pi * inner_height * (inner_radius_top**2 + inner_radius_top*inner_radius_bottom + inner_radius_bottom**2)
        volume -= inner_volume
    elif params.shape == "square":
        # Approximate as frustum of square pyramid
        size_top = params.top_diameter
        size_bottom = params.bottom_diameter if params.bottom_diameter > 0 else size_top - 2 * params.height * math.tan(math.radians(params.taper_angle))
        volume = (1/3) * params.height * (size_top**2 + size_top*size_bottom + size_bottom**2)
        # Subtract inner volume
        inner_size_top = size_top - 2 * params.wall_thickness
        inner_size_bottom = size_bottom - 2 * params.wall_thickness
        inner_height = params.height - params.base_thickness
        inner_volume = (1/3) * inner_height * (inner_size_top**2 + inner_size_top*inner_size_bottom + inner_size_bottom**2)
        volume -= inner_volume
    else:  # rectangular
        length = params.top_diameter
        width = params.width if params.width > 0 else length * 0.7
        volume = length * width * params.height
        # Subtract inner volume
        inner_length = length - 2 * params.wall_thickness
        inner_width = width - 2 * params.wall_thickness
        inner_height = params.height - params.base_thickness
        inner_volume = inner_length * inner_width * inner_height
        volume -= inner_volume
    
    # Convert to cm³ for material estimation
    volume_cm3 = volume / 1000
    
    # Material estimation (PLA density ~1.24 g/cm³)
    material_density = 1.24  # g/cm³ for PLA
    material_weight = volume_cm3 * material_density
    
    # Printing recommendations based on size and features
    recommendations = []
    
    # Layer height recommendation
    if params.wall_thickness < 2.0:
        recommendations.append("Use 0.1mm layer height for better detail with thin walls")
    elif params.wall_thickness > 4.0:
        recommendations.append("Use 0.2mm layer height for faster printing with thick walls")
    else:
        recommendations.append("Use 0.15mm layer height for good balance of speed and detail")
    
    # Infill recommendation
    if params.height > 150:
        recommendations.append("Use 20% infill for tall pots to reduce warping")
    elif params.pattern != "none":
        recommendations.append("Use 15% infill to highlight decorative patterns")
    else:
        recommendations.append("Use 25% infill for standard strength")
    
    # Support recommendation
    if params.rim_height > 10 or params.foot_height > 5:
        recommendations.append("Enable supports for overhangs (rim and feet)")
    else:
        recommendations.append("No supports needed for this design")
    
    # Print speed recommendation
    if params.drain_diameter < 4:
        recommendations.append("Reduce print speed to 30mm/s for small drain holes")
    elif params.shape == "rectangular":
        recommendations.append("Use 40mm/s print speed for rectangular shapes")
    else:
        recommendations.append("Use 50mm/s print speed for standard printing")
    
    # Bed adhesion recommendation
    if params.bottom_diameter > 150 or params.top_diameter > 150:
        recommendations.append("Use brim or raft for large base area")
    else:
        recommendations.append("Use skirt for bed adhesion")
    
    # Material recommendation
    if params.foot_height > 0:
        recommendations.append("Consider PETG for better durability with feet")
    else:
        recommendations.append("PLA recommended for most applications")
    
    # Special considerations
    if params.modular and params.sections > 1:
        recommendations.append("Print modular sections individually for best quality")
        recommendations.append("Test fit connections before printing full set")
    
    if params.pattern != "none":
        recommendations.append("Use slower print speed for pattern details")
        recommendations.append("Consider using 0.4mm nozzle for better pattern resolution")
    
    # Printing time estimation (rough calculation)
    # Based on typical speeds: 50mm/s, 0.15mm layer height, 25% infill
    surface_area = 2 * math.pi * (params.top_diameter/2) * params.height if params.shape == "circular" else 2 * (params.top_diameter + params.width) * params.height
    estimated_time_minutes = (volume_cm3 * 2.5) + (surface_area / 1000)  # Very rough estimate
    
    # Cost estimation
    pla_cost_per_kg = 20  # $20 per kg typical
    estimated_cost = (material_weight / 1000) * pla_cost_per_kg
    
    return {
        "volume_cm3": round(volume_cm3, 2),
        "material_weight_g": round(material_weight, 2),
        "estimated_time_minutes": round(estimated_time_minutes, 0),
        "estimated_cost_usd": round(estimated_cost, 2),
        "recommendations": recommendations,
        "layer_height_mm": 0.15 if 2.0 <= params.wall_thickness <= 4.0 else (0.1 if params.wall_thickness < 2.0 else 0.2),
        "infill_percent": 20 if params.height > 150 else (15 if params.pattern != "none" else 25),
        "supports_needed": params.rim_height > 10 or params.foot_height > 5,
        "print_speed_mm_s": 30 if params.drain_diameter < 4 else (40 if params.shape == "rectangular" else 50),
        "bed_adhesion": "brim" if params.bottom_diameter > 150 or params.top_diameter > 150 else "skirt",
        "recommended_material": "PETG" if params.foot_height > 0 else "PLA"
    }


def export_parameter_summary(filename: Path, params: FlowerpotParams) -> None:
    """Export parameter summary to a JSON file."""
    # Calculate derived dimensions
    top_radius: float = params.top_diameter / 2.0
    bottom_radius: float = params.bottom_diameter / 2.0 if params.bottom_diameter > 0 else top_radius - params.height * math.tan(math.radians(params.taper_angle))
    inner_radius_top: float = top_radius - params.wall_thickness
    inner_radius_bottom: float = bottom_radius - params.wall_thickness
    
    # Calculate approximate volumes (simplified)
    outer_volume: float = (math.pi * params.height / 3.0) * (top_radius**2 + top_radius * bottom_radius + bottom_radius**2)
    inner_volume: float = (math.pi * (params.height - params.base_thickness) / 3.0) * (inner_radius_top**2 + inner_radius_top * inner_radius_bottom + inner_radius_bottom**2) if inner_radius_bottom > 0 else 0
    material_volume: float = outer_volume - inner_volume
    
    # Get 3D printing guidance
    printing_guidance = calculate_printing_guidance(params)
    
    summary = {
        "parameters": {
            "top_diameter_mm": params.top_diameter,
            "bottom_diameter_mm": params.bottom_diameter,
            "taper_angle_degrees": params.taper_angle,
            "height_mm": params.height,
            "wall_thickness_mm": params.wall_thickness,
            "base_thickness_mm": params.base_thickness,
            "drain_diameter_mm": params.drain_diameter,
            "number_of_drains": params.number_of_drains,
            "rim_thickness_mm": params.rim_thickness,
            "rim_height_mm": params.rim_height,
            "foot_height_mm": params.foot_height,
            "foot_ring_count": params.foot_ring_count,
            "shape": params.shape,
            "width_mm": params.width if params.width > 0 else params.top_diameter * 0.7,
            "pattern": params.pattern,
            "pattern_depth_mm": params.pattern_depth,
            "modular": params.modular,
            "sections": params.sections,
        },
        "dimensions": {
            "top_radius_mm": round(top_radius, 3),
            "bottom_radius_mm": round(bottom_radius, 3),
            "inner_radius_top_mm": round(inner_radius_top, 3),
            "inner_radius_bottom_mm": round(inner_radius_bottom, 3) if inner_radius_bottom > 0 else 0,
            "rim_outer_diameter_mm": round(params.top_diameter + 2 * params.rim_thickness, 3) if params.rim_thickness > 0 else params.top_diameter,
        },
        "volumes": {
            "outer_volume_cm3": round(outer_volume / 1000.0, 2),
            "inner_volume_cm3": round(inner_volume / 1000.0, 2) if inner_radius_bottom > 0 else 0,
            "material_volume_cm3": round(material_volume / 1000.0, 2),
            "water_capacity_ml": round(inner_volume / 1000.0, 0) if inner_radius_bottom > 0 else 0,
        },
        "printing_guidance": {
            "volume_cm3": printing_guidance["volume_cm3"],
            "material_weight_g": printing_guidance["material_weight_g"],
            "estimated_time_minutes": printing_guidance["estimated_time_minutes"],
            "estimated_cost_usd": printing_guidance["estimated_cost_usd"],
            "layer_height_mm": printing_guidance["layer_height_mm"],
            "infill_percent": printing_guidance["infill_percent"],
            "supports_needed": printing_guidance["supports_needed"],
            "print_speed_mm_s": printing_guidance["print_speed_mm_s"],
            "bed_adhesion": printing_guidance["bed_adhesion"],
            "recommended_material": printing_guidance["recommended_material"],
            "recommendations": printing_guidance["recommendations"],
        },
        "export_info": {
            "format": "parametric_flowerpot_v1",
            "generator": "flowerpots.py",
            "timestamp": None,  # Could add timestamp if needed
        }
    }
    
    summary_filename = filename.with_suffix('.json')
    try:
        with open(summary_filename, 'w') as f:
            json.dump(summary, f, indent=2)
        logging.info(f"Exported parameter summary to {summary_filename}")
    except Exception as e:
        logging.error(f"Failed to export parameter summary: {e}")


def export_step(pot: cq.Workplane, filename: Path) -> None:
    """Export the pot as a STEP file."""
    step_filename = filename.with_suffix('.step')
    try:
        cq.exporters.export(pot, str(step_filename), "STEP")
        logging.info(f"Exported STEP file to {step_filename}")
    except Exception as e:
        logging.error(f"Failed to export STEP file: {e}")


def export_stl(pot: cq.Workplane, filename: Path) -> None:
    """Export the pot as an STL file for 3D printing."""
    stl_filename = filename.with_suffix('.stl')
    try:
        cq.exporters.export(pot, str(stl_filename), "STL")
        logging.info(f"Exported STL file to {stl_filename}")
    except Exception as e:
        logging.error(f"Failed to export STL file: {e}")


def setup_logging() -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )


def validate_parameters(params: FlowerpotParams) -> None:
    """
    Validate input parameters and raise ValueError for invalid combinations.
    """
    
    # Check for negative values and zero heights
    if params.top_diameter <= 0:
        raise ValueError("Top diameter must be positive")
    if params.bottom_diameter < 0:
        raise ValueError("Bottom diameter cannot be negative")
    if params.height <= 0:
        raise ValueError("Height must be positive")
    if params.wall_thickness <= 0:
        raise ValueError("Wall thickness must be positive")
    if params.base_thickness <= 0:
        raise ValueError("Base thickness must be positive")
    if params.drain_diameter < 0:
        raise ValueError("Drain diameter cannot be negative")
    if params.number_of_drains < 0:
        raise ValueError("Number of drains cannot be negative")
    if params.rim_thickness < 0:
        raise ValueError("Rim thickness cannot be negative")
    if params.rim_height < 0:
        raise ValueError("Rim height cannot be negative")
    if params.foot_height < 0:
        raise ValueError("Foot height cannot be negative")
    if params.foot_ring_count < 0:
        raise ValueError("Foot ring count cannot be negative")
    
    # Check for reasonable angle ranges
    if abs(params.taper_angle) > 45:
        raise ValueError("Taper angle should be between -45 and 45 degrees")
    
    # Check diameter ratios
    if params.bottom_diameter > 0 and params.bottom_diameter > params.top_diameter:
        raise ValueError("Bottom diameter cannot exceed top diameter")
    
    # Calculate bottom radius based on taper if not specified
    radius = params.top_diameter / 2.0
    taper = math.tan(math.radians(params.taper_angle))
    bottom_radius = params.bottom_diameter / 2.0 if params.bottom_diameter > 0 else radius - params.height * taper
    
    if bottom_radius <= 0:
        raise ValueError("Calculated bottom radius is non-positive - reduce taper angle or increase top diameter")
    
    # Check wall thickness vs bottom radius
    min_bottom_radius = params.wall_thickness + 1.0  # Leave at least 1mm inner radius
    if bottom_radius < min_bottom_radius:
        raise ValueError(f"Bottom radius too small for wall thickness. Minimum bottom diameter: {min_bottom_radius * 2:.1f}mm")
    
    # Check drain diameter vs pot size
    if params.drain_diameter > 0 and params.number_of_drains > 0:
        inner_radius_bottom = bottom_radius - params.wall_thickness
        max_drain_diameter = inner_radius_bottom * 0.8  # Don't exceed 80% of inner radius
        if params.drain_diameter > max_drain_diameter:
            raise ValueError(f"Drain diameter too large for pot size. Maximum: {max_drain_diameter:.1f}mm")
    
    # Check rim dimensions
    if params.rim_height > params.height * 0.3:  # Rim shouldn't be more than 30% of total height
        raise ValueError("Rim height too large relative to total height")
    
    # Check foot dimensions
    if params.foot_height > params.base_thickness:
        raise ValueError("Foot height cannot exceed base thickness")


def add_decorative_pattern(pot: cq.Workplane, params: FlowerpotParams) -> cq.Workplane:
    """Add decorative patterns to the pot surface."""
    if params.pattern == "none":
        return pot
    
    pattern_height = params.height - params.base_thickness - params.rim_height
    
    if params.pattern == "lines":
        # Add vertical lines around the pot
        num_lines = 12
        line_width = 1.0
        line_depth = params.pattern_depth
        
        lines = None
        for i in range(num_lines):
            angle = 360 * i / num_lines
            line = (
                cq.Workplane("XY")
                .workplane(offset=params.base_thickness)
                .rect(line_width, pattern_height)
                .extrude(line_depth)
                .rotate((0, 0, 0), (0, 0, 1), angle)
                .translate((0, 0, 0))
            )
            lines = line if lines is None else lines.union(line)
        
        if lines:
            pot = pot.union(lines)
    
    elif params.pattern == "dots":
        # Add dot pattern
        dot_diameter = 3.0
        dot_depth = params.pattern_depth
        rows = 8
        cols = 12
        
        dots = None
        for row in range(rows):
            for col in range(cols):
                angle = 360 * col / cols
                height_offset = params.base_thickness + (row + 1) * pattern_height / (rows + 1)
                dot = (
                    cq.Workplane("XY")
                    .workplane(offset=height_offset)
                    .circle(dot_diameter / 2)
                    .extrude(dot_depth)
                    .rotate((0, 0, 0), (0, 0, 1), angle)
                )
                dots = dot if dots is None else dots.union(dot)
        
        if dots:
            pot = pot.union(dots)
    
    elif params.pattern == "waves":
        # Add wave pattern
        wave_amplitude = params.pattern_depth
        wave_frequency = 8
        wave_width = 2.0
        
        waves = None
        for i in range(wave_frequency):
            angle = 360 * i / wave_frequency
            # Create wave profile as a series of points
            wave_points = []
            num_points = 20
            for j in range(num_points + 1):
                y = j * pattern_height / num_points
                x = wave_amplitude * math.sin(2 * math.pi * j / num_points * 2)  # 2 complete waves
                wave_points.append((x, y))
            
            # Create the wave shape
            wave_profile = (
                cq.Workplane("XZ")
                .polyline(wave_points)
                .rect(wave_width, 0.1)
                .extrude(1)
            )
            
            # Position and rotate the wave
            wave = (
                wave_profile
                .rotate((0, 0, 0), (0, 0, 1), angle)
                .translate((0, 0, params.base_thickness))
            )
            waves = wave if waves is None else waves.union(wave)
        
        if waves:
            pot = pot.union(waves)
    
    return pot


def create_square_pot(params: FlowerpotParams) -> cq.Workplane:
    """Create a square-shaped pot."""
    size = params.top_diameter
    bottom_size = params.bottom_diameter if params.bottom_diameter > 0 else size - 2 * params.height * math.tan(math.radians(params.taper_angle))
    
    # Main body profile
    body_profile = [
        (bottom_size/2, 0),
        (size/2, params.height),
    ]
    
    if params.rim_thickness > 0 and params.rim_height > 0:
        top_outer = size/2 + params.rim_thickness
        bottom_outer = max(size/2 + params.rim_thickness - params.rim_height, size/2)
        body_profile.append((top_outer, params.height))
        body_profile.append((bottom_outer, params.height - params.rim_height))
        if bottom_outer > size/2:
            body_profile.append((size/2, params.height - params.rim_height))
    
    body_profile.extend([
        (size/2 - params.wall_thickness, params.height),
        (bottom_size/2 - params.wall_thickness, params.base_thickness),
        (0, params.base_thickness),
        (0, 0),
    ])
    
    # Create the pot by revolving and then making it square
    pot = (
        cq.Workplane("XZ")
        .polyline(body_profile)
        .close()
        .revolve()
    )
    
    # Convert to square shape
    pot = pot.intersect(
        cq.Workplane("XY")
        .rect(size, size)
        .extrude(params.height * 2)
        .translate((0, 0, -params.height))
    )
    
    return pot


def create_rectangular_pot(params: FlowerpotParams) -> cq.Workplane:
    """Create a rectangular-shaped pot."""
    length = params.top_diameter
    width = params.width if params.width > 0 else length * 0.7
    bottom_length = params.bottom_diameter if params.bottom_diameter > 0 else length - 2 * params.height * math.tan(math.radians(params.taper_angle))
    bottom_width = bottom_length * (width / length) if bottom_length > 0 else width - 2 * params.height * math.tan(math.radians(params.taper_angle))
    
    # Create the pot as a rectangular solid
    outer = (
        cq.Workplane("XY")
        .rect(length, width)
        .extrude(params.height)
    )
    
    # Create inner cavity
    inner = (
        cq.Workplane("XY")
        .rect(length - 2*params.wall_thickness, width - 2*params.wall_thickness)
        .workplane(offset=params.base_thickness)
        .extrude(params.height - params.base_thickness)
    )
    
    pot = outer.cut(inner)
    
    # Add rim if specified
    if params.rim_thickness > 0 and params.rim_height > 0:
        rim = (
            cq.Workplane("XY")
            .rect(length + 2*params.rim_thickness, width + 2*params.rim_thickness)
            .extrude(params.rim_height)
            .translate((0, 0, params.height - params.rim_height))
        )
        pot = pot.union(rim)
    
    return pot


def create_modular_sections(params: FlowerpotParams) -> cq.Workplane:
    """Create stackable modular sections."""
    section_height = params.height / params.sections
    total_pot = None
    
    for i in range(params.sections):
        # Create parameters for this section
        section_params = FlowerpotParams(
            top_diameter=params.top_diameter,
            bottom_diameter=params.top_diameter - 2 * section_height * math.tan(math.radians(params.taper_angle)),
            taper_angle=params.taper_angle,
            height=section_height,
            wall_thickness=params.wall_thickness,
            base_thickness=params.base_thickness,
            drain_diameter=params.drain_diameter if i == params.sections - 1 else 0,  # Only last section has drains
            number_of_drains=params.number_of_drains,
            rim_thickness=params.rim_thickness if i == params.sections - 1 else 0,  # Only top section has rim
            rim_height=params.rim_height if i == params.sections - 1 else 0,
            foot_height=params.foot_height if i == 0 else 0,  # Only bottom section has feet
            foot_ring_count=params.foot_ring_count,
            shape=params.shape,
            width=params.width,
            pattern=params.pattern,
            pattern_depth=params.pattern_depth,
            modular=False,  # Prevent infinite recursion
            sections=1,
        )
        
        # Create the section
        if params.shape == "circular":
            section = make_circular_pot(section_params)
        elif params.shape == "square":
            section = create_square_pot(section_params)
        elif params.shape == "rectangular":
            section = create_rectangular_pot(section_params)
        else:
            section = make_circular_pot(section_params)
        
        # Add interlocking features
        if i > 0:  # Add male connector to bottom
            connector_height = 2.0
            connector = (
                cq.Workplane("XY")
                .circle(params.top_diameter/2 - params.wall_thickness - 1.0)
                .extrude(connector_height)
            )
            section = section.union(connector)
        
        if i < params.sections - 1:  # Add female connector to top
            connector_height = 2.0
            connector = (
                cq.Workplane("XY")
                .circle(params.top_diameter/2 - params.wall_thickness - 1.5)
                .extrude(connector_height)
                .translate((0, 0, section_height - connector_height))
            )
            section = section.cut(connector)
        
        # Position the section
        section = section.translate((0, 0, i * section_height))
        
        # Combine with total pot
        total_pot = section if total_pot is None else total_pot.union(section)
    
    return total_pot


def make_circular_pot(params: FlowerpotParams) -> cq.Workplane:
    """
    Generate a parametric flowerpot as a STEP file.

    Parameters
    ----------
    params
        FlowerpotParams containing all flowerpot dimensions and settings.
    """

    # Calculate taper factor
    taper: float = math.tan(math.radians(params.taper_angle))

    # Compute radii
    radius: float = params.top_diameter / 2.0
    bottom_radius: float = params.bottom_diameter / 2.0 if params.bottom_diameter > 0 else radius - params.height * taper
    inner_radius_top: float = radius - params.wall_thickness
    inner_radius_bottom: float = bottom_radius - params.wall_thickness
    
    # Adjust wall thickness if needed for bottom radius
    wall_thickness = params.wall_thickness
    if inner_radius_bottom <= 0:
        min_inner: float = 0.5
        wall_thickness = min(bottom_radius - min_inner, radius - min_inner)
        wall_thickness = max(wall_thickness, 0.1)
        inner_radius_bottom = bottom_radius - wall_thickness
        inner_radius_top = radius - wall_thickness
        logging.warning(
            f"Wall thickness too large for bottom radius; "
            f"capping to {wall_thickness:.2f}."
        )

    # Main pot body + rim profile revolved around Z axis
    body_profile: list[tuple[float, float]] = [
        (bottom_radius, 0),
        (radius, params.height),
    ]
    if params.rim_thickness > 0 and params.rim_height > 0:
        top_outer: float = radius + params.rim_thickness
        bottom_outer: float = max(radius + params.rim_thickness - params.rim_height, radius)
        body_profile.append((top_outer, params.height))
        body_profile.append((bottom_outer, params.height - params.rim_height))
        if bottom_outer > radius:
            body_profile.append((radius, params.height - params.rim_height))
    body_profile.extend([
        (inner_radius_top, params.height),
        (inner_radius_bottom, params.base_thickness),
        (0, params.base_thickness),
        (0, 0),
    ])

    pot: cq.Workplane = (
        cq.Workplane("XZ")
        .polyline(body_profile)
        .close()
        .revolve()
    )

    # Bottom ventilation feet / rings
    foot_ring_count = params.foot_ring_count
    if params.foot_height > 0 and foot_ring_count > 0:
        foot_ring_width: float = bottom_radius / foot_ring_count
        min_width: float = params.foot_height * 2.0
        if foot_ring_width <= min_width:
            max_rings: int = int(bottom_radius / min_width)
            if max_rings >= bottom_radius / min_width:
                max_rings -= 1
            if max_rings < 1:
                logging.warning(
                    f"Foot height {params.foot_height} is too large for "
                    f"bottom radius {bottom_radius:.2f}; disabling feet."
                )
                foot_ring_count = 0
            else:
                logging.warning(
                    f"Foot height {params.foot_height} is too big for "
                    f"{foot_ring_count} rings; reducing to {max_rings}."
                )
                foot_ring_count = max_rings
                foot_ring_width = bottom_radius / foot_ring_count

    if params.foot_height > 0 and foot_ring_count > 0:
        flare = params.foot_height * math.tan(math.radians(45))

        feet = None
        for i in range(foot_ring_count):
            outer_r = bottom_radius - i * foot_ring_width
            inner_r = outer_r - foot_ring_width
            ring_profile = [
                (outer_r, 0),
                (outer_r - flare, -params.foot_height),
                (inner_r + flare, -params.foot_height),
                (inner_r, 0),
            ]
            ring = (
                cq.Workplane("XZ")
                .polyline(ring_profile)
                .close()
                .revolve()
            )
            feet = ring if feet is None else feet.union(ring)

        # cut radial slits through the feet, one per drain
        if params.number_of_drains > 0 and feet is not None:
            slit_width: float = 0.0
            slit_length: float = bottom_radius + flare + 2

            half_top: float = slit_width / 2.0
            half_bottom: float = half_top + flare
            slit_profile = [
                (half_top, 1),
                (half_top, 0),
                (half_bottom, -params.foot_height),
                (half_bottom, -params.foot_height - 1),
                (-half_bottom, -params.foot_height - 1),
                (-half_bottom, -params.foot_height),
                (-half_top, 0),
                (-half_top, 1),
            ]
            slit = (
                cq.Workplane("YZ")
                .polyline(slit_profile)
                .close()
                .extrude(slit_length * 2.0)
                #.translate((slit_length / 2, 0, 0))
            )
            for i in range(params.number_of_drains):
                angle: float = 2 * math.pi * i / params.number_of_drains
                slit_rotated: cq.Workplane = slit.rotate(
                    (0, 0, 0), (0, 0, 1), math.degrees(angle)
                )
                feet = feet.cut(slit_rotated)

        pot = pot.union(feet)

    # Drainage holes
    if params.number_of_drains > 0 and params.drain_diameter > 0:
        hole_radius: float = params.drain_diameter / 2.0

        if params.number_of_drains > 1:
            # arrange holes in a circle around the center of the base
            drain_circle_radius: float = min(
                params.drain_diameter * 2.0,
                inner_radius_bottom - hole_radius - 1.0,
            )
            min_circle_radius: float = hole_radius / math.sin(math.pi / params.number_of_drains)
            if drain_circle_radius < min_circle_radius:
                if drain_circle_radius <= hole_radius:
                    logging.warning(
                        f"Drain diameter {params.drain_diameter} too large "
                        f"for pot base; disabling drains."
                    )
                    params.number_of_drains = 0
                else:
                    max_drains: int = int(
                        math.pi / math.asin(hole_radius / drain_circle_radius)
                    )
                    if max_drains < 1:
                        logging.warning(
                            f"Drain diameter {params.drain_diameter} too large "
                            f"for pot base; disabling drains."
                        )
                        params.number_of_drains = 0
                    else:
                        logging.warning(
                            f"{params.number_of_drains} drains too large for "
                            f"pot base; reducing to {max_drains}."
                        )
                        params.number_of_drains = max_drains

        if params.number_of_drains == 1:
            holes = (
                cq.Workplane("XY")
                .workplane(offset=-params.foot_height)
                .circle(hole_radius)
                .extrude(params.height)
            )
        elif params.number_of_drains > 1:
            drain_circle_radius = min(
                params.drain_diameter * 2.0,
                inner_radius_bottom - hole_radius - 1.0,
            )
            points: list[tuple[float, float]] = [
                (
                    drain_circle_radius * math.cos(2 * math.pi * i / params.number_of_drains),
                    drain_circle_radius * math.sin(2 * math.pi * i / params.number_of_drains),
                )
                for i in range(params.number_of_drains)
            ]
            holes = (
                cq.Workplane("XY")
                .workplane(offset=-params.foot_height)
                .pushPoints(points)
                .circle(hole_radius)
                .extrude(params.height)
            )
        else:
            holes = None

        if holes is not None:
            pot = pot.cut(holes)

    return pot


def make_flowerpot(params: FlowerpotParams) -> cq.Workplane:
    """
    Generate a parametric flowerpot with advanced geometry options.

    Parameters
    ----------
    params
        FlowerpotParams containing all flowerpot dimensions and settings.
    """
    
    # Handle modular sections first
    if params.modular and params.sections > 1:
        pot = create_modular_sections(params)
    else:
        # Handle different shapes
        if params.shape == "circular":
            pot = make_circular_pot(params)
        elif params.shape == "square":
            pot = create_square_pot(params)
        elif params.shape == "rectangular":
            pot = create_rectangular_pot(params)
        else:
            pot = make_circular_pot(params)  # Default to circular
    
    # Add decorative patterns
    pot = add_decorative_pattern(pot, params)
    
    return pot


def interactive_mode() -> FlowerpotParams:
    """Interactive mode to prompt user for parameters."""
    print("🌸 Interactive Flowerpot Generator")
    print("=" * 40)
    
    def get_float(prompt: str, default: float) -> float:
        while True:
            try:
                value = input(f"{prompt} [{default}]: ").strip()
                return float(value) if value else default
            except ValueError:
                print("Please enter a valid number.")
    
    def get_int(prompt: str, default: int) -> int:
        while True:
            try:
                value = input(f"{prompt} [{default}]: ").strip()
                return int(value) if value else default
            except ValueError:
                print("Please enter a valid integer.")
    
    def get_choice(prompt: str, choices: list[str], default: str) -> str:
        while True:
            value = input(f"{prompt} [{default}] ({', '.join(choices)}): ").strip()
            if not value:
                return default
            if value in choices:
                return value
            print(f"Please choose from: {', '.join(choices)}")
    
    def get_bool(prompt: str, default: bool) -> bool:
        while True:
            value = input(f"{prompt} [{'y' if default else 'n'}]: ").strip().lower()
            if not value:
                return default
            if value in ['y', 'yes', 'true', '1']:
                return True
            elif value in ['n', 'no', 'false', '0']:
                return False
            print("Please enter y/n or yes/no.")
    
    print("\n📏 Basic Dimensions:")
    diameter = get_float("Top diameter (mm)", 120.0)
    height = get_float("Height (mm)", 100.0)
    wall = get_float("Wall thickness (mm)", 3.0)
    base = get_float("Base thickness (mm)", 4.0)
    
    print("\n🕳️ Drainage:")
    drain_diameter = get_float("Drain hole diameter (mm, 0 to disable)", 8.0)
    drains = get_int("Number of drain holes", 4)
    
    print("\n📐 Shape & Style:")
    shape = get_choice("Pot shape", ["circular", "square", "rectangular"], "circular")
    width = 0.0
    if shape == "rectangular":
        width = get_float("Width for rectangular pot (mm, 0 = 0.7 × diameter)", 0.0)
    
    pattern = get_choice("Decorative pattern", ["none", "lines", "dots", "waves"], "none")
    pattern_depth = 0.5
    if pattern != "none":
        pattern_depth = get_float("Pattern depth (mm)", 0.5)
    
    modular = get_bool("Create modular stackable sections", False)
    sections = 1
    if modular:
        sections = get_int("Number of sections", 2)
    
    print("\n🎯 Advanced Options:")
    bottom_diameter = get_float("Bottom diameter (mm, 0 = auto-calculate)", 0.0)
    taper = get_float("Taper angle (degrees)", 5.0)
    rim_thickness = get_float("Rim thickness (mm)", 2.0)
    rim_height = get_float("Rim height (mm)", 5.0)
    foot = get_float("Foot height (mm, 0 to disable)", 3.0)
    rings = get_int("Number of foot rings", 2)
    
    print("\n📁 Output:")
    format_choice = get_choice("Output format", ["stl", "step", "all"], "stl")
    summary = get_bool("Export parameter summary", False)
    
    # Create the parameters object
    params = FlowerpotParams(
        top_diameter=diameter,
        bottom_diameter=bottom_diameter,
        taper_angle=taper,
        height=height,
        wall_thickness=wall,
        base_thickness=base,
        drain_diameter=drain_diameter,
        number_of_drains=drains,
        rim_thickness=rim_thickness,
        rim_height=rim_height,
        foot_height=foot,
        foot_ring_count=rings,
        shape=shape,
        width=width,
        pattern=pattern,
        pattern_depth=pattern_depth,
        modular=modular,
        sections=sections,
    )
    
    print(f"\n✅ Configuration complete!")
    print(f"   Shape: {shape}")
    if shape == "rectangular":
        print(f"   Dimensions: {diameter}mm × {width}mm × {height}mm")
    else:
        print(f"   Dimensions: {diameter}mm diameter × {height}mm")
    if pattern != "none":
        print(f"   Pattern: {pattern} ({pattern_depth}mm depth)")
    if modular:
        print(f"   Modular: {sections} sections")
    print(f"   Format: {format_choice}")
    if summary:
        print(f"   Summary: JSON file will be generated")
    
    return params, format_choice, summary


def main() -> None:
    setup_logging()
    
    parser = argparse.ArgumentParser(description="Generate a parametric flowerpot STEP file.")
    parser.add_argument("--diameter", type=float, default=120.0, help="Outer top diameter in mm.")
    parser.add_argument("--bottom-diameter", type=float, default=0.0, help="Outer bottom diameter in mm.")
    parser.add_argument("--height", type=float, default=100.0, help="Total height in mm.")
    parser.add_argument("--wall", type=float, default=3.0, help="Wall thickness in mm.")
    parser.add_argument("--base", type=float, default=4.0, help="Base thickness in mm.")
    parser.add_argument("--drain-diameter", type=float, default=8.0, help="Drainage hole diameter in mm (0 to disable).")
    parser.add_argument("--drains", type=int, default=4, help="Number of drainage holes.")
    parser.add_argument("--taper", type=float, default=5.0, help="Wall taper angle in degrees.")
    parser.add_argument("--foot", type=float, default=3.0, help="Height of bottom ventilation feet in mm (0 to disable).")
    parser.add_argument("--rings", type=int, default=2, help="Number of concentric bottom ventilation rings.")
    parser.add_argument("--rim-thickness", type=float, default=2.0, help="Extra rim thickness in mm.")
    parser.add_argument("--rim-height", type=float, default=5.0, help="Rim height in mm.")
    parser.add_argument("--format", choices=["step", "stl", "all"], default="stl", 
                       help="Output format: stl (default), step, or all")
    parser.add_argument("--summary", action="store_true", 
                       help="Export parameter summary as JSON file")
    parser.add_argument("--preset", type=str, 
                       help="Use a preset (built-in: succulent, herb, tree, or saved preset file)")
    parser.add_argument("--save-preset", type=str, 
                       help="Save current parameters as a named preset")
    parser.add_argument("--list-presets", action="store_true", 
                       help="List all available presets and exit")
    # Advanced geometry arguments
    parser.add_argument("--shape", choices=["circular", "square", "rectangular"], default="circular",
                       help="Pot shape: circular (default), square, or rectangular")
    parser.add_argument("--width", type=float, default=0.0,
                       help="Width for rectangular pots (0 = use 0.7 * diameter)")
    parser.add_argument("--pattern", choices=["none", "lines", "dots", "waves"], default="none",
                       help="Decorative pattern: none (default), lines, dots, or waves")
    parser.add_argument("--pattern-depth", type=float, default=0.5,
                       help="Depth of decorative patterns in mm")
    parser.add_argument("--modular", action="store_true",
                       help="Create stackable modular sections")
    parser.add_argument("--sections", type=int, default=1,
                       help="Number of modular sections")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive mode with parameter prompts")
    parser.add_argument("--print-guidance", action="store_true",
                       help="Show 3D printing recommendations and material usage")
    parser.add_argument("filename", type=Path, default=Path("flowerpot"), nargs="?", help="Output file path.")

    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle argparse errors gracefully
        logging.error("Invalid command line arguments. Use --help for usage information.")
        sys.exit(1)

    # Handle --list-presets
    if args.list_presets:
        list_presets()
        sys.exit(0)

    # Handle interactive mode
    if args.interactive:
        params, format_choice, summary_choice = interactive_mode()
        # Override args with interactive choices
        args.format = format_choice
        args.summary = summary_choice
    else:
        # Create parameters struct
        if args.preset:
            params = load_preset(args.preset)
            logging.info(f"Using preset: {args.preset}")
        else:
            params = FlowerpotParams(
                top_diameter=args.diameter,
                bottom_diameter=args.bottom_diameter,
                taper_angle=args.taper,
                height=args.height,
                wall_thickness=args.wall,
                base_thickness=args.base,
                drain_diameter=args.drain_diameter,
                number_of_drains=args.drains,
                rim_thickness=args.rim_thickness,
                rim_height=args.rim_height,
                foot_height=args.foot,
                foot_ring_count=args.rings,
                shape=args.shape,
                width=args.width,
                pattern=args.pattern,
                pattern_depth=args.pattern_depth,
                modular=args.modular,
                sections=args.sections,
            )

    # Handle --print-guidance
    if args.print_guidance:
        guidance = calculate_printing_guidance(params)
        print(f"\n🖨️  3D Printing Guidance for {params.shape} pot")
        print("=" * 50)
        print(f"📊 Material Usage:")
        print(f"   Volume: {guidance['volume_cm3']} cm³")
        print(f"   Weight: {guidance['material_weight_g']} g")
        print(f"   Estimated Cost: ${guidance['estimated_cost_usd']}")
        print(f"   Estimated Time: {guidance['estimated_time_minutes']} minutes")
        print(f"\n⚙️  Recommended Settings:")
        print(f"   Layer Height: {guidance['layer_height_mm']} mm")
        print(f"   Infill: {guidance['infill_percent']}%")
        print(f"   Print Speed: {guidance['print_speed_mm_s']} mm/s")
        print(f"   Material: {guidance['recommended_material']}")
        print(f"   Bed Adhesion: {guidance['bed_adhesion']}")
        print(f"   Supports Needed: {'Yes' if guidance['supports_needed'] else 'No'}")
        print(f"\n💡 Recommendations:")
        for rec in guidance['recommendations']:
            print(f"   • {rec}")
        print(f"\n⚠️  WARNING: No print has been done using these instructions yet.")
        print()
        sys.exit(0)

    # Handle --save-preset
    if args.save_preset:
        save_preset(args.save_preset, params)
        sys.exit(0)

    # Validate parameters before generating the pot
    try:
        validate_parameters(params)
    except ValueError as e:
        logging.error(f"Parameter validation failed: {e}")
        sys.exit(1)

    try:
        pot = make_flowerpot(params)

        try:
            # Export based on format choice
            if args.format in ["step", "all"]:
                export_step(pot, args.filename)
            
            if args.format in ["stl", "all"]:
                export_stl(pot, args.filename)
            
            if args.summary:
                export_parameter_summary(args.filename, params)
                
        except Exception as e:
            logging.error(f"Failed to export flowerpot: {e}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to generate flowerpot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
