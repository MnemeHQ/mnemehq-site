#!/usr/bin/env python3
"""Maintain and validate Mneme HQ Open Graph metadata.

This script no longer creates per-page OG HTML templates. The image renderer is
fully data-driven (scripts/generate_og_images.py); this helper owns metadata and
coverage checks only.

Usage:
    python scripts/ensure_og_coverage.py --check
    python scripts/ensure_og_coverage.py --write
"""

from __future__ import annotations

import argparse
import html
import re
import struct
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
BASE_URL = "https://mnemehq.com"
EXPECTED_WIDTH = 1200
EXPECTED_HEIGHT = 630


def public_html_pages() -> list[Path]:
    pages: list[Path] = []
    for page in sorted(SITE_DIR.rglob("*.html")):
        rel = page.relative_to(SITE_DIR)
        if page.name.startswith("og-") or "assets" in rel.parts or page.name == "404.html":
            continue
        pages.append(page)
    return pages


def page_path(page: Path) -> str:
    rel = page.relative_to(SITE_DIR)
    if rel == Path("index.html"):
        return "/"
    if rel.name == "index.html":
        return "/" + rel.parent.as_posix().strip("/") + "/"
    return "/" + rel.as_posix().lstrip("/")


def default_image_url(page: Path) -> str:
    path = page_path(page)
    if path == "/":
        return f"{BASE_URL}/og-home-v2.png"
    if page.name == "index.html":
        return f"{BASE_URL}{path}og.png"
    return f"{BASE_URL}{path.rsplit('/', 1)[0]}/og.png"


def find_meta(text: str, key: str) -> str:
    key_re = re.escape(key)
    tag_re = re.compile(
        rf"<meta\b(?=[^>]*\b(?:property|name)=[\"']{key_re}[\"'])[^>]*>",
        re.I,
    )
    match = tag_re.search(text)
    if not match:
        return ""
    content = re.search(r"\bcontent=[\"']([^\"']*)[\"']", match.group(0), re.I)
    return html.unescape(content.group(1)).strip() if content else ""


def find_title(text: str) -> str:
    value = find_meta(text, "og:title")
    if not value:
        match = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
        value = re.sub(r"<[^>]+>", " ", match.group(1)) if match else "Mneme HQ"
    value = html.unescape(value)
    value = re.sub(r"\s*[|—-]\s*Mneme HQ\s*$", "", value, flags=re.I)
    return " ".join(value.split()).strip() or "Mneme HQ"


def upsert_meta(text: str, attr: str, key: str, value: str) -> str:
    key_re = re.escape(key)
    tag_re = re.compile(
        rf"<meta\b(?=[^>]*\b(?:property|name)=[\"']{key_re}[\"'])[^>]*>",
        re.I,
    )
    escaped = html.escape(value, quote=True)
    replacement = f'<meta {attr}="{key}" content="{escaped}" />'
    if tag_re.search(text):
        return tag_re.sub(replacement, text, count=1)
    head_end = re.search(r"</head\s*>", text, re.I)
    if not head_end:
        raise ValueError("missing </head>")
    return text[: head_end.start()] + "  " + replacement + "\n" + text[head_end.start() :]


def image_file_from_url(value: str) -> Path | None:
    if not value:
        return None
    parsed = urlparse(value)
    if parsed.netloc and parsed.netloc not in {"mnemehq.com", "www.mnemehq.com"}:
        return None
    path = parsed.path if parsed.scheme or parsed.netloc else value
    if not path.startswith("/"):
        return None
    return SITE_DIR / path.lstrip("/")


def png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as f:
            header = f.read(24)
        if len(header) < 24 or header[:8] != b"\x89PNG\r\n\x1a\n" or header[12:16] != b"IHDR":
            return None
        return struct.unpack(">II", header[16:24])
    except OSError:
        return None


def expected_meta(text: str, page: Path) -> dict[str, tuple[str, str]]:
    image = find_meta(text, "og:image") or default_image_url(page)
    alt = f"{find_title(text)} — Mneme HQ"
    return {
        "og:image": ("property", image),
        "og:image:width": ("property", str(EXPECTED_WIDTH)),
        "og:image:height": ("property", str(EXPECTED_HEIGHT)),
        "og:image:alt": ("property", alt),
        "twitter:image": ("name", find_meta(text, "twitter:image") or image),
        "twitter:image:alt": ("name", alt),
    }


def rewrite_page(page: Path) -> bool:
    before = page.read_text(encoding="utf-8")
    after = before
    for key, (attr, value) in expected_meta(before, page).items():
        after = upsert_meta(after, attr, key, value)
    if after != before:
        page.write_text(after, encoding="utf-8", newline="\n")
        return True
    return False


def validate_page(page: Path, require_images: bool) -> list[str]:
    text = page.read_text(encoding="utf-8")
    issues: list[str] = []
    expected = expected_meta(text, page)
    for key, (_, wanted) in expected.items():
        actual = find_meta(text, key)
        if not actual:
            issues.append(f"missing {key}")
        elif key in {"og:image:width", "og:image:height"} and actual != wanted:
            issues.append(f"{key}={actual!r}, expected {wanted!r}")

    image = find_meta(text, "og:image")
    twitter = find_meta(text, "twitter:image")
    if image and twitter and image != twitter:
        issues.append("twitter:image does not match og:image")

    if require_images and image:
        image_file = image_file_from_url(image)
        if image_file is not None:
            if not image_file.exists():
                issues.append(f"referenced image missing: {image_file.relative_to(ROOT)}")
            else:
                dims = png_dimensions(image_file)
                if dims != (EXPECTED_WIDTH, EXPECTED_HEIGHT):
                    issues.append(f"image dimensions {dims}, expected {(EXPECTED_WIDTH, EXPECTED_HEIGHT)}")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    ap.add_argument("--require-images", action="store_true", help="also require referenced local PNG files and 1200x630 dimensions")
    args = ap.parse_args()

    pages = public_html_pages()
    if args.write:
        changed = sum(1 for page in pages if rewrite_page(page))
        print(f"Updated OG metadata in {changed} of {len(pages)} public HTML pages.")

    failures = 0
    for page in pages:
        issues = validate_page(page, args.require_images)
        if issues:
            failures += 1
            rel = page.relative_to(ROOT)
            print(f"FAIL {rel}: {'; '.join(issues)}")

    if failures:
        print(f"\n{failures} page(s) failed OG coverage checks.")
        return 1
    print(f"OG coverage OK across {len(pages)} public HTML pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
