"""Unit tests for the LATEST-commit SVG generator."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from gen_latest import (  # noqa: E402
    pick_event,
    sanitize_message,
    render,
    PLACEHOLDER,
)


def push_event(repo, msg="commit message", actor="ramit-mitra", head="abc123"):
    # Kept `msg` as a kwarg so existing call sites don't break,
    # but `msg` is no longer embedded in the payload — commit message
    # is fetched separately via fetch_commit_message(repo, head).
    return {
        "type": "PushEvent",
        "actor": {"login": actor},
        "repo": {"name": repo},
        "created_at": "2026-04-24T12:00:00Z",
        "payload": {"head": head},
    }


class TestPickEvent(unittest.TestCase):
    def test_picks_first_matching_push(self):
        events = [
            {"type": "WatchEvent", "actor": {"login": "ramit-mitra"}, "repo": {"name": "a/b"}},
            push_event("ramit-mitra/ramit", "real commit"),
        ]
        chosen = pick_event(events, "ramit-mitra")
        self.assertEqual(chosen["repo"]["name"], "ramit-mitra/ramit")

    def test_skips_bot_actors(self):
        events = [
            push_event("ramit-mitra/x", actor="dependabot[bot]"),
            push_event("ramit-mitra/ramit", actor="ramit-mitra"),
        ]
        chosen = pick_event(events, "ramit-mitra")
        self.assertEqual(chosen["repo"]["name"], "ramit-mitra/ramit")

    def test_skips_self_referential_profile_repo(self):
        # Daily-refresh commit on the profile repo itself must not loop back
        events = [
            push_event("ramit-mitra/ramit-mitra", "chore(profile): refresh LATEST commit SVG"),
            push_event("ramit-mitra/arya", "real code"),
        ]
        chosen = pick_event(events, "ramit-mitra")
        self.assertEqual(chosen["repo"]["name"], "ramit-mitra/arya")

    def test_returns_none_when_no_match(self):
        events = [
            push_event("ramit-mitra/x", "x", actor="github-actions[bot]"),
        ]
        self.assertIsNone(pick_event(events, "ramit-mitra"))

    def test_returns_none_on_empty_list(self):
        self.assertIsNone(pick_event([], "ramit-mitra"))

    def test_returns_none_if_no_head_in_payload(self):
        # Malformed PushEvent without head SHA
        events = [{
            "type": "PushEvent",
            "actor": {"login": "ramit-mitra"},
            "repo": {"name": "ramit-mitra/arya"},
            "created_at": "2026-04-24T12:00:00Z",
            "payload": {},
        }]
        self.assertIsNone(pick_event(events, "ramit-mitra"))


class TestSanitizeMessage(unittest.TestCase):
    def test_first_line_only(self):
        self.assertEqual(sanitize_message("hello\nworld\nmore"), "hello")

    def test_truncates_long(self):
        msg = "x" * 200
        out = sanitize_message(msg)
        self.assertLessEqual(len(out), 90)
        self.assertTrue(out.endswith("…"))

    def test_preserves_short(self):
        self.assertEqual(sanitize_message("short commit"), "short commit")

    def test_strips_trailing_whitespace(self):
        self.assertEqual(sanitize_message("msg   \n"), "msg")


class TestRender(unittest.TestCase):
    def test_valid_svg_with_repo_and_message(self):
        svg = render(
            theme_name="light",
            repo="ramit-mitra/ramit",
            message="ADD STREAMING PARSER",
            when_text="2 hours ago",
        )
        root = ET.fromstring(svg)
        self.assertTrue(root.tag.endswith("svg"))
        self.assertIn("ramit-mitra/ramit", svg)
        self.assertIn("ADD STREAMING PARSER", svg)
        self.assertIn("2 hours ago", svg)

    def test_accent_used_as_panel_fill(self):
        svg = render("light", "a/b", "hi", "now")
        self.assertIn("#5FD7DF", svg)

    def test_dark_theme_uses_dark_bg(self):
        svg = render("dark", "a/b", "hi", "now")
        self.assertIn("#0d1117", svg)

    def test_placeholder_when_no_repo(self):
        svg = render("light", repo="", message=PLACEHOLDER, when_text="")
        self.assertIn(PLACEHOLDER, svg)

    def test_escapes_unsafe_chars_in_message(self):
        svg = render("light", "a/b", "<script>bad</script>", "now")
        self.assertNotIn("<script>", svg)
        self.assertIn("&lt;script&gt;", svg)


if __name__ == "__main__":
    unittest.main()
