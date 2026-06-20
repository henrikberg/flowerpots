import cadquery as cq
import argparse
import math
from pathlib import Path

def make_flowerpot(
    outer_diameter: float = 120.0,
    height: float = 100.0,
    wall_thickness: float = 3.0,
    base_thickness: float = 4.0,
    drain_diameter: float = 8.0,
    number_of_drains: int = 1,
    taper_angle: float = 5.0,
    rim_thickness: float = 2.0,
    rim_height: float = 5.0,
    foot_height: float = 3.0,
    foot_ring_count: int = 2,
) -> cq.Workplane:
    """
    Generate a parametric flowerpot as a STEP file.

    Parameters
    ----------
    outer_diameter
        Outer diameter of the pot at the top rim (mm).
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
    taper_angle
        Draft angle of the outer wall in degrees (positive narrows toward the bottom).
    rim_thickness
        Extra thickness added to the top rim (mm).
    rim_height
        Height of the reinforced rim (mm).
    foot_height
        Height of the bottom ventilation feet (mm). Set to 0 to omit.
    foot_ring_count
        Number of concentric rings on the bottom for ventilation.
    """
    radius = outer_diameter / 2.0
    taper = math.tan(math.radians(taper_angle))

    # Compute radii
    bottom_radius = radius - height * taper
    inner_radius_top = radius - wall_thickness
    inner_radius_bottom = radius - height * taper - wall_thickness
    if inner_radius_bottom <= 0:
        raise ValueError("Wall thickness too large for the chosen diameter/height/taper.")

    # Main pot body + rim profile revolved around Z axis
    body_profile = [
        (bottom_radius, 0),
        (radius, height),
    ]
    if rim_thickness > 0 and rim_height > 0:
        top_outer = radius + rim_thickness
        bottom_outer = max(radius + rim_thickness - rim_height, radius)
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

    pot = (
        cq.Workplane("XZ")
        .polyline(body_profile)
        .close()
        .revolve()
    )

    # Bottom ventilation feet / rings
    if foot_height > 0 and foot_ring_count > 0:
        foot_ring_width = bottom_radius / foot_ring_count
        if foot_ring_width <= foot_height * 2.0:
            raise ValueError("Foot height too big for the number of foot rings.")
        #innermost_outer_r = bottom_radius - (foot_ring_count - 1) * foot_ring_width
        #if innermost_outer_r - foot_ring_width < 0:
        #    raise ValueError("Foot rings too wide for the pot bottom.")

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
            slit_width = 0.0
            slit_length = bottom_radius + flare + 2

            half_top = slit_width / 2.0
            half_bottom = half_top + flare
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
                angle = 2 * math.pi * i / number_of_drains
                slit_rotated = slit.rotate(
                    (0, 0, 0), (0, 0, 1), math.degrees(angle)
                )
                feet = feet.cut(slit_rotated)

        pot = pot.union(feet)

    # Drainage holes
    if number_of_drains > 0 and drain_diameter > 0:
        hole_radius = drain_diameter / 2.0
        if number_of_drains == 1:
            holes = (
                cq.Workplane("XY")
                .circle(hole_radius)
                .extrude(height)
            )
        else:
            # arrange holes in a circle around the center of the base
            drain_circle_radius = min(
                drain_diameter * 2.0,
                inner_radius_bottom - hole_radius - 1.0,
            )
            min_circle_radius = hole_radius / math.sin(math.pi / number_of_drains)
            if drain_circle_radius < min_circle_radius:
                raise ValueError(
                    "Drain diameter/number of drains too large for the pot base."
                )
            points = [
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
        pot = pot.cut(holes)

    return pot


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a parametric flowerpot STEP file.")
    parser.add_argument("--diameter", type=float, default=120.0, help="Outer top diameter in mm.")
    parser.add_argument("--height", type=float, default=100.0, help="Total height in mm.")
    parser.add_argument("--wall", type=float, default=3.0, help="Wall thickness in mm.")
    parser.add_argument("--base", type=float, default=4.0, help="Base thickness in mm.")
    parser.add_argument("--drain-diameter", type=float, default=8.0, help="Drainage hole diameter in mm (0 to disable).")
    parser.add_argument("--number-of-drains", type=int, default=4, help="Number of drainage holes.")
    parser.add_argument("--taper", type=float, default=5.0, help="Wall taper angle in degrees.")
    parser.add_argument("--foot-height", type=float, default=3.0, help="Height of bottom ventilation feet in mm (0 to disable).")
    parser.add_argument("--foot-ring-count", type=int, default=2, help="Number of concentric bottom ventilation rings.")
    parser.add_argument("--rim-thickness", type=float, default=2.0, help="Extra rim thickness in mm.")
    parser.add_argument("--rim-height", type=float, default=5.0, help="Rim height in mm.")
    parser.add_argument("--output", type=Path, default=Path("flowerpots.step"), help="Output STEP file path.")

    args = parser.parse_args()

    pot = make_flowerpot(
        outer_diameter=args.diameter,
        height=args.height,
        wall_thickness=args.wall,
        base_thickness=args.base,
        drain_diameter=args.drain_diameter,
        number_of_drains=args.number_of_drains,
        taper_angle=args.taper,
        rim_thickness=args.rim_thickness,
        rim_height=args.rim_height,
        foot_height=args.foot_height,
        foot_ring_count=args.foot_ring_count,
    )

    cq.exporters.export(pot, str(args.output))
    print(f"Exported flowerpot to {args.output}")


if __name__ == "__main__":
    main()
