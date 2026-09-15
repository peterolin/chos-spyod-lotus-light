#!/usr/bin/env python3
"""Fill the prev/next arrows in src/ from spine + document order.

Every practice in the book sits under a heading like

    <h1 class="tocpage1" id="page420">བརྗོད་མེད་དོན་བཤགས།</h1><span class="pageno">420</span>

followed by a nav block

    <div class="wrap">
      <a class="left"  href="…" title="…"/>
      <a class="ppnp">420</a>
      <a class="right" href="…" title="…"/>
    </div>

Those headings, walked in spine order, ARE the reading order of the book, so
prev/next can be derived rather than typed. This fills only the arrows that
still hold a placeholder (`../pn.htm#todo`, `#TODO`, `title="todoprev"` …);
arrows that already point somewhere real are left alone, but are checked and
reported when they disagree with document order.

It also audits the JUMP LINKS: an arrow that points the wrong way is worse
than no arrow, and neither check.py nor a reading of the page will catch it,
because the link still resolves. Direction is measured from real reading
order — spine index, then position within the document — so it is as
mechanically certain as the prev/next chain, and --write corrects it.

    python3 tools/nav.py            report only (default)
    python3 tools/nav.py --write    rewrite the placeholders, turn wrong arrows

Run tools/check.py afterwards.
"""

import argparse
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path, PurePosixPath

SRC = Path(__file__).resolve().parent.parent / "src"

# A section heading that can be linked to: has both tocpageN class and an id.
HEADING = re.compile(
    r'<h[1-6][^>]*\bclass="tocpage[12]"[^>]*\bid="([^"]+)"[^>]*>(.*?)</h[1-6]>',
    re.S,
)
# The page number lives INSIDE the heading now (moved there so a reader cannot
# break it away from the title), so it is read out of the heading's content and
# then removed from the title text.
PAGENO_IN = re.compile(r'<span class="pageno[^"]*">([^<]*)</span>', re.S)

# A jump link in the running text, and which direction each class claims.
# jumpTODO renders a literal "TODO " prefix, so it is deliberately unfinished
# and gets no arrow; key.xhtml is the legend, whose rows demonstrate each
# class BY NAME and so must keep the class they document.
JUMP = re.compile(
    r'<a class="(jump|jumpUp|jumpDown|jumpTODO|jumpTodO|easyjump)"'
    r'((?=[^>]*\bhref="([^"]+)")[^>]*)>')
CLAIMS = {"jumpUp": "back", "jumpDown": "fwd"}
LEGEND = "key.xhtml"

# A left/right arrow inside a nav block.
ARROW = re.compile(r'<a\s+class="(left|right)"\s+([^>]*?)(/?)>')

# href/title values that mean "not filled in yet".
PLACEHOLDER_HREF = re.compile(r'pn\.htm#todo|#TODO\b|#todo\b|#\?\?', re.I)
PLACEHOLDER_TITLE = re.compile(
    r'^\s*(todo\w*|todo[_ ]?(prev|previous|next)|previous prayer|next prayer|'
    r'something( else)?|\?\?\??.*)\s*$',
    re.I,
)

TAGS = re.compile(r"<[^>]+>")
# A few headings carry the page number inline as a ppnp badge; it is not part
# of the title, and tooltip() appends the page number itself.
PPNP_BADGE = re.compile(r'<a class="ppnp">.*?</a>', re.S)
# Editorial noise that crept into a few heading texts.
NOISE = re.compile(r"TODO\s*phys\s*page\s*\??\?*|\?\?\?+", re.I)
# A tooltip ending in the same page number twice: 'ཇ་མཆོད། 175 175'.
DOUBLED_PAGE = re.compile(r"^(.*?\b(\d+))\s+\2\s*$", re.S)


def spine_order():
    """Content documents in reading order, per content.opf.

    Parsed as XML, not by regex: the manifest is not consistent about
    attribute order (some items write id before href).
    """
    root = ET.parse(SRC / "content.opf").getroot()

    def tag(el):
        return el.tag.split("}")[-1]

    manifest = {}
    for el in root.iter():
        if tag(el) == "item" and el.get("id") and el.get("href"):
            manifest[el.get("id")] = el.get("href")

    order = []
    for el in root.iter():
        if tag(el) == "itemref":
            href = manifest.get(el.get("idref"))
            if href and href.endswith((".htm", ".html", ".xhtml")):
                order.append(href)
    return order


