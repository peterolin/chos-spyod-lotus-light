#!/usr/bin/env python3
"""Generate src/jumps.htm — the Jump Index: every jump link in the book, by page.

    python3 tools/jumps.py            write src/jumps.htm
    python3 tools/jumps.py --check    exit 1 if it would change, or if any
                                      link's words differ from its target's
                                      landmark label (CI)

One row per jump link in the running text (jumpDown / jumpUp / jump; the
TODO stubs too, flagged; repeat braces are not links with words and are left
out). Sorted by the PAGE the jump leads to — the lpn the label carries, with
ཟུར་ཡིག last — so the labels for one destination stand together and can be
read against each other. Each row shows the link exactly as it renders in
the text (same classes, same href, so it is live), then in small type where
it stands and where it lands: prayer and page on both sides, and the target
id. Built for the label review of 2026-09-17 (Peter: "let me review every
single one"); a reader who finds it useful may keep it.

LANDMARKS. A landing jewel may carry a short name — the step of the liturgy
it begins (མཆོད་པ, མཎྜལ, བཤགས་པ, རྗེས་སུ་ཡི་རང, བསྔོ་སྨོན…), taken from the yig
chung that announces it. Every link into a named jewel uses the same name as
its first words, so the reader lands on the word they tapped. Links whose
words differ from their target's label are listed when the page is written,
flagged ≠ on it, and fail --check: since 2026-09-17 the count is zero and
stays there.
"""
import re
import sys
from pathlib import Path

RAIL_OPEN = re.compile(r'<div class="rail (hue-\w+ pat-\w+)"')

RAIL_CLOSE = re.compile(r"</div>\n</div>\n</div>")


def rail_at(text, pos):
    """The rail classes in force at pos. A heading stands between two rails;
    it belongs to the one that follows it."""
    opens = [(m.start(), m.group(1)) for m in RAIL_OPEN.finditer(text)]
    closes = [m.start() for m in RAIL_CLOSE.finditer(text)]
    last_open = max((o for o in opens if o[0] < pos), default=None)
    last_close = max((c for c in closes if c < pos), default=-1)
    if last_open and last_open[0] > last_close:
        return last_open[1]
    nxt = min((o for o in opens if o[0] >= pos), default=None)
    return nxt[1] if nxt else ""

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import nav  # noqa: E402

SRC = HERE.parent / "src"
OUT = SRC / "jumps.htm"
JUMP = re.compile(r'<a class="(jump|jumpUp|jumpDown|jumpTODO)( out)?"([^>]*)>(.*?)</a>', re.S)
HREF = re.compile(r'\bhref="([^"]*)"')
LPN = re.compile(r'<span class="lpn">([^<]*)</span>')


def prayer_at(sections, rel, offset):
    secs = [s for s in sections if s["file"] == rel and s["start"] <= offset]
    return (secs[-1]["title"], secs[-1]["page"]) if secs else ("", "")


def collect():
    files = nav.spine_order()
    sections, per_file = nav.collect(files)
    pos = nav.id_positions(files)
    rows = []
    for rel in files:
        if not rel.startswith("OPS/") or rel not in per_file:
            continue
        text = per_file[rel][0]
        for m in JUMP.finditer(text):
            cls, out, attrs, inner = m.group(1), m.group(2) or "", m.group(3), m.group(4)
            h = HREF.search(attrs)
            href = h.group(1) if h else ""
            lpn = LPN.search(inner)
            page = lpn.group(1).strip() if lpn else ""
            words = " ".join(re.sub(r"<[^>]+>", "", LPN.sub("", inner)).split())
            frm = prayer_at(sections, rel, m.start())
            trel, frag = rel, ""
            if href and not href.startswith(("http", "mailto")):
                tf, _, frag = href.partition("#")
                if tf:
                    trel = "OPS/" + tf.split("/")[-1]
            tp = pos.get((trel, frag))
            to = prayer_at(sections, trel, tp[1]) if tp else ("", "")
            # the target jewel's label, if it has one: link words should equal it
            target_label = ""
            if tp:
                ttext = per_file[trel][0]
                # id_positions points at the id attribute; back up to the tag's '<'
                start = ttext.rfind("<", 0, tp[1])
                lm = re.match(r'<span id="[^"]+" class="(?:inlineAnchor|inlineAnchorReturn|repeatAnchor)">([^<]*)</span>', ttext[start:])
                if lm:
                    target_label = lm.group(1).strip()
            mismatch = bool(target_label) and words.split(" ")[0].rstrip("།་") != target_label.rstrip("།་") and cls != "jumpTODO"
            rail_from = rail_at(text, m.start())
            rail_to = rail_at(per_file[trel][0], tp[1]) if tp else ""
            same_rail = bool(rail_to) and rail_from == rail_to and trel != rel and cls != "jumpTODO"
            rows.append(dict(file=rel, cls=cls, out=out, href=href, inner=inner, words=words, page=page,
                             frm=frm, to=to, frag=frag, todo=(cls == "jumpTODO"), target_label=target_label, mismatch=mismatch,
                             rail_from=rail_from, rail_to=rail_to, same_rail=same_rail))
    def key(r):
        p = r["page"]
        return (2, 0, r["words"]) if p == "ཟུར་ཡིག" else ((1, 0, r["words"]) if not p.isdigit() else (0, int(p), r["words"]))
    rows.sort(key=key)
    return rows


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;")


