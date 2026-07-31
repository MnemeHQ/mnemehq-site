#!/usr/bin/env python3
"""Check video links, embeds, and VideoObject scope across the static site."""

from __future__ import annotations

import json
import re
from pathlib import Path


SITE_ROOT = Path(__file__).resolve().parent.parent / "site"
JSON_LD_RE = re.compile(
    r'<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
    re.IGNORECASE | re.DOTALL,
)
SMART_ATTRIBUTE_RE = re.compile(r'\b(?:href|src|style|class|id|target|rel)=”')


def has_video_object(value: object) -> bool:
    if isinstance(value, dict):
        return value.get("@type") == "VideoObject" or any(
            has_video_object(child) for child in value.values()
        )
    if isinstance(value, list):
        return any(has_video_object(child) for child in value)
    return False


def check_page(path: Path) -> list[str]:
    errors: list[str] = []
    html = path.read_text(encoding="utf-8")
    relative = path.relative_to(SITE_ROOT).as_posix()

    if SMART_ATTRIBUTE_RE.search(html):
        errors.append(f"{relative}: smart quote used as an HTML attribute delimiter")

    contains_video_object = False
    for match in JSON_LD_RE.finditer(html):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError as exc:
            errors.append(f"{relative}: invalid JSON-LD ({exc})")
            continue
        contains_video_object |= has_video_object(data)

    if contains_video_object:
        is_demo_page = relative == "demo/index.html" or relative.startswith("demo/")
        has_visible_video = (
            "youtube-nocookie.com/embed/" in html
            or "youtube.com/embed/" in html
            or "yt-facade" in html
        )
        if not is_demo_page:
            errors.append(f"{relative}: VideoObject is only allowed on dedicated demo pages")
        elif not has_visible_video:
            errors.append(f"{relative}: VideoObject has no visible video embed or facade")

    return errors


def main() -> int:
    errors: list[str] = []
    for path in sorted(SITE_ROOT.rglob("*.html")):
        errors.extend(check_page(path))
    if errors:
        print("\n".join(errors))
        return 1
    print("video markup check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
