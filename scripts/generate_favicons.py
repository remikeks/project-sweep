"""
One-off asset-generation script (not part of the Django app). Rasterizes
static/img/logo.svg's exact geometry into the PNG/ICO favicon set, since
no SVG rasterizer is available in this environment. Re-run if the logo
design ever changes.
"""

import math

from PIL import Image, ImageDraw

GOLD_LIGHT = (228, 195, 116)
GOLD_DARK = (199, 154, 60)
FOREST = (18, 59, 53)
PAPER = (238, 240, 234)

SCALE = 16  # supersample factor; render big, downsample for clean anti-aliasing
SIZE = 64 * SCALE


def cubic_bezier_points(p0, p1, p2, p3, steps=60):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        mt = 1 - t
        x = (mt**3) * p0[0] + 3 * (mt**2) * t * p1[0] + 3 * mt * (t**2) * p2[0] + (t**3) * p3[0]
        y = (mt**3) * p0[1] + 3 * (mt**2) * t * p1[1] + 3 * mt * (t**2) * p2[1] + (t**3) * p3[1]
        pts.append((x * SCALE, y * SCALE))
    return pts


def leaf_polygon():
    # Mirrors the cubic path in static/img/logo.svg exactly:
    # M32,16 C42,16 50,24 50,34 C50,42 44,48 36,48
    #        C36,48 35,38 22,32 C26,22 28,16 32,16 Z
    segments = [
        ((32, 16), (42, 16), (50, 24), (50, 34)),
        ((50, 34), (50, 42), (44, 48), (36, 48)),
        ((36, 48), (36, 48), (35, 38), (22, 32)),
        ((22, 32), (26, 22), (28, 16), (32, 16)),
    ]
    pts = []
    for p0, p1, p2, p3 in segments:
        pts.extend(cubic_bezier_points(p0, p1, p2, p3))
    return pts


def render_mark():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy, r = 32 * SCALE, 32 * SCALE, 30 * SCALE

    # Radial-gradient-ish gold circle: concentric rings from centre outward,
    # lerping GOLD_LIGHT -> GOLD_DARK (approximates the SVG radialGradient).
    steps = 160
    for i in range(steps, 0, -1):
        t = i / steps
        ring_r = int(r * t)
        blend = min(1.0, t * 1.15)
        color = tuple(int(GOLD_LIGHT[c] + (GOLD_DARK[c] - GOLD_LIGHT[c]) * blend) for c in range(3))
        draw.ellipse((cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r), fill=color)

    # Ring outline
    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        outline=FOREST,
        width=max(1, int(1.5 * SCALE)),
    )

    # Leaf glyph
    draw.polygon(leaf_polygon(), fill=FOREST)

    # Vein detail (approximate the stroked bezier as a thick line through sampled points)
    vein_pts = cubic_bezier_points((32, 18), (34, 25), (34, 33), (30, 43), steps=40)
    draw.line(vein_pts, fill=GOLD_LIGHT + (140,), width=max(1, int(1.6 * SCALE)), joint="curve")

    return img


def main():
    master = render_mark()

    sizes = {
        "static/favicon/favicon-16x16.png": 16,
        "static/favicon/favicon-32x32.png": 32,
        "static/favicon/favicon-48x48.png": 48,
        "static/favicon/android-chrome-192x192.png": 192,
        "static/favicon/android-chrome-512x512.png": 512,
    }
    resized = {}
    for path, size in sizes.items():
        im = master.resize((size, size), Image.LANCZOS)
        im.save(path)
        resized[size] = im
        print("wrote", path)

    # Apple touch icon: solid paper background (Apple composites transparent
    # PNGs onto black otherwise, which would swallow the gold ring at a glance)
    apple = Image.new("RGBA", (180, 180), PAPER + (255,))
    apple_mark = master.resize((180, 180), Image.LANCZOS)
    apple.alpha_composite(apple_mark)
    apple.convert("RGB").save("static/favicon/apple-touch-icon.png")
    print("wrote static/favicon/apple-touch-icon.png")

    # Also drop a full-res PNG of the mark for use anywhere the SVG isn't
    # convenient (README, social preview, etc.)
    master.resize((512, 512), Image.LANCZOS).save("static/img/logo.png")
    print("wrote static/img/logo.png")

    # Multi-size .ico
    resized[16].save(
        "static/favicon/favicon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
        append_images=[resized[32], resized[48]],
    )
    print("wrote static/favicon/favicon.ico")


if __name__ == "__main__":
    main()