def clean_title(raw):
    text = NOISE.sub("", TAGS.sub("", PPNP_BADGE.sub("", raw)))
    return " ".join(text.split())


def collect(files):
    """Every linkable section, in reading order.

    Returns a list of dicts and, per file, the character offset of each
    section so a nav block can be matched to the section it sits in.
    """
    sections, per_file = [], {}
    for rel in files:
        path = SRC / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        found = []
        for m in HEADING.finditer(text):
            inner = m.group(2)
            pm = PAGENO_IN.search(inner)
            sec = {
                "file": rel,
                "id": m.group(1),
                "title": clean_title(PAGENO_IN.sub("", inner)),
                "page": (pm.group(1) if pm else "").strip(),
                "start": m.start(),
            }
            found.append(sec)
            sections.append(sec)
        per_file[rel] = (text, found)
    return sections, per_file


def link_to(target, from_file):
    """href for target as seen from from_file.

    Most documents live in OPS/, but not all: c_fastjump.htm, pn.htm,
    repeats.htm and key.xhtml sit at the root beside it. A bare basename is
    only right when the two share a directory, so the path is computed
    relative to the linking document.
    """
    frag = f"#{target['id']}"
    if target["file"] == from_file:
        return frag
    rel = os.path.relpath(target["file"], Path(from_file).parent)
    return PurePosixPath(rel).as_posix() + frag


def tooltip(target):
    """'TITLE PAGE', the convention the hand-written arrows use.

    A few headings already end in their own page number (they are pointers to
    a practice printed elsewhere); appending it again would read '742 742'.
    """
    page = NOISE.sub("", target["page"]).strip()
    title = target["title"]
    if page and re.search(rf"\b{re.escape(page)}\s*$", title):
        return title
    return f"{title} {page}".strip()


def attr(attrs, name):
    m = re.search(rf'\b{name}="([^"]*)"', attrs)
    return m.group(1) if m else None


def set_attr(attrs, name, value):
    if re.search(rf'\b{name}="', attrs):
        return re.sub(rf'\b{name}="[^"]*"', f'{name}="{value}"', attrs, count=1)
    return f'{attrs.rstrip()} {name}="{value}"'


def id_positions(files):
    """Absolute position of every id in the book: (document index, offset)."""
    pos = {}
    for i, rel in enumerate(files):
        text = (SRC / rel).read_text(encoding="utf-8")
        for m in re.finditer(r'\bid="([^"]+)"', text):
            pos[(rel, m.group(1))] = (i, m.start())
    return pos


def audit_jumps(files, apply=False):
    """Check every jump link's arrow against the direction it actually goes.

    Returns (turned, arrowless). A reversed arrow is mechanically certain —
    the target either precedes the link in reading order or follows it — so
    --write swaps the class. A link whose class has no arrow at all is only
    reported: whether that class was chosen deliberately is a judgement.
    """
    pos = id_positions(files)
    turned, arrowless = [], []

    for i, rel in enumerate(files):
        if Path(rel).name == LEGEND:
            continue
        path = SRC / rel
        text = path.read_text(encoding="utf-8")
        changed = False

        def classify(m):
            nonlocal changed
            cls, attrs, href = m.group(1), m.group(2), m.group(3)
            if "#" not in href:
                return m.group(0)
            target_file, frag = href.split("#", 1)
            key = (rel if not target_file else "OPS/" + Path(target_file).name, frag)
            if key not in pos:
                return m.group(0)          # check.py reports unresolvable ones
            goes = "fwd" if pos[key] > (i, m.start()) else "back"
            want = "jumpDown" if goes == "fwd" else "jumpUp"

            if cls not in CLAIMS:
                if cls != "jumpTODO":
                    arrowless.append((rel, cls, want, frag))
                return m.group(0)
            if CLAIMS[cls] == goes:
                return m.group(0)

            turned.append((rel, cls, want, frag))
            if apply:
                changed = True
                return f'<a class="{want}"{attrs}>'
            return m.group(0)

        new = JUMP.sub(classify, text)
        if apply and changed:
            path.write_text(new, encoding="utf-8")

    return turned, arrowless


