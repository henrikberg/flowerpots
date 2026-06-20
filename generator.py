import cadquery as cq
import argparse
import json
import logging
import math
import sys
from pathlib import Path


def export_parameter_summary(
    filename: Path,
    top_diameter: float,
    bottom_diameter: float,
    taper_angle: float,
    height: float,
    wall_thickness: float,
    base_thickness: float,
    drain_diameter: float,
    number_of_drains: int,
    rim_thickness: float,
    rim_height: float,
    foot_height: float,
    foot_ring_count: int,
) -> None:
    """Export parameter summary to a JSON file."""
    # Calculate derived dimensions
    top_radius: float = top_diameter / 2.0
    bottom_radius: float = bottom_diameter / 2.0 if bottom_diameter > 0 else top_radius - height * math.tan(math.radians(taper_angle))
    inner_radius_top: float = top_radius - wall_thickness
    inner_radius_bottom: float = bottom_radius - wall_thickness
    
    # Calculate approximate volumes (simplified)
    outer_volume: float = (math.pi * height / 3.0) * (top_radius**2 + top_radius * bottom_radius + bottom_radius**2)
    inner_volume: float = (math.pi * (height - base_thickness) / 3.0) * (inner_radius_top**2 + inner_radius_top * inner_radius_bottom + inner_radius_bottom**2) if inner_radius_bottom > 0 else 0
    material_volume: float = outer_volume - inner_volume
    
    summary = {
        "parameters": {
            "top_diameter_mm": top_diameter,
            "bottom_diameter_mm": bottom_diameter,
            "taper_angle_degrees": taper_angle,
            "height_mm": height,
            "wall_thickness_mm": wall_thickness,
            "base_thickness_mm": base_thickness,
            "drain_diameter_mm": drain_diameter,
            "number_of_drains": number_of_drains,
            "rim_thickness_mm": rim_thickness,
            "rim_height_mm": rim_height,
            "foot_height_mm": foot_height,
            "foot_ring_count": foot_ring_count,
        },
        "dimensions": {
            "top_radius_mm": round(top_radius, 3),
            "bottom_radius_mm": round(bottom_radius, 3),
            "inner_radius_top_mm": round(inner_radius_top, 3),
            "inner_radius_bottom_mm": round(inner_radius_bottom, 3) if inner_radius_bottom > 0 else 0,
            "rim_outer_diameter_mm": round(top_diameter + 2 * rim_thickness, 3) if rim_thickness > 0 else top_diameter,
        },
        "volumes": {
            "outer_volume_cm3": round(outer_volume / 1000.0, 2),
            "inner_volume_cm3": round(inner_volume / 1000.0, 2) if inner_radius_bottom > 0 else 0,
            "material_volume_cm3": round(material_volume / 1000.0, 2),
            "water_capacity_ml": round(inner_volume / 1000.0, 0) if inner_radius_bottom > 0 else 0,
        },
        "printing_info": {
            "recommended_layer_height_mm": "0.2-0.3",
            "recommended_infill_percent": "15-25",
            "supports_needed": foot_height > 0,
            "estimated_print_time_hours": round(material_volume / 1000.0 * 0.1, 1),  # Rough estimate
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


def validate_parameters(
    top_diameter: float,
    bottom_diameter: float,
    taper_angle: float,
    height: float,
    wall_thickness: float,
    base_thickness: float,
    drain_diameter: float,
    number_of_drains: int,
    rim_thickness: float,
    rim_height: float,
    foot_height: float,
    foot_ring_count: int,
) -> None:
    """
    Validate input parameters and raise ValueError for invalid combinations.
    """
    
    # Check for negative values and zero heights
    if top_diameter <= 0:
        raise ValueError("Top diameter must be positive")
    if bottom_diameter < 0:
        raise ValueError("Bottom diameter cannot be negative")
    if height <= 0:
        raise ValueError("Height must be positive")
    if wall_thickness <= 0:
        raise ValueError("Wall thickness must be positive")
    if base_thickness <= 0:
        raise ValueError("Base thickness must be positive")
    if drain_diameter < 0:
        raise ValueError("Drain diameter cannot be negative")
    if number_of_drains < 0:
        raise ValueError("Number of drains cannot be negative")
    if rim_thickness < 0:
        raise ValueError("Rim thickness cannot be negative")
    if rim_height < 0:
        raise ValueError("Rim height cannot be negative")
    if foot_height < 0:
        raise ValueError("Foot height cannot be negative")
    if foot_ring_count < 0:
        raise ValueError("Foot ring count cannot be negative")
    
    # Check for reasonable angle ranges
    if abs(taper_angle) > 45:
        raise ValueError("Taper angle should be between -45 and 45 degrees")
    
    # Check diameter ratios
    if bottom_diameter > 0 and bottom_diameter > top_diameter:
        raise ValueError("Bottom diameter cannot exceed top diameter")
    
    # Calculate bottom radius based on taper if not specified
    radius = top_diameter / 2.0
    taper = math.tan(math.radians(taper_angle))
    bottom_radius = bottom_diameter / 2.0 if bottom_diameter > 0 else radius - height * taper
    
    if bottom_radius <= 0:
        raise ValueError("Calculated bottom radius is non-positive - reduce taper angle or increase top diameter")
    
    # Check wall thickness vs bottom radius
    min_bottom_radius = wall_thickness + 1.0  # Leave at least 1mm inner radius
    if bottom_radius < min_bottom_radius:
        raise ValueError(f"Bottom radius too small for wall thickness. Minimum bottom diameter: {min_bottom_radius * 2:.1f}mm")
    
    # Check drain diameter vs pot size
    if drain_diameter > 0 and number_of_drains > 0:
        inner_radius_bottom = bottom_radius - wall_thickness
        max_drain_diameter = inner_radius_bottom * 0.8  # Don't exceed 80% of inner radius
        if drain_diameter > max_drain_diameter:
            raise ValueError(f"Drain diameter too large for pot size. Maximum: {max_drain_diameter:.1f}mm")
    
    # Check rim dimensions
    if rim_height > height * 0.3:  # Rim shouldn't be more than 30% of total height
        raise ValueError("Rim height too large relative to total height")
    
    # Check foot dimensions
    if foot_height > base_thickness:
        raise ValueError("Foot height cannot exceed base thickness")


def make_flowerpot(
    top_diameter: float = 120.0,
    bottom_diameter: float = 0.0,
    taper_angle: float = 5.0,
    height: float = 100.0,
    wall_thickness: float = 3.0,
    base_thickness: float = 4.0,
    drain_diameter: float = 8.0,
    number_of_drains: int = 1,
    rim_thickness: float = 2.0,
    rim_height: float = 5.0,
    foot_height: float = 3.0,
    foot_ring_count: int = 2,
) -> cq.Workplane:
    """
    Generate a parametric flowerpot as a STEP file.

    Parameters
    ----------
    top_diameter
        Outer diameter of the pot at the top rim (mm).
    bottom_diameter
        Outer diameter of the pot at the bottom (mm). If 0, the taper will be used.
    taper_angle
        Draft angle of the outer wall in degrees (positive narrows toward the bottom).
    height
        Total height of the pot (mm).
    wall_thickness
        Thickness of the side walls (mm).
    base_thickness
        Thickness of the bottom base (mm).
    drain_diameter
        Diameter of each drainage hole (mm). Set to 0 to omit.
    number_of_drains
        Number of drainage holes. 1 centers the hole; >1 arranges holes in a circle.
    rim_thickness
        Extra thickness added to the top rim (mm).
    rim_height
        Height of the reinforced rim (mm).
    foot_height
        Height of the bottom ventilation feet (mm). Set to 0 to omit.
    foot_ring_count
        Number of concentric rings on the bottom for ventilation.
    """

    # Calculate taper factor
    taper: float = math.tan(math.radians(taper_angle))

    # Compute radii
    radius: float = top_diameter / 2.0
    bottom_radius: float = bottom_diameter / 2.0 if bottom_diameter > 0 else radius - height * taper
    inner_radius_top: float = radius - wall_thickness
    inner_radius_bottom: float = bottom_radius - wall_thickness
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
        (radius, height),
    ]
    if rim_thickness > 0 and rim_height > 0:
        top_outer: float = radius + rim_thickness
        bottom_outer: float = max(radius + rim_thickness - rim_height, radius)
        body_profile.append((top_outer, height))
        body_profile.append((bottom_outer, height - rim_height))
        if bottom_outer > radius:
            body_profile.append((radius, height - rim_height))
    body_profile.extend([
        (inner_radius_top, height),
        (inner_radius_bottom, base_thickness),
        (0, base_thickness),
        (0, 0),
    ])

    pot: cq.Workplane = (
        cq.Workplane("XZ")
        .polyline(body_profile)
        .close()
        .revolve()
    )

    # Bottom ventilation feet / rings
    if foot_height > 0 and foot_ring_count > 0:
        foot_ring_width: float = bottom_radius / foot_ring_count
        min_width: float = foot_height * 2.0
        if foot_ring_width <= min_width:
            max_rings: int = int(bottom_radius / min_width)
            if max_rings >= bottom_radius / min_width:
                max_rings -= 1
            if max_rings < 1:
                logging.warning(
                    f"Foot height {foot_height} is too large for "
                    f"bottom radius {bottom_radius:.2f}; disabling feet."
                )
                foot_ring_count = 0
            else:
                logging.warning(
                    f"Foot height {foot_height} is too big for "
                    f"{foot_ring_count} rings; reducing to {max_rings}."
                )
                foot_ring_count = max_rings
                foot_ring_width = bottom_radius / foot_ring_count

    if foot_height > 0 and foot_ring_count > 0:
        flare = foot_height * math.tan(math.radians(45))

        feet = None
        for i in range(foot_ring_count):
            outer_r = bottom_radius - i * foot_ring_width
            inner_r = outer_r - foot_ring_width
            ring_profile = [
                (outer_r, 0),
                (outer_r - flare, -foot_height),
                (inner_r + flare, -foot_height),
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
        if number_of_drains > 0 and feet is not None:
            slit_width: float = 0.0
            slit_length: float = bottom_radius + flare + 2

            half_top: float = slit_width / 2.0
            half_bottom: float = half_top + flare
            slit_profile = [
                (half_top, 1),
                (half_top, 0),
                (half_bottom, -foot_height),
                (half_bottom, -foot_height - 1),
                (-half_bottom, -foot_height - 1),
                (-half_bottom, -foot_height),
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
            for i in range(number_of_drains):
                angle: float = 2 * math.pi * i / number_of_drains
                slit_rotated: cq.Workplane = slit.rotate(
                    (0, 0, 0), (0, 0, 1), math.degrees(angle)
                )
                feet = feet.cut(slit_rotated)

        pot = pot.union(feet)

    # Drainage holes
    if number_of_drains > 0 and drain_diameter > 0:
        hole_radius: float = drain_diameter / 2.0

        if number_of_drains > 1:
            # arrange holes in a circle around the center of the base
            drain_circle_radius: float = min(
                drain_diameter * 2.0,
                inner_radius_bottom - hole_radius - 1.0,
            )
            min_circle_radius: float = hole_radius / math.sin(math.pi / number_of_drains)
            if drain_circle_radius < min_circle_radius:
                if drain_circle_radius <= hole_radius:
                    logging.warning(
                        f"Drain diameter {drain_diameter} too large "
                        f"for pot base; disabling drains."
                    )
                    number_of_drains = 0
                else:
                    max_drains: int = int(
                        math.pi / math.asin(hole_radius / drain_circle_radius)
                    )
                    if max_drains < 1:
                        logging.warning(
                            f"Drain diameter {drain_diameter} too large "
                            f"for pot base; disabling drains."
                        )
                        number_of_drains = 0
                    else:
                        logging.warning(
                            f"{number_of_drains} drains too large for "
                            f"pot base; reducing to {max_drains}."
                        )
                        number_of_drains = max_drains

        if number_of_drains == 1:
            holes = (
                cq.Workplane("XY")
                .workplane(offset=-foot_height)
                .circle(hole_radius)
                .extrude(height)
            )
        elif number_of_drains > 1:
            drain_circle_radius = min(
                drain_diameter * 2.0,
                inner_radius_bottom - hole_radius - 1.0,
            )
            points: list[tuple[float, float]] = [
                (
                    drain_circle_radius * math.cos(2 * math.pi * i / number_of_drains),
                    drain_circle_radius * math.sin(2 * math.pi * i / number_of_drains),
                )
                for i in range(number_of_drains)
            ]
            holes = (
                cq.Workplane("XY")
                .workplane(offset=-foot_height)
                .pushPoints(points)
                .circle(hole_radius)
                .extrude(height)
            )
        else:
            holes = None

        if holes is not None:
            pot = pot.cut(holes)

    return pot


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
    parser.add_argument("filename", type=Path, default=Path("flowerpots.step"), nargs="?", help="Output file path.")

    try:
        args = parser.parse_args()
    except SystemExit:
        # Handle argparse errors gracefully
        logging.error("Invalid command line arguments. Use --help for usage information.")
        sys.exit(1)

    # Validate parameters before generating the pot
    try:
        validate_parameters(
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
        )
    except ValueError as e:
        logging.error(f"Parameter validation failed: {e}")
        sys.exit(1)

    try:
        pot = make_flowerpot(
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
        )

        try:
            # Export based on format choice
            if args.format in ["step", "all"]:
                export_step(pot, args.filename)
            
            if args.format in ["stl", "all"]:
                export_stl(pot, args.filename)
            
            if args.summary:
                export_parameter_summary(
                    args.filename,
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
                )
                
        except Exception as e:
            logging.error(f"Failed to export flowerpot: {e}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Failed to generate flowerpot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
