#!/usr/bin/env python3
"""WCAG 2.2 contrast ratio between a text color and a background color.

Usage: contrast.py <foreground> <background> [<foreground> <background> ...]
Colors: #rgb, #rrggbb, #rrggbbaa, rgb(r, g, b), rgba(r, g, b, a) or a basic CSS name.
Semi-transparent foregrounds are blended over the background.
"""
import re
import sys

NAMES = {
    "black": "#000000", "white": "#ffffff", "red": "#ff0000", "green": "#008000", "blue": "#0000ff",
    "gray": "#808080", "grey": "#808080", "silver": "#c0c0c0", "yellow": "#ffff00", "orange": "#ffa500",
    "purple": "#800080", "navy": "#000080", "teal": "#008080", "maroon": "#800000", "olive": "#808000",
    "lime": "#00ff00", "aqua": "#00ffff", "fuchsia": "#ff00ff", "lightgray": "#d3d3d3", "darkgray": "#a9a9a9",
}


def parse(c):
    c = NAMES.get(c.strip().lower(), c.strip())
    m = re.fullmatch(r"#([0-9a-fA-F]{3,8})", c)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h)
        if len(h) not in (6, 8):
            raise ValueError(c)
        rgb = [int(h[i:i + 2], 16) for i in (0, 2, 4)]
        alpha = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return rgb, alpha
    m = re.fullmatch(r"rgba?\(\s*([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+)(?:\s*[,/]\s*([\d.]+%?))?\s*\)", c)
    if m:
        rgb = [float(m.group(i)) for i in (1, 2, 3)]
        a = m.group(4)
        alpha = 1.0 if a is None else (float(a[:-1]) / 100 if a.endswith("%") else float(a))
        return rgb, alpha
    raise ValueError(f"Unrecognised color: {c}")


def luminance(rgb):
    def ch(v):
        v = v / 255
        return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(fg, bg):
    (frgb, fa), (brgb, _) = parse(fg), parse(bg)
    blended = [fa * f + (1 - fa) * b for f, b in zip(frgb, brgb)]
    l1, l2 = sorted((luminance(blended), luminance(brgb)), reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def verdict(r):
    def ok(x):
        return "pass" if r >= x else "FAIL"
    return (f"AA normal text {ok(4.5)}, AA large text {ok(3)}, "
            f"AAA normal {ok(7)}, AAA large {ok(4.5)}, UI components {ok(3)}")


def main():
    args = sys.argv[1:]
    if not args or len(args) % 2:
        sys.exit(__doc__)
    failed = False
    for fg, bg in zip(args[::2], args[1::2]):
        try:
            r = ratio(fg, bg)
        except ValueError as e:
            sys.exit(str(e))
        failed |= r < 4.5
        print(f"{fg} on {bg}: {r:.2f}:1  {verdict(r)}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