PRAYER = re.compile(r'<h[1-6][^>]*\bclass="(tocpage[12])"[^>]*\bid="([^"]+)"', re.S)
# Files whose tocpage2 sub-headings are separate texts for the triangle rule:
# the seven chapters of the ལེའུ་བདུན་མ are read as independent prayers
# (Peter, 2026-09-15). Elsewhere a tocpage2 heading is a section of one text.
SUBTEXT_FILES = {"p257_leu_bdun_ma.htm"}
SCOPE_ATTR = re.compile(r'\s*\bdata-scope="[^"]*"')


def audit_scope(files, apply=False):
    """Stamp every jump link with whether it leaves its prayer.

    The reader sees one triangle for a jump that stays inside the text in
    front of them and two for a jump into another text (Peter, 2026-09-15).
    "Text" means the nearest preceding heading with class tocpage1 — the
    prayer-level heading — not the file: several files hold several prayers.
    In SUBTEXT_FILES the tocpage2 sub-headings count too (the seven chapters).
    A link whose target sits under a different such heading (or in another
    file) gets data-scope="out"; one that stays loses the attribute. The
    stylesheet draws the doubled triangle from that attribute alone. Returns
    the list of links whose stamp changed; --write applies it.
    """
    pos = id_positions(files)
    owners = {}                       # (file, id) -> (file, prayer id)
    prayers = {}                      # file -> [(offset, id)]
    for rel in files:
        text = (SRC / rel).read_text(encoding="utf-8")
        prayers[rel] = [(m.start(), m.group(2)) for m in PRAYER.finditer(text)
                        if m.group(1) == "tocpage1" or Path(rel).name in SUBTEXT_FILES]

    def owner(rel, offset):
        last = None
        for off, pid in prayers.get(rel, []):
            if off <= offset:
                last = pid
            else:
                break
        return (rel, last)

    changes = []
    for rel in files:
        if Path(rel).name == LEGEND:
            continue
        path = SRC / rel
        text = path.read_text(encoding="utf-8")
        changed = False

        def stamp(m):
            nonlocal changed
            cls, attrs, href = m.group(1), m.group(2), m.group(3)
            if cls not in CLAIMS or "#" not in href:
                return m.group(0)
            target_file, frag = href.split("#", 1)
            trel = rel if not target_file else "OPS/" + Path(target_file).name
            if (trel, frag) not in pos:
                return m.group(0)
            here = owner(rel, m.start())
            there = owner(trel, pos[(trel, frag)][1])
            want = "out" if here != there else None
            have = attr(attrs, "data-scope")
            if have == want:
                return m.group(0)
            changes.append((rel, cls, frag, have, want))
            if not apply:
                return m.group(0)
            changed = True
            new_attrs = SCOPE_ATTR.sub("", attrs)
            if want:
                new_attrs = set_attr(new_attrs, "data-scope", want)
            return f'<a class="{cls}"{new_attrs}>'

        new = JUMP.sub(stamp, text)
        if apply and changed:
            path.write_text(new, encoding="utf-8")
    return changes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="apply the changes")
    args = ap.parse_args()

    files = spine_order()
    sections, per_file = collect(files)
    index = {(s["file"], s["id"]): n for n, s in enumerate(sections)}

    filled = kept = mismatch = unfillable = deduped = 0
    drift = []
    notes = []

    for rel, (text, found) in per_file.items():
        if not found:
            continue
        out, cursor, changed = [], 0, False

        # Iterate the ARROWS, not their container. 104 of the 105 nav blocks
        # were dissolved when the arrows moved inside their headings (so a
        # reader can no longer break the header apart and strand them); one
        # still stands on its own mid-text. Finding arrows directly handles
        # both, since an arrow inside a heading still sits at or after that
        # heading's start.
        for arrow in ARROW.finditer(text):
            owner = None
            for sec in found:
                if sec["start"] <= arrow.start():
                    owner = sec
                else:
                    break
            if owner is None:
                notes.append(f"{rel}: arrow at offset {arrow.start()} "
                             f"precedes every heading — skipped")
                unfillable += 1
                continue

            pos = index[(owner["file"], owner["id"])]
            neighbour = {
                "left": sections[pos - 1] if pos > 0 else None,
                "right": sections[pos + 1] if pos + 1 < len(sections) else None,
            }

            def fix(m):
                nonlocal filled, kept, mismatch, unfillable, deduped, changed
                side, attrs, slash = m.group(1), m.group(2), m.group(3)
                target = neighbour[side]
                href, title = attr(attrs, "href") or "", attr(attrs, "title") or ""
                stale = bool(PLACEHOLDER_HREF.search(href)) or bool(
                    PLACEHOLDER_TITLE.match(title)
                )

                if target is None:
                    # First or last section of the whole book.
                    if stale:
                        notes.append(
                            f"{rel}: {owner['id']} has no {side} neighbour "
                            f"(book edge) — placeholder left in place"
                        )
                        unfillable += 1
                    return m.group(0)

                want_href, want_title = link_to(target, rel), tooltip(target)

                if not stale:
                    if href != want_href:
                        notes.append(
                            f"{rel}: {owner['id']} {side} points at '{href}', "
                            f"document order says '{want_href}' — left as is"
                        )
                        mismatch += 1
                        return m.group(0)
                    dup = DOUBLED_PAGE.match(title)
                    if dup:
                        # 'ཇ་མཆོད། 175 175' — the page number twice. The only
                        # tooltip defect that is mechanically certain, so the
                        # only one this tool touches.
                        deduped += 1
                        changed = True
                        attrs = set_attr(attrs, "title", dup.group(1))
                        return f'<a class="{side}" {attrs.strip()}{slash}>'
                    if title != want_title:
                        # Everything else is a judgement call: the heading and
                        # the tooltip disagree on wording, spelling or page
                        # number. Several are Tibetan orthography differences
                        # where the HEADING is the wrong one, so copying it
                        # over would spread the typo. Report, never rewrite.
                        drift.append(
                            f"{rel.split('/')[-1]}: {owner['id']} {side}\n"
                            f"        tooltip: {title!r}\n"
                            f"        heading: {want_title!r}"
                        )
                    else:
                        kept += 1
                    return m.group(0)

                attrs = set_attr(set_attr(attrs, "href", want_href),
                                 "title", want_title)
                filled += 1
                changed = True
                return f'<a class="{side}" {attrs.strip()}{slash}>'

            out.append(text[cursor:arrow.start()])
            out.append(fix(arrow))
            cursor = arrow.end()

        if changed and args.write:
            out.append(text[cursor:])
            (SRC / rel).write_text("".join(out), encoding="utf-8")

    turned, arrowless = audit_jumps(files, apply=args.write)
    rescoped = audit_scope(files, apply=args.write)

    print(f"{len(sections)} linkable sections across {len(per_file)} files\n")
    for n in notes:
        print("  -", n)
    if notes:
        print()
    verb = "filled" if args.write else "fillable"
    print(f"{verb:>10}: {filled}")
    print(f"{'deduped':>10}: {deduped}")
    print(f"{'already ok':>10}: {kept}")
    print(f"{'mismatched':>10}: {mismatch}   (left untouched — review by hand)")
    print(f"{'unfillable':>10}: {unfillable}")
    if drift:
        print(f"\n{len(drift)} tooltips disagree with their heading — yours to judge,")
        print("not the tool's (in several the heading is the wrong spelling):\n")
        for d in drift:
            print("  -", d)
    verb3 = "restamped" if args.write else "need restamping"
    print(f"\njump scope (one triangle inside the prayer, two out) {verb3}: {len(rescoped)}")
    for rel, cls, frag, have, want in rescoped[:40]:
        print(f"  - {Path(rel).name}: {cls} #{frag}: {have or 'in'} -> {want or 'in'}")
    verb2 = "turned" if args.write else "point the wrong way"
    print(f"\njump arrows {verb2}: {len(turned)}")
    for rel, was, now, frag in turned:
        print(f"  - {Path(rel).name}: {was} -> {now}  (#{frag})")
    if arrowless:
        print(f"\n{len(arrowless)} jump links have a class that draws NO arrow —")
        print("yours to judge: reclassify, or leave if the class is deliberate.\n")
        for rel, cls, want, frag in arrowless:
            print(f"  - {Path(rel).name}: {cls}, goes {want[4:]}  (#{frag})")

    if not args.write:
        print("\nreport only; re-run with --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
