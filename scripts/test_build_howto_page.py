"""The how-to builder must emit manifest-backed images and complete JSON-LD."""
from __future__ import annotations

import json
import re
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


def _jsonld(meta: dict) -> list[dict]:
    block = build_howto_page.jsonld(
        meta,
        [("Home", "https://mnemehq.com/"), ("How-to guides", meta["url"])],
        f"{meta['url']}og-v2.png",
    )
    payload = re.search(r"<script[^>]*>(.*)</script>", block, re.S)
    return json.loads(payload.group(1))["@graph"]


def test_guide_schema_has_google_article_type_image_and_relationships():
    url = "https://mnemehq.com/docs/how-to/example/"
    graph = _jsonld({
        "url": url,
        "h1_plain": "Example guide",
        "description": "An example.",
        "date": "2026-10-04",
        "modified": "2026-10-12",
    })
    article = next(node for node in graph if "TechArticle" in node.get("@type", []))
    assert article["@type"] == ["Article", "TechArticle"]
    assert article["dateModified"] == "2026-10-12"
    assert article["image"]["url"] == f"{url}og-v2.png"
    assert article["mainEntityOfPage"]["@id"] == f"{url}#webpage"
    assert article["isPartOf"]["@id"] == "https://mnemehq.com/docs/how-to/#webpage"
    assert article["inLanguage"] == "en"


def test_hub_schema_exposes_an_ordered_item_list():
    url = "https://mnemehq.com/docs/how-to/"
    graph = _jsonld({
        "url": url,
        "h1_plain": "How-to guides",
        "description": "Guides.",
        "date": "2026-10-05",
        "modified": "2026-10-12",
        "collection": [
            ("First", f"{url}first/"),
            ("Second", f"{url}second/"),
        ],
    })
    collection = next(node for node in graph if node.get("@type") == "CollectionPage")
    item_list = next(node for node in graph if node.get("@type") == "ItemList")
    assert collection["mainEntity"]["@id"] == item_list["@id"]
    assert collection["dateModified"] == "2026-10-12"
    assert item_list["numberOfItems"] == 2
    assert [item["position"] for item in item_list["itemListElement"]] == [1, 2]
