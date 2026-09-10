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

    python3 tools/nav.py            report only (default)
    python3 tools/nav.py --write    rewrite the placeholders

Run tools/check.py afterwards.
"""

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"

# A section heading that can be linked to: has both tocpageN class and an id.
HEADING = re.compile(
    r'<h[1-6][^>]*\bclass="tocpage[12]"[^>]*\bid="([^"]+)"[^>]*>(.*?)</h[1-6]>'
    r'(?:\s*<span class="pageno">([^<]*)</span>)?',
    re.S,
)

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
            sec = {
                "file": rel,
                "id": m.group(1),
                "title": clean_title(m.group(2)),
                "page": (m.group(3) or "").strip(),
                "start": m.start(),
            }
            found.append(sec)
            sections.append(sec)
        per_file[rel] = (text, found)
    return sections, per_file


def link_to(target, from_file):
    """href for target as seen from from_file (both live in OPS/)."""
    frag = f"#{target['id']}"
    if target["file"] == from_file:
        return frag
    return Path(target["file"]).name + frag


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
    if not args.write:
        print("\nreport only; re-run with --write to apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
