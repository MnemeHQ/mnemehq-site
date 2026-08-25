"""PR4 sweep:
1. Insights: insert cta-band before the SECOND <h2> (after first proof section).
2. Concepts: append soft 'See this enforced' link at end of article-body.
3. Benchmark: top actions cluster after the hero lede.
Idempotent via cta-band / concept-cta-link / benchmark-cta markers.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site"

BAND = """<aside class="cta-band" aria-label="Try Mneme">
  <div class="cta-band-eyebrow">Runnable in five minutes</div>
  <h3>See this enforced on your own repository</h3>
  <p>Install the CLI, add one decision, run one check. No signup, no telemetry &mdash; MIT licensed.</p>
  <div class="cta-row">
    <a href="/docs/#quickstart" class="cta-btn-primary" data-cta-intent="install" data-cta-position="mid" data-cta-component="cta_band">Install Mneme</a>
    <a href="/demo/" class="cta-btn-outline" data-cta-intent="demo" data-cta-position="mid" data-cta-component="cta_band">Run the 2-minute demo</a>
  </div>
</aside>
"""

CONCEPT_LINK = """<p style="margin-top:2.5rem;"><a class="cta-link" href="/demo/" data-cta-intent="demo" data-cta-position="end" data-cta-component="concept_link">See this enforced in the 2-minute demo &rarr;</a></p>
"""

BENCHMARK_CLUSTER = """  <div class="cta-row" style="margin-top:1.5rem;" id="benchmark-cta">
    <a href="https://github.com/MnemeHQ/mneme/tree/main/examples/benchmarks" class="cta-btn-primary" target="_blank" rel="noopener" data-cta-intent="benchmark" data-cta-position="hero" data-cta-component="hero_cluster">Run the benchmark</a>
    <a href="https://github.com/MnemeHQ/mneme/discussions" class="cta-btn-outline" target="_blank" rel="noopener" data-cta-intent="contribute" data-cta-position="hero" data-cta-component="hero_cluster">Contribute a scenario</a>
  </div>
"""

# ── 1. Insights ──
ins_changed = skipped = 0
for d in sorted((SITE / "insights").iterdir()):
    if not d.is_dir() or d.name in ("topics", "all"):
        continue
    f = d / "index.html"
    if not f.exists():
        continue
    t = f.read_text(encoding="utf-8")
    if "cta-band" in t:
        skipped += 1
        continue
    h2s = [m for m in re.finditer(r"<h2[ >]", t)]
    if len(h2s) < 2:
        skipped += 1
        continue
    pos = h2s[1].start()
    t = t[:pos] + BAND + t[pos:]
    f.write_bytes(t.encode("utf-8"))
    ins_changed += 1
print(f"insights: {ins_changed} bands inserted, {skipped} skipped")

# ── 2. Concepts ──
con_changed = cskipped = 0
for d in sorted((SITE / "concepts").iterdir()):
    if not d.is_dir():
        continue
    f = d / "index.html"
    if not f.exists():
        continue
    t = f.read_text(encoding="utf-8")
    if "concept_link" in t:
        cskipped += 1
        continue
    m = re.search(r'<div class="related-panel"', t)
    if m:
        t = t[:m.start()] + CONCEPT_LINK + t[m.start():]
    else:
        # append inside article-body: before its closing </div> preceding </article>
        m2 = re.search(r"</article>", t)
        if not m2:
            cskipped += 1
            continue
        close = t.rfind("</div>", 0, m2.start())
        if close == -1:
            cskipped += 1
            continue
        t = t[:close] + CONCEPT_LINK + t[close:]
    f.write_bytes(t.encode("utf-8"))
    con_changed += 1
print(f"concepts: {con_changed} links inserted, {cskipped} skipped")

# ── 3. Benchmark ──
bf = SITE / "benchmark" / "index.html"
bt = bf.read_text(encoding="utf-8")
if "benchmark-cta" not in bt:
    anchor = '<div class="toc">'
    bt = bt.replace(anchor, BENCHMARK_CLUSTER + anchor, 1)
    bf.write_bytes(bt.encode("utf-8"))
    print("benchmark: top cluster inserted")
else:
    print("benchmark: already present")
