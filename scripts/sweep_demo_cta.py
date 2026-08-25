"""PR2 sweep: canonical demo-detail CTA section (#try).
- Pages WITH the old block: swap the lime cta-actions for the canonical cluster
  + install module (keeps the existing cta-tertiary line).
- Pages WITHOUT #try: insert the full section before </main>.
Idempotent: skips files already containing cta-btn-primary inside #try.
"""
import re
from pathlib import Path

SITE = Path(__file__).parent.parent / "site" / "demo"

INSTALL_MODULE = """<div class="install-module" id="install" style="text-align:left;max-width:520px;margin:0 auto 1.25rem;">
          <div class="install-module-cmd">
            <code>pip install mneme-hq</code>
            <button type="button" class="install-module-copy" data-code-copy data-copy-text="pip install mneme-hq"
                    onclick="navigator.clipboard.writeText('pip install mneme-hq');this.dataset.copied='true';this.textContent='Copied';setTimeout(()=>{this.dataset.copied='false';this.textContent='Copy';},1600);">Copy</button>
          </div>
          <div class="install-module-meta">
            <a href="/docs/#quickstart" data-cta-intent="quickstart" data-cta-position="end" data-cta-component="install_module">5-minute quickstart</a>
            <span>Python 3.10+</span>
            <span>MIT licensed</span>
          </div>
        </div>"""

CLUSTER = """<div class="cta-actions">
          <a class="cta-btn-primary" href="/docs/#quickstart" data-cta-intent="install" data-cta-position="end" data-cta-component="install_module">Install Mneme</a>
          <a class="cta-link" href="/pilot/" data-cta-intent="pilot" data-cta-position="end" data-cta-component="install_module">Evaluating for your team? Request a drift audit &rarr;</a>
        </div>"""

NEW_SECTION = f"""<section class="cta-snippet" id="try">
        <h3>Ready to try it?</h3>
        <p>Install the CLI and check your first decision in under a minute.</p>
        {INSTALL_MODULE}
        {CLUSTER}
        <p class="cta-tertiary"><a href="https://github.com/MnemeHQ/mneme">View source on GitHub</a> &middot; <a href="/demo/">All demos</a></p>
      </section>
"""

OLD_ACTIONS = re.compile(
    r'<div class="cta-actions">\s*'
    r'<a class="cta-primary" href="/docs/">Install the CLI</a>\s*'
    r'<a class="cta-secondary" href="/pilot/">Request a pilot</a>\s*'
    r'</div>'
)

changed = []
for d in sorted(SITE.iterdir()):
    f = d / "index.html"
    if d.name == "index.html" or not f.exists():
        continue
    if d.name == "index.html":
        continue
    text = f.read_text(encoding="utf-8")
    orig = text

    if 'id="try"' in text:
        if "cta-btn-primary" in text:
            continue  # already canonical
        m = OLD_ACTIONS.search(text)
        if not m:
            print(f"WARN {d.name}: #try exists but no known cta-actions block")
            continue
        text = OLD_ACTIONS.sub(INSTALL_MODULE + "\n        " + CLUSTER, text, count=1)
        f.write_bytes(text.encode("utf-8"))
        changed.append(f"{d.name}: upgraded")
    else:
        if "</main>" not in text:
            print(f"WARN {d.name}: no </main>")
            continue
        text = text.replace("</main>", NEW_SECTION + "  </main>", 1)
        f.write_bytes(text.encode("utf-8"))
        changed.append(f"{d.name}: inserted")

for c in changed:
    print(c)
print(f"{len(changed)} demo pages updated")
