#!/usr/bin/env python3
"""Build the fiber-dad brand glyph SVGs (drop-in replacements for nous-girl-*.svg).

Single monochrome path, absolute M/L/C/z only (icons generator constraint),
fill-rule evenodd (house silhouette + lightning-bolt negative space).
"""
import math

V = 5487.0615  # generator's expected canvas


def rounded_path(points, radii, fmt=lambda v: f"{v:.3f}".rstrip("0").rstrip(".")):
    """Closed polygon path with cubic-fillet corners (absolute M/L/C only)."""
    n = len(points)
    segs = []
    start = None
    for i in range(n):
        p_prev = points[(i - 1) % n]
        p = points[i]
        p_next = points[(i + 1) % n]
        r = radii[i]
        v1 = (p_prev[0] - p[0], p_prev[1] - p[1])
        v2 = (p_next[0] - p[0], p_next[1] - p[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        r = min(r, l1 / 2, l2 / 2)
        a = (p[0] + v1[0] / l1 * r, p[1] + v1[1] / l1 * r)  # point before corner
        b = (p[0] + v2[0] / l2 * r, p[1] + v2[1] / l2 * r)  # point after corner
        # control points on the straight edges, close to the corner
        c1 = (p[0] - v1[0] / l1 * r * 0.4477, p[1] - v1[1] / l1 * r * 0.4477)
        c2 = (p[0] + v2[0] / l2 * r * 0.4477, p[1] + v2[1] / l2 * r * 0.4477)
        if start is None:
            start = a
            segs.append(f"M {fmt(a[0])} {fmt(a[1])}")
        else:
            segs.append(f"L {fmt(a[0])} {fmt(a[1])}")
        segs.append(f"C {fmt(c1[0])} {fmt(c1[1])} {fmt(c2[0])} {fmt(c2[1])} {fmt(b[0])} {fmt(b[1])}")
    segs.append("Z")
    return " ".join(segs)


# House silhouette: foundation corners, eaves, peak. Canvas 5487 wide.
house = [
    (1143, 3900),   # bottom-left foundation
    (1143, 2385),   # left eave
    (2743, 1043),   # peak
    (4343, 2385),   # right eave
    (4343, 3900),   # bottom-right foundation
]
# sharper fillets at foundation, softer at peak/eaves
house_radii = [100, 200, 280, 200, 100]

# Lightning bolt (negative space) inside the body: Lucide 'zap' polygon
# (M13 2 L3 14 H12 L11 22 L21 10 H12 L13 2 Z on a 24 grid) mapped to a box
# centered on the house body, thick diagonals so it survives 32px.
bx, by, bw, bh = 1940, 2420, 1600, 1300
zap = [(13, 2), (3, 14), (12, 14), (11, 22), (21, 10), (12, 10)]
bolt = [(bx + u / 24 * bw, by + v / 24 * bh) for u, v in zap]
bolt_radii = [55, 55, 55, 130, 55, 55]

d = rounded_path(house, house_radii) if False else None
path_body = f"M {house[0][0]} {house[0][1]}"  # placeholder replaced below

def poly_path(points, radii):
    n = len(points)
    segs = []
    start = None
    for i in range(n):
        p_prev = points[(i - 1) % n]
        p = points[i]
        p_next = points[(i + 1) % n]
        r = radii[i]
        v1 = (p_prev[0] - p[0], p_prev[1] - p[1])
        v2 = (p_next[0] - p[0], p_next[1] - p[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        r = min(r, l1 / 2.2, l2 / 2.2)
        a = (p[0] + v1[0] / l1 * r, p[1] + v1[1] / l1 * r)
        b = (p[0] + v2[0] / l2 * r, p[1] + v2[1] / l2 * r)
        c1 = (p[0] - v1[0] / l1 * r * 0.4477, p[1] - v1[1] / l1 * r * 0.4477)
        c2 = (p[0] + v2[0] / l2 * r * 0.4477, p[1] + v2[1] / l2 * r * 0.4477)
        if start is None:
            start = a
            segs.append(f"M {a[0]:.3f} {a[1]:.3f}")
        else:
            segs.append(f"L {a[0]:.3f} {a[1]:.3f}")
        segs.append(f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {b[0]:.3f} {b[1]:.3f}")
    segs.append("Z")
    return " ".join(segs)

d = poly_path(house, house_radii) + " " + poly_path(bolt, bolt_radii)

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="5487.0615" height="5487.0615" '
    'viewBox="0 0 5487.0615 5487.0615">\n'
    '  <path fill="{fill}" fill-rule="evenodd" d="{d}"/>\n'
    "</svg>\n"
)

for color in ("black", "white"):
    fill = "#000000" if color == "black" else "#ffffff"
    out = f"assets/nous-girl-{color}.svg"
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg.replace("{fill}", fill).replace("{d}", d))
    print(f"wrote {out} ({len(d)} chars of path)")