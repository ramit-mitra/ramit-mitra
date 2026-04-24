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

# Approximate widths at 64px Arial Black — tuned empirically for brutalist aesthetic
CHAR_WIDTH_64 = {
    " ": 20, ".": 20, "-": 26, ",": 18, "'": 14,
    "I": 25, "J": 28, "L": 36, "1": 30,
    "M": 58, "W": 58,
}
DEFAULT_CHAR_WIDTH_64 = 44


def text_width_64(s: str) -> int:
    """Approximate pixel width of uppercase text at 64px Arial Black."""
    return sum(CHAR_WIDTH_64.get(c.upper(), DEFAULT_CHAR_WIDTH_64) for c in s)


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
        if highlight:
            # Left text with trailing space to separate from highlighted word
            left_with_trailing = left + " "
            left_w = text_width_64(left_with_trailing)
            hi_x = PAD_X + left_w
            hi_w = text_width_64(highlight)
            # Pill sits under the highlighted word
            pill_pad_x = 8
            pill_pad_y_top = 48   # above baseline
            pill_pad_y_bot = 12   # below baseline
            pill_h = pill_pad_y_top + pill_pad_y_bot
            pill_y = y - pill_pad_y_top
            # Draw pill first (under text)
            parts.append(
                f'  <rect x="{hi_x - pill_pad_x}" y="{pill_y}" '
                f'width="{hi_w + 2 * pill_pad_x}" height="{pill_h}" '
                f'fill="{accent}"/>'
            )
            # Left text
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" '
                f'font-family="{xml_escape(FONT_DISPLAY)}" font-weight="900" '
                f'font-size="64" fill="{fg}" '
                f'style="letter-spacing:-2px; text-transform:uppercase;">'
                f'{xml_escape(left)}</text>'
            )
            # Highlighted text (separate element, same styling)
            parts.append(
                f'  <text x="{hi_x}" y="{y}" '
                f'font-family="{xml_escape(FONT_DISPLAY)}" font-weight="900" '
                f'font-size="64" fill="{fg}" '
                f'style="letter-spacing:-2px; text-transform:uppercase;">'
                f'{xml_escape(highlight)}</text>'
            )
        else:
            parts.append(
                f'  <text x="{PAD_X}" y="{y}" '
                f'font-family="{xml_escape(FONT_DISPLAY)}" font-weight="900" '
                f'font-size="64" fill="{fg}" '
                f'style="letter-spacing:-2px; text-transform:uppercase;">'
                f'{xml_escape(left)}</text>'
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
