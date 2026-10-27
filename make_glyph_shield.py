#!/usr/bin/env python3
"""Fiber Dad shield icon glyph preview — site logo mark (cyan shield + padlock).

Monochrome positive-space path (icons generator constraint: M/L/C/z only,
evenodd, 5487.0615 canvas). Ink = shield ring + solid padlock; the interior
reads as the squircle background color.
"""
import math

C = 5487.0615
CX = 2743.5


def fillet_poly(points, radii):
    """Closed polygon -> path with cubic corner fillets."""
    n = len(points)
    segs = []
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
        if not segs:
            segs.append(f"M {a[0]:.3f} {a[1]:.3f}")
        else:
            segs.append(f"L {a[0]:.3f} {a[1]:.3f}")
        segs.append(f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {b[0]:.3f} {b[1]:.3f}")
    segs.append("Z")
    return " ".join(segs)


def shield_path(top, left, right, tip, corner, low_frac):
    """Heater-shield outline: flat top with rounded shoulders, straight sides
    to `low_frac`, then an angle to the bottom tip."""
    mid = (left + right) / 2
    drop = tip - top
    pts = [
        (left, top),
        (right, top),
        (right, top + drop * (low_frac * 0.62)),
        (right - (right - mid) * (1 - low_frac) * 1.6, top + drop * low_frac),
        (mid, tip),
        (left + (mid - left) * (1 - low_frac) * 1.6, top + drop * low_frac),
        (left, top + drop * (low_frac * 0.62)),
    ]
    radii = [corner, corner, 40, 90, 140, 90, 40]
    return fillet_poly(pts, radii)


# Monochrome: SOLID shield, padlock (body + shackle band) knocked out.
# Ink = shield interior crossing 1; inside the body/shackle band crossings
# = 2 -> evenodd leaves the background showing (the padlock silhouette).
outer = shield_path(1150, 1500, 3987, 4250, 150, 0.70)
inner = ""  # no ring — solid fill

def scale_path_top(top, left, right, tip, corner, s, cy):
    def sc(y): return cy + (y - cy) * s
    def scx(x): return CX + (x - CX) * s
    return shield_path(sc(top), scx(left), scx(right), sc(tip), corner, 0.70)

def bezier_half_annulus(cx, cy, r_outer, r_inner, t0_deg=180, t1_deg=360, steps=4):
    """Upper-half annulus centered (cx, cy) as cubic segments (angles CCW,
    180..360 = left to right over the top)."""
    k = 4.0 / 3.0 * math.tan(math.radians(45.0 / steps))
    pts = []
    for r in (r_outer, r_inner):
        for i in range(steps + 1):
            a = math.radians(t0_deg + (t1_deg - t0_deg) * i / steps)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    # outer arc left->top->right, then inner arc right->top->left
    path = [f"M {pts[0][0]:.3f} {pts[0][1]:.3f}"]
    for i in range(1, steps + 1):
        p0 = pts[i - 1]
        p1 = pts[i]
        # cubic control points along the arc directions
        a0 = math.radians(t0_deg + (t1_deg - t0_deg) * (i - 1) / steps)
        a1 = math.radians(t0_deg + (t1_deg - t0_deg) * i / steps)
        c1 = (p0[0] - r_outer * k * math.sin(a0), p0[1] + r_outer * k * math.cos(a0))
        c2 = (p1[0] + r_outer * k * math.sin(a1), p1[1] - r_outer * k * math.cos(a1))
        path.append(f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p1[0]:.3f} {p1[1]:.3f}")
    inner_start = steps + 1
    path.append(f"L {pts[inner_start][0]:.3f} {pts[inner_start][1]:.3f}")
    for i in range(1, steps + 1):
        p0 = pts[inner_start + i - 1]
        p1 = pts[inner_start + i]
        a0 = math.radians(t1_deg - (t1_deg - t0_deg) * (i - 1) / steps)
        a1 = math.radians(t1_deg - (t1_deg - t0_deg) * i / steps)
        c1 = (p0[0] - r_inner * k * math.sin(a0), p0[1] + r_inner * k * math.cos(a0))
        c2 = (p1[0] + r_inner * k * math.sin(a1), p1[1] - r_inner * k * math.cos(a1))
        path.append(f"C {c1[0]:.3f} {c1[1]:.3f} {c2[0]:.3f} {c2[1]:.3f} {p1[0]:.3f} {p1[1]:.3f}")
    path.append("Z")
    return " ".join(str(p) for p in path)


# Padlock: body + true half-annulus shackle, feet landing inside the body
bx, by, bw, bh = 2743.5 - 480, 2570, 960, 680   # body rounded rect
shackle_r = 300           # outer radius
shackle_t = 128           # wall thickness
shackle_cy = by - shackle_r + 90   # arc center sits below the top edge
shackle = bezier_half_annulus(bx + bw / 2, shackle_cy, shackle_r, shackle_r - shackle_t, 180, 360, 6)

body = fillet_poly([(bx, by), (bx + bw, by), (bx + bw, by + bh), (bx, by + bh)], [120, 120, 170, 170])

d = outer + " " + inner + " " + shackle + " " + body

svg = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="5487.0615" height="5487.0615" '
    'viewBox="0 0 5487.0615 5487.0615">\n'
    '  <path fill="{fill}" fill-rule="evenodd" d="'
    + outer
    + " "
    + inner
    + " "
    + shackle
    + " "
    + body
    + '"/>\n</svg>\n'
)

# Preview both appearances
import resvg_py
import re
import xml.etree.ElementTree as ET

for color, fill, bgname in (("dark", "#ffffff", "squircle-dark.svg"), ("light", "#000000", "squircle-light.svg")):
    shield = shield_path(1150, 1500, 3987, 4250, 150, 0.70)
    padlock = body + " " + shackle
    path_el = f'<path fill="{fill}" fill-rule="evenodd" d="{shield} {padlock}"/>'
    bg = open(f"assets/backgrounds/{bgname}").read()
    inner_bg = "".join(ET.tostring(c, encoding="unicode") for c in ET.fromstring(bg))
    rect = re.search(r"<rect[^>]*/>", bg).group(0)
    master = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024">'
        f'<defs><clipPath id="s">{rect}</clipPath></defs>{inner_bg}'
        f'<g clip-path="url(#s)"><svg x="72.149433" y="104.703674" width="872.767801" height="872.767801" '
        f'viewBox="0 0 5487.0615 5487.0615" preserveAspectRatio="xMidYMax meet">{path_el}</svg></g></svg>'
    )
    for size, name in ((512, "512"), (32, "32")):
        data = resvg_py.svg_to_bytes(svg_string=master, width=size, height=size)
        open(f"/tmp/shield_{color}_{name}.png", "wb").write(bytes(data))
print("previews written")