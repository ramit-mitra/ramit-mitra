#!/usr/bin/env python3
"""Generate the static manifesto SVG for the profile README.

Usage:
    python3 scripts/gen_manifesto.py --theme light > assets/manifesto-light.svg
    python3 scripts/gen_manifesto.py --theme dark  > assets/manifesto-dark.svg

Rerun manually whenever the manifesto copy changes.
"""
import argparse
import sys

from svg_common import THEMES, FONT_DISPLAY, FONT_MONO, xml_escape

# Manifesto lines. Edit here, rerun the script, commit.
LINES = [
    ("I BUILD",             None),
    ("MY OWN",              "TOOLS."),   # second cell gets the highlight pill
    ("MOSTLY IN THE OPEN.", None),
    ("USUALLY BECAUSE THE", None),
    ("OFF-THE-SHELF ONE",   None),
    ("IRRITATED ME.",       None),
]

BYLINE = "— RAMIT MITRA  ·  FULL STACK + OPEN SOURCE  ·  INDIA  ·  SINCE 2016"

# Layout (px, aligned with spec viewbox 900x520)
VIEW_W = 900
VIEW_H = 520
PAD_X = 32
LINE_HEIGHT = 68
TOP_Y = 88
BYLINE_Y = 480


def render(theme_name: str) -> str:
    theme = THEMES[theme_name]
    fg = theme["fg"]
    bg = theme["bg"]
    accent = theme["accent"]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}">',
        f'  <rect width="{VIEW_W}" height="{VIEW_H}" fill="{bg}"/>',
    ]

    # Render each manifesto line
    for idx, (left, highlight) in enumerate(LINES):
        y = TOP_Y + idx * LINE_HEIGHT
        # Highlight pill behind the highlighted word (drawn first so text sits on top)
        if highlight:
            # Very rough width estimate for the pill; Arial Black uppercase ~ 0.62em
            pill_w = int(len(highlight) * 38)
            # Position pill after the left word with a space
            left_w = int(len(left) * 38)
            pill_x = PAD_X + left_w + 20
            pill_y = y - 54
            parts.append(
                f'  <rect x="{pill_x}" y="{pill_y}" width="{pill_w}" height="64" '
                f'fill="{accent}"/>'
            )

        parts.append(
            f'  <text x="{PAD_X}" y="{y}" '
            f'font-family="{xml_escape(FONT_DISPLAY)}" font-weight="900" '
            f'font-size="64" fill="{fg}" '
            f'style="letter-spacing:-2px; text-transform:uppercase;">'
            f'{xml_escape(left)}'
            + (f' <tspan fill="{fg}">{xml_escape(highlight)}</tspan>' if highlight else '')
            + '</text>'
        )

    # Byline
    parts.append(
        f'  <text x="{PAD_X}" y="{BYLINE_Y}" '
        f'font-family="{xml_escape(FONT_MONO)}" font-size="14" '
        f'fill="{fg}" style="letter-spacing:1.5px;">{xml_escape(BYLINE)}</text>'
    )

    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate the manifesto SVG.")
    parser.add_argument("--theme", choices=list(THEMES.keys()), required=True)
    args = parser.parse_args()
    sys.stdout.write(render(args.theme))


if __name__ == "__main__":
    main()
