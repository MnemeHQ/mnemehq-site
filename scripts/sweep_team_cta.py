"""PR3 sweep: team/role pages — pilot-first clusters per docs/site/cta-system.md.
Replaces contact/GitHub lime primaries with coral 'Request a drift audit'.
"""
from pathlib import Path

PILOT_PRIMARY = (
    '<a href="/pilot/" class="cta-btn-primary" data-cta-intent="pilot" '
    'data-cta-position="{pos}" data-cta-component="hero_cluster">Request a drift audit</a>'
)
GITHUB_TEXT = (
    '<a href="https://github.com/MnemeHQ/mneme" class="cta-link" data-cta-intent="github" '
    'data-cta-position="{pos}" data-cta-component="hero_cluster">View source on GitHub &rarr;</a>'
)
DEMO_GHOST = (
    '<a href="/demo/" class="btn-ghost" data-cta-intent="demo" '
    'data-cta-position="{pos}" data-cta-component="hero_cluster">Run the 2-minute demo</a>'
)

REPLACEMENTS = {
    "site/for/cto/index.html": [
        # hero
        (
            '<div class="cta-group">\n      '
            '<a href="/contact/" class="btn-primary">Talk to the founder</a>\n      '
            '<a href="/use-cases/" class="btn-ghost">See use cases</a>\n    </div>',
            '<div class="cta-group">\n      '
            + PILOT_PRIMARY.format(pos="hero") + "\n      "
            + DEMO_GHOST.format(pos="hero") + "\n      "
            + GITHUB_TEXT.format(pos="hero") + "\n    </div>",
        ),
        # footer
        (
            '<a href="/contact/" class="btn-primary">Talk to the founder</a> <a href="/roadmap/" class="btn-ghost">See the roadmap</a>',
            PILOT_PRIMARY.format(pos="end") + " " + '<a href="/roadmap/" class="btn-ghost">See the roadmap</a>',
        ),
    ],
    "site/for/platform/index.html": [
        (
            '<a href="https://github.com/MnemeHQ/mneme" class="btn-primary">View on GitHub</a> <a href="/use-cases/" class="btn-ghost">See all use cases</a>',
            PILOT_PRIMARY.format(pos="hero") + " "
            + '<a href="/use-cases/" class="btn-ghost">See all use cases</a> ' + GITHUB_TEXT.format(pos="hero"),
        ),
    ],
    "site/for/principal-engineer/index.html": [
        (
            '<a href="https://github.com/MnemeHQ/mneme" class="btn-primary">View on GitHub</a>',
            PILOT_PRIMARY.format(pos="end") + " " + GITHUB_TEXT.format(pos="end"),
        ),
    ],
}

for path, pairs in REPLACEMENTS.items():
    f = Path(path)
    t = f.read_text(encoding="utf-8")
    for old, new in pairs:
        if old in t:
            t = t.replace(old, new)
            print(f"ok   {path}: {new[:70]}...")
        else:
            print(f"MISS {path}: pattern not found: {old[:80]}")
    f.write_bytes(t.encode("utf-8"))
