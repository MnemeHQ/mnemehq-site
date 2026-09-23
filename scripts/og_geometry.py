#!/usr/bin/env python3
"""The eight Editorial motifs.

Motif is chosen semantically upstream (og_manifest.motif_for_slug); this
module only draws. The slug hash varies geometry *within* the chosen
motif -- node positions, which edges exist, which node is highlighted --
so cards sharing a motif still differ.

Red appears only when tone == "failure". In neutral tone the highlight is
sage alone.

Ported from the reviewed mockup builder (approved-mockup-reference.py,
`geometry()` + its `_node`/`_ring`/`_cross`/`_line` helpers). That script
was a throwaway design-review tool; the geometry it drew is approved as-is,
but four of its eight branches ("connected", "broken", "boundary",
"isolated") drew their sage/red marker inside a single mutually-exclusive
`if fail: ... else: ...`, so the mockup only ever emitted ONE of sage or
red for that node depending on tone -- never both, and in "connected"'s
case never red at all. Production requires sage in *every* tone and red
only (but always) in failure tone, so those four branches were adjusted to
draw the sage element unconditionally and layer the red marker on top only
when `fail`, matching the pattern the "stack" and "intersection" branches
already used correctly in the reference.
"""
from __future__ import annotations

import hashlib
import math

from og_manifest import MOTIFS

GREY, DIM, SAGE, RED = "#4a4a54", "#34343c", "#b5cc7a", "#ff5c7a"


def _node(x, y, r=9, fill=GREY, op="1"):
    return '<circle cx="%g" cy="%g" r="%g" fill="%s" opacity="%s"/>' % (x, y, r, fill, op)


def _ring(x, y, col, r=27):
    return ('<circle cx="%g" cy="%g" r="%g" fill="#0c0c0d" stroke="%s" stroke-width="4.5"/>'
            '<circle cx="%g" cy="%g" r="9" fill="%s"/>' % (x, y, r, col, x, y, col))


def _cross(x, y, col, r=27):
    d = 12
    return ('<circle cx="%g" cy="%g" r="%g" fill="#0c0c0d" stroke="%s" stroke-width="4.5"/>'
            '<path d="M%g,%g L%g,%g M%g,%g L%g,%g" stroke="%s" stroke-width="4.5" stroke-linecap="round"/>'
            % (x, y, r, col, x - d, y - d, x + d, y + d, x + d, y - d, x - d, y + d, col))


def _line(x1, y1, x2, y2, col=DIM, w=3, dash=None):
    da = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<line x1="%g" y1="%g" x2="%g" y2="%g" stroke="%s" stroke-width="%g"%s/>'
            % (x1, y1, x2, y2, col, w, da))


