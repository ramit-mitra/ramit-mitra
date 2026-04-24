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


if __name__ == "__main__":
    unittest.main()