def render(rows):
    lines = []
    for r in rows:
        href = r["href"]
        # live link from the index page: hrefs in the text are relative to OPS/
        if href and not href.startswith(("http", "mailto", "#")):
            href = "OPS/" + href.split("/")[-1]
        elif href.startswith("#"):
            href = r["file"] + href
        attrs = f' href="{href}"' if href else ""
        link = f'<a class="{r["cls"]}{r["out"]}"{attrs}>{r["inner"]}</a>'
        frm = f'{esc(r["frm"][0])} {r["frm"][1]}'.strip()
        to = f'{esc(r["to"][0])} {r["to"][1]}'.strip() or "?"
        flag = ' <span class="flag">TODO</span>' if r["todo"] else ""
        if r["mismatch"]:
            flag += f' <span class="flag">≠ {esc(r["target_label"])}</span>'   # words differ from the landmark
        lines.append(f'<p class="jumprow">{link}{flag}<br/><span class="jumpmeta">from {frm} · to {to} · <span class="id">#{esc(r["frag"])}</span></span></p>')
    return f'''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>Jump Index</title>
  <link type="text/css" rel="stylesheet" href="stylesheet.css"/>
  <script type="text/javascript" src="toggle.js"></script>
</head>
<body class="calibreBody">
<!-- GENERATED by tools/jumps.py — do not edit; re-run the tool. -->
<h1 class="jewelstitle">Jump Index</h1>
<p class="jewelsintro">Every jump link in the book, exactly as it stands in the text, in the order of the page it leads to. Under each: the prayer it stands in, the prayer it lands in, and the landing point's id. Tap a link to go there.</p>
{chr(10).join(lines)}
</body>
</html>
'''


def report_same_rail(rows):
    """Jumps whose target sits in a rail identical to the one they leave —
    a report for the editor; the reader sees no change at the edge there."""
    bad = []
    for r in rows:
        if not r["same_rail"]:
            continue
        a, b = str(r["frm"][0] if isinstance(r["frm"], tuple) else r["frm"]).strip(), str(r["to"][0] if isinstance(r["to"], tuple) else r["to"]).strip()
        print(f"    {r['file'].split('/')[-1]:14} “{r['words']}” {a} → {b}  both {r['rail_from']}")
        bad.append(r)
    return len(bad)


def report_mismatches(rows):
    mism = [r for r in rows if r["mismatch"]]
    for r in mism:
        print(f"    {r['file'].split('/')[-1]:14} “{r['words']}” → label “{r['target_label']}”  #{r['frag']}")
    return len(mism)


def main(argv):
    rows = collect()
    new = render(rows)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if "--check" in argv:
        print("jumps.htm up to date" if new == old else "jumps.htm would change")
        n = report_mismatches(rows)
        print(f"{n} links whose words differ from the target's landmark label")
        s = report_same_rail(rows)
        print(f"{s} jumps that land in the same rail they left (reported, not a gate)")
        return 0 if new == old and n == 0 else 1
    OUT.write_text(new, encoding="utf-8")
    print(f"wrote {OUT.name}: {len(rows)} jumps; {sum(1 for r in rows if r['mismatch'])} whose words differ from the target's landmark label")
    report_mismatches(rows)
    print(f"{report_same_rail(rows)} jumps that land in the same rail they left (reported, not a gate)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
