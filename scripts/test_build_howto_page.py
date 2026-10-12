"""build_howto_page must advertise the OG card the manifest names for each page."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_howto_page  # noqa: E402
import og_manifest  # noqa: E402

MANIFEST = Path(__file__).resolve().parents[1] / "site" / "og" / "cards.yaml"


def _manifest_card(rel: str) -> str:
    raw = og_manifest.load(MANIFEST)
    return og_manifest.resolve(rel, raw.get(rel), strict=True)["card"]


def test_hub_uses_the_manifest_card_name():
    rel = "docs/how-to/"
    assert build_howto_page.og_image_url(rel) == f"https://mnemehq.com/{rel}{_manifest_card(rel)}"


def test_guide_uses_the_manifest_card_name():
    rel = "docs/how-to/give-agents-applicable-decisions/"
    assert build_howto_page.og_image_url(rel) == f"https://mnemehq.com/{rel}{_manifest_card(rel)}"
