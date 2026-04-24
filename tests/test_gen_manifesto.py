"""Unit tests for the manifesto SVG generator and shared helpers."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

# Make scripts/ importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from svg_common import THEMES, xml_escape  # noqa: E402


class TestSvgCommon(unittest.TestCase):
    def test_light_theme_has_expected_keys(self):
        self.assertIn("bg", THEMES["light"])
        self.assertIn("fg", THEMES["light"])
        self.assertIn("accent", THEMES["light"])
        self.assertIn("border", THEMES["light"])

    def test_dark_theme_uses_github_dark_bg(self):
        self.assertEqual(THEMES["dark"]["bg"], "#0d1117")

    def test_accent_is_cap_cyan(self):
        # Same cyan across both themes
        self.assertEqual(THEMES["light"]["accent"], "#5FD7DF")
        self.assertEqual(THEMES["dark"]["accent"], "#5FD7DF")

    def test_xml_escape_ampersand(self):
        self.assertEqual(xml_escape("rock & roll"), "rock &amp; roll")

    def test_xml_escape_angle_brackets(self):
        self.assertEqual(xml_escape("<script>"), "&lt;script&gt;")

    def test_xml_escape_quotes(self):
        self.assertEqual(xml_escape('he said "hi"'), 'he said &quot;hi&quot;')


import subprocess


def run_manifesto(theme: str) -> str:
    """Invoke the generator as a subprocess and capture stdout."""
    result = subprocess.run(
        ["python3", str(REPO_ROOT / "scripts" / "gen_manifesto.py"), "--theme", theme],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


class TestManifestoGenerator(unittest.TestCase):
    def test_light_output_is_well_formed_svg(self):
        svg = run_manifesto("light")
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))

    def test_dark_output_is_well_formed_svg(self):
        svg = run_manifesto("dark")
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))

    def test_light_background_is_white(self):
        svg = run_manifesto("light")
        self.assertIn('fill="#ffffff"', svg)

    def test_dark_background_is_github_dark(self):
        svg = run_manifesto("dark")
        self.assertIn('fill="#0d1117"', svg)

    def test_accent_highlight_present_in_both_themes(self):
        # The highlight pill behind "TOOLS" uses the cap-cyan
        for theme in ("light", "dark"):
            svg = run_manifesto(theme)
            self.assertIn("#5FD7DF", svg, f"missing accent in {theme} theme")

    def test_contains_all_manifesto_lines(self):
        svg = run_manifesto("light")
        for phrase in (
            "I BUILD",
            "MY OWN",
            "TOOLS.",
            "MOSTLY IN THE OPEN.",
            "USUALLY BECAUSE THE",
            "OFF-THE-SHELF ONE",
            "IRRITATED ME.",
        ):
            self.assertIn(phrase, svg, f"missing line: {phrase!r}")

    def test_invalid_theme_exits_nonzero(self):
        result = subprocess.run(
            ["python3", str(REPO_ROOT / "scripts" / "gen_manifesto.py"), "--theme", "purple"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()