def render(slug: str, motif: str, tone: str = "neutral", size: int = 286) -> str:
    if motif not in MOTIFS:
        raise ValueError(f"unknown motif {motif!r}; expected one of {MOTIFS}")
    d = hashlib.sha256(slug.encode()).digest()
    fail = tone == "failure"
    mark = RED if fail else SAGE
    p: list[str] = []
    S = size
    cx = cy = S / 2

    if motif == "connected":
        pts = [(S * .18, S * .22), (S * .62, S * .16), (S * .84, S * .46),
               (S * .5, S * .52), (S * .22, S * .72), (S * .68, S * .84)]
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                if d[(i * 6 + j) % 32] & 0x3:
                    p.append(_line(*pts[i], *pts[j]))
        hi = d[1] % len(pts)
        for i, (x, y) in enumerate(pts):
            p.append(_ring(x, y, SAGE) if i == hi else _node(x, y))
        if fail:
            bx, by = pts[(hi + 1) % len(pts)]
            p.append(_cross(bx, by, RED))

    elif motif == "broken":
        y = cy
        xs = [S * .1 + i * (S * .8 / 4) for i in range(5)]
        gap = 1 + d[1] % 3
        for i in range(4):
            if i == gap:
                p.append(_line(xs[i] + 18, y, xs[i] + 52, y, DIM, 3, "7 11"))
                p.append(_line(xs[i + 1] - 52, y, xs[i + 1] - 18, y, DIM, 3, "7 11"))
            else:
                p.append(_line(xs[i] + 14, y, xs[i + 1] - 14, y, DIM, 3))
        for i, x in enumerate(xs):
            if i == gap:
                p.append(_ring(x, y, SAGE))
                if fail:
                    p.append(_cross(x, y, RED))
            else:
                p.append(_node(x, y, 11))

    elif motif == "boundary":
        bx = S * .52
        p.append(_line(bx, S * .08, bx, S * .92, SAGE, 4.5))
        for i in range(4):
            p.append(_node(S * .16 + (i % 2) * S * .16, S * .2 + i * S * .2, 10))
        for i in range(3):
            p.append(_node(S * .72 + (i % 2) * S * .14, S * .28 + i * S * .22, 10, DIM))
        yy = S * .2 + (d[1] % 4) * S * .2
        p.append(_line(S * .3, yy, bx - 30, yy, DIM, 3))
        p.append(_ring(bx, yy, SAGE))
        if fail:
            p.append(_cross(bx, yy, RED))

    elif motif == "branch":
        ox, oy = S * .14, cy
        p.append(_line(ox, oy, S * .46, oy, DIM, 3))
        p.append(_line(S * .46, oy, S * .82, S * .22, DIM, 3))
        p.append(_line(S * .46, oy, S * .82, S * .78, DIM, 3))
        p.append(_node(ox, oy, 11))
        p.append(_node(S * .46, oy, 11))
        up = d[1] & 1
        p.append(_ring(S * .82, S * .22 if up else S * .78, SAGE))
        ox2, oy2 = S * .82, S * .78 if up else S * .22
        p.append(_cross(ox2, oy2, mark) if fail else _node(ox2, oy2, 11, DIM))

    elif motif == "stack":
        h, g = S * .13, S * .05
        hi = d[1] % 4
        for i in range(4):
            yy = S * .16 + i * (h + g)
            col = SAGE if i == hi else DIM
            wdt = S * (.56 + ((d[(i + 3) % 32] % 5) * .06))
            p.append('<rect x="%g" y="%g" width="%g" height="%g" rx="7" fill="none" '
                     'stroke="%s" stroke-width="%g"/>' % (S * .12, yy, wdt, h, col, 4 if i == hi else 3))
        if fail:
            p.append(_cross(S * .8, S * .16 + ((hi + 2) % 4) * (h + g) + h / 2, mark, 23))

    elif motif == "intersection":
        p.append(_line(S * .1, S * .78, S * .9, S * .24, DIM, 3))
        p.append(_line(S * .16, S * .2, S * .86, S * .8, DIM, 3))
        p.append(_ring(S * .5, S * .5, SAGE, 30))
        for x, y in ((S * .1, S * .78), (S * .9, S * .24), (S * .16, S * .2), (S * .86, S * .8)):
            p.append(_node(x, y, 10))
        if fail:
            p.append(_cross(S * .86, S * .8, mark, 23))

    elif motif == "propagation":
        ring = [(cx + S * .34 * math.cos(a), cy + S * .34 * math.sin(a))
                for a in [i * 0.7854 for i in range(8)]]
        blocked = d[1] % 8 if fail else -1
        for i, (x, y) in enumerate(ring):
            p.append(_line(cx, cy, x, y, DIM, 3, "6 10" if i == blocked else None))
        p.append(_ring(cx, cy, SAGE, 30))
        for i, (x, y) in enumerate(ring):
            p.append(_cross(x, y, mark, 22) if i == blocked else _node(x, y, 10))

    elif motif == "isolated":
        cl = [(S * .2, S * .28), (S * .38, S * .2), (S * .3, S * .46), (S * .5, S * .38)]
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                p.append(_line(*cl[i], *cl[j]))
        for x, y in cl:
            p.append(_node(x, y, 10))
        ax, ay = S * .74, S * .78
        p.append(_line(S * .5, S * .38, ax - 34, ay - 34, DIM, 3, "7 11"))
        p.append(_ring(ax, ay, SAGE))
        if fail:
            p.append(_cross(ax, ay, RED))

    return (f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" '
            f'data-motif="{motif}" class="og-geometry">{"".join(p)}</svg>')
