"""Shared helpers for SVG generators. Standard library only."""

THEMES = {
    "light": {
        "bg": "#ffffff",
        "fg": "#111111",
        "accent": "#5FD7DF",
        "border": "#000000",
        "muted": "#555555",
    },
    "dark": {
        "bg": "#0d1117",
        "fg": "#f0f6fc",
        "accent": "#5FD7DF",
        "border": "#f0f6fc",
        "muted": "#8b949e",
    },
}

FONT_DISPLAY = (
    "'Arial Black', 'Helvetica Neue', Impact, "
    "'Franklin Gothic Heavy', sans-serif"
)
FONT_MONO = "'SF Mono', ui-monospace, Menlo, Consolas, monospace"


def xml_escape(s: str) -> str:
    """Escape text for inclusion in SVG text nodes."""
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
