#!/usr/bin/env python3
"""Retire "Request a drift audit" as customer-facing CTA copy (P0-C).

Canonical CTA language (docs/site/cta-system.md):

    Analyze repository  -> Run Architecture Audit   -> /audit/
    Experience Mneme    -> Run the 2-minute demo    -> /demo/
    Self-serve          -> Install Mneme            -> quickstart/install
    Work with Mneme HQ  -> Request a pilot          -> /pilot/

"Request a drift audit" described an Audit but linked to /pilot/, and the
"drift audit" label is retired outright. This one-off sweep rewrites the label
wherever it survives in customer-facing sources:

  - site/**/*.html          (except og-*.html OpenGraph templates)
  - templates/**/*.html     (canonical CTA partials)
  - scripts/sweep_team_cta.py, scripts/sweep_demo_cta.py
    (the legacy one-off sweeps hardcode the old label; left unchanged they
    would regenerate it on a re-run)

Idempotent: sources already carrying only canonical labels are left untouched.
The zero-hit acceptance gate is scripts/check_drift_audit_cta.py (CI).

Usage:
  python scripts/sweep_drift_audit_cta.py
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parent.parent

OLD_LABEL = "Request a drift audit"
NEW_LABEL = "Request a pilot"

LEGACY_SWEEP_SCRIPTS = [
    "scripts/sweep_team_cta.py",
    "scripts/sweep_demo_cta.py",
]


def sweep_text(text: str) -> tuple[str, int]:
    """Replace the retired label. Returns (new_text, replacement_count)."""
    return text.replace(OLD_LABEL, NEW_LABEL), text.count(OLD_LABEL)


def targets() -> Iterable[Path]:
    for pattern in ("site/**/*.html", "templates/**/*.html"):
        for path in sorted(REPO_ROOT.glob(pattern)):
            if path.name.startswith("og-"):
                continue  # OG image templates are not customer-facing copy
            yield path
    for name in LEGACY_SWEEP_SCRIPTS:
        yield REPO_ROOT / name


def main() -> int:
    changed: list[str] = []
    for path in targets():
        if not path.exists():
            print(f"WARN missing: {path.relative_to(REPO_ROOT)}")
            continue
        raw = path.read_bytes()
        text = raw.decode("utf-8")
        new_text, count = sweep_text(text)
        if count:
            path.write_bytes(new_text.encode("utf-8"))
            changed.append(f"{path.relative_to(REPO_ROOT)} ({count})")
    for line in changed:
        print(f"ok {line}")
    print(f"{len(changed)} source(s) updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
