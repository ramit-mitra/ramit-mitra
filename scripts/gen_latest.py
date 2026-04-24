#!/usr/bin/env python3
"""Generate the LATEST-commit SVG for the profile README.

Invoked by the daily GitHub Action. Can also be run locally:
    python3 scripts/gen_latest.py --theme light > assets/latest-light.svg
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from urllib.request import Request, urlopen

from svg_common import THEMES, FONT_DISPLAY, FONT_MONO, xml_escape

USER = "ramit-mitra"
PROFILE_REPO = f"{USER}/{USER}"
EVENTS_URL = f"https://api.github.com/users/{USER}/events/public"
MAX_MSG_LEN = 90
PLACEHOLDER = "— quietly working —"

VIEW_W = 900
VIEW_H = 200


def fetch_events():
    """Fetch public events for USER. Uses GITHUB_TOKEN if available."""
    req = Request(EVENTS_URL, headers={"Accept": "application/vnd.github+json"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urlopen(req, timeout=30) as resp:
        return json.load(resp)


def pick_event(events, user):
    """Return the first event that is a real push by USER, else None."""
    for ev in events:
        if ev.get("type") != "PushEvent":
            continue
        actor = (ev.get("actor") or {}).get("login", "")
        if actor != user or actor.endswith("[bot]"):
            continue
        repo = (ev.get("repo") or {}).get("name", "")
        if repo == PROFILE_REPO:
            # Skip our own daily-refresh commits
            continue
        commits = (ev.get("payload") or {}).get("commits") or []
        if not commits:
            continue
        return ev
    return None


def sanitize_message(msg: str) -> str:
    """First line, trimmed, truncated to MAX_MSG_LEN with ellipsis."""
    first = msg.splitlines()[0].rstrip() if msg else ""
    if len(first) > MAX_MSG_LEN:
        return first[: MAX_MSG_LEN - 1] + "…"
    return first


def relative_time(iso_ts: str) -> str:
    """Return a human 'X ago' string from an ISO-8601 timestamp."""
    try:
        t = datetime.fromisoformat(iso_ts.replace("Z", "+00:00"))
    except ValueError:
        return ""
    now = datetime.now(timezone.utc)
    delta = now - t
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return "just now"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    days = hours // 24
    return f"{days} day{'s' if days != 1 else ''} ago"


def render(theme_name: str, repo: str, message: str, when_text: str) -> str:
    theme = THEMES[theme_name]
    fg = theme["fg"]
    bg = theme["bg"]
    accent = theme["accent"]
    border = theme["border"]

    # On-cyan content is always black — locked design decision
    on_accent = "#111111"

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {VIEW_W} {VIEW_H}" width="{VIEW_W}" height="{VIEW_H}">',
        f'  <rect width="{VIEW_W}" height="{VIEW_H}" fill="{bg}"/>',
        # Main cyan panel with 3px border
        f'  <rect x="4" y="4" width="{VIEW_W - 8}" height="{VIEW_H - 8}" '
        f'fill="{accent}" stroke="{border}" stroke-width="6"/>',
        # "LATEST COMMIT" label
        f'  <text x="30" y="36" font-family="{xml_escape(FONT_DISPLAY)}" '
        f'font-weight="900" font-size="12" fill="{on_accent}" '
        f'style="letter-spacing:2.5px; text-transform:uppercase;">LATEST COMMIT</text>',
        # repo path
        f'  <text x="30" y="64" font-family="{xml_escape(FONT_MONO)}" '
        f'font-weight="700" font-size="14" fill="{on_accent}">{xml_escape(repo)}</text>',
        # message
        f'  <text x="30" y="108" font-family="{xml_escape(FONT_DISPLAY)}" '
        f'font-weight="900" font-size="26" fill="{on_accent}" '
        f'style="letter-spacing:-0.5px; text-transform:uppercase;">'
        f'{xml_escape(message)}</text>',
        # when
        f'  <text x="30" y="{VIEW_H - 26}" font-family="{xml_escape(FONT_MONO)}" '
        f'font-size="11" fill="{on_accent}" opacity="0.7">{xml_escape(when_text)}</text>',
        "</svg>",
    ]
    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Generate the LATEST-commit SVG.")
    parser.add_argument("--theme", choices=list(THEMES.keys()), required=True)
    args = parser.parse_args()

    repo, message, when_text = "", PLACEHOLDER, ""
    try:
        events = fetch_events()
        chosen = pick_event(events, USER)
        if chosen:
            repo = chosen["repo"]["name"]
            commits = chosen["payload"]["commits"]
            message = sanitize_message(commits[-1]["message"])
            when_text = relative_time(chosen["created_at"])
    except Exception as e:
        # Fall back to placeholder on any API/network failure
        print(f"warning: falling back to placeholder ({e})", file=sys.stderr)

    sys.stdout.write(render(args.theme, repo, message, when_text))


if __name__ == "__main__":
    main()
