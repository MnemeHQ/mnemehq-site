"""P2 pass A: prune dead hm-* rules from home-v2.css and collapse the
triple-stacked .hm-install cascade into its effective result.

Conservative rule: a rule is removed only if EVERY selector in its
comma-group contains at least one class token that is unused across
homepage markup (the only page that links this stylesheet).
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
CSS = REPO / "site" / "assets" / "css" / "home-v2.css"
HOME = REPO / "site" / "index.html"

markup = HOME.read_text(encoding="utf-8")

# classes referenced by css
css_text = CSS.read_text(encoding="utf-8")
all_classes = sorted(set(re.findall(r"\.([a-z][a-z0-9-]*)", css_text)))
unused = {c for c in all_classes if markup.count(c) == 0}
print(f"unused classes: {len(unused)}")


def selector_is_dead(sel: str) -> bool:
    sels = [s.strip() for s in sel.split(",")]
    return bool(sels) and all(
        any(re.search(rf"\.{re.escape(u)}\b", s) for u in unused)
        for s in sels
    )


def prune(css: str) -> tuple[str, int]:
    """Return pruned css and number of removed top-level/inner rules."""
    out = []
    i = 0
    n = len(css)
    removed = 0
    while i < n:
        b = css.find("{", i)
        if b == -1:
            out.append(css[i:])
            break
        head = css[i:b]
        sel = head.rstrip("{ \t\r\n")
        depth = 1
        j = b + 1
        while j < n and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[b + 1:j - 1]

        if sel.startswith("@media"):
            new_body, k = prune(body)
            removed += k
            if norm(new_body):
                out.append(css[i:b + 1] + new_body + "}")
            # else: drop whole empty media block
            i = j
            continue

        if sel.startswith("@"):
            out.append(css[i:j])  # keep other at-rules (keyframes etc.)
            i = j
            continue

        if selector_is_dead(sel):
            removed += 1
        else:
            out.append(css[i:j])
        i = j
    return "".join(out), removed


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\r\n", "\n")).strip()


pruned, removed = prune(css_text)
print(f"rules removed: {removed}")

# ── collapse the .hm-install triple stack ────────────────────────────────
# Effective cascade result of blocks at (orig) 1917, 1948, 1960:
INSTALL_EFFECTIVE = """
/* Install banner - single effective block (collapsed from three
   historically stacked variants; final cascade values preserved). */
.hm-install { border-top: 1px solid var(--border); border-bottom: 1px solid var(--border); background: var(--surface); }
.hm-install-inner { display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; padding: 1.15rem 0; }
.hm-install-label { color: var(--quiet); font-family: var(--mono); font-size: .6rem; letter-spacing: .14em; text-transform: uppercase; }
.hm-install-cmd { flex: 1 1 auto; min-width: 220px; padding: .6rem .9rem; border: 1px solid var(--border2); border-radius: 4px; background: var(--bg); color: var(--teal); font-family: var(--mono); font-size: .84rem; }
.hm-install-copy { padding: .6rem 1rem; border: 1px solid var(--border2); border-radius: 4px; background: var(--surface2); color: var(--muted); font-family: var(--mono); font-size: .7rem; letter-spacing: .06em; text-transform: uppercase; cursor: pointer; transition: color .15s, border-color .15s; }
.hm-install-copy:hover { border-color: var(--accent); color: var(--accent); background: var(--surface3); }
.hm-install-alt { color: var(--quiet); font-family: var(--mono); font-size: .68rem; text-decoration: none; white-space: nowrap; }
.hm-install-alt:hover { color: var(--accent); }
@media (max-width: 640px) { .hm-install-cmd { font-size: .74rem; } }
"""

pat = re.compile(
    r"\n*/\* Install is the first rung.*?(?=\n\n/\* | \Z)", re.S)
assert pat.search(pruned), "install region not found"
pruned = pat.sub(INSTALL_EFFECTIVE, pruned, count=1)

CSS.write_bytes(pruned.encode("utf-8"))
print(f"home-v2.css: {len(css_text)} -> {len(pruned)} bytes")
