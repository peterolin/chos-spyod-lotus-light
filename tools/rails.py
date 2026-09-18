#!/usr/bin/env python3
"""Wrap every prayer in its rail — the coloured, patterned line down the right
edge of the page that says which text the reader is in (2026-09-18).

    python3 tools/rails.py            rewrite the wrappers in src/OPS/*.htm
    python3 tools/rails.py --check    exit 1 if a file would change (CI)

A section runs from one tocpage1 heading (h1 or h2) to the next, or to the
end of the file's <div class="text">. The HEADING STAYS OUTSIDE: the wrapper
opens right after it and the stylesheet pulls the wrapper up over the title
line, so the rail begins level with the title and the arrow row above it
stays clear. (Build 309 wrapped the heading and pulled it up instead; when a
prayer began at a page top its row landed on the previous page.)

    <h1 class="tocpage1" …>…</h1>
    <div class="rail hue-X pat-Y"><div class="rail-m"><div class="rail-i">
      …text…
    </div></div></div>

The outer and inner divs draw hairlines, the middle one the pattern band —
all borders (plus one background for the hatch), so the rail survives Books'
Night theme and is drawn on every page the section occupies. Hue = family,
pattern = role within it (see stylesheet.css, THE RAILS). The assignment is
the table below; anything not listed is slate bar — a common text.

jumps.py reports the jumps that land in a rail identical to the one they
left — information for the editor, not a gate (Peter, 2026-09-18: "adhering
strictly to the graph is a bit too rigorous").
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import fmt  # noqa: E402 — the output is laid out by fmt.py, so the two tools agree byte for byte
OPS = HERE.parent / "src" / "OPS"
FILES = sorted(OPS.glob("p*.htm")) + [OPS / "zur-yig.htm"]

HUES = ("red", "indigo", "verdigris", "ochre", "slate", "plum")
PATS = ("root", "scaffold", "insert")
# root     — a practice text recited through: two hairlines, a solid band between
# scaffold — what stands around a practice (lineage prayers, supplications,
#            zur 'debs, appendices): two hairlines, nothing between
# insert   — a text other practices jump into (refuge, བཟང་སྤྱོད, confessions,
#            the Tara collection): two hairlines, beads between
DEFAULT = ("slate", "root")

RED_SCAFFOLD = ("page319", "page328", "page330", "page334", "page339", "page340",
                "page60", "page61", "page62", "page64", "page70", "page77", "page84",
                "page257", "page654", "page691",
                "TOC_LamaGyangbo", "TOC_TromeLadrub")
RED_ROOT = ("page88", "page336", "page346", "page357", "page362", "page378", "toc_1", "page395", "toc_3", "page420")
OCHRE_ROOT = ("page133", "page135", "page137", "page142", "page148", "page154", "page157", "page170", "page175", "page177",
              "page546", "page441", "page445", "page468", "page472", "page474", "page477", "page481", "page487",
              "page490", "page494", "page497", "page499", "page502", "page506")
SLATE_INSERT = ("page425", "page571", "page578", "page687")   # the extensive refuge (page4) is slate root: solid against བཟང་སྤྱོད's beads
# plum: aspirations and dedications — the run of སྨོན་ལམ at the end of the book,
# and བཟང་སྤྱོད, the insert most jumped into (Peter, 2026-09-18: a distinct
# scheme for aspirations, so it differs from the refuge and the sems bskyed)
PLUM_ROOT = ("page596", "page603", "page615", "page624", "page630", "page638", "page644", "page645", "page647",
             "page650", "page658", "page662", "page699", "page701", "page702", "page704", "page710", "page713",
             "page716", "page723", "page735", "page744", "page695", "TOC_NgowaMonlam")
PLUM_INSERT = ("page581",)   # བཟང་སྤྱོད alone wears plum beads — colour AND pattern its own (Peter, build 311)
SLATE_SCAFFOLD = ("page557", "shabten")   # བཀྲ་ཤིས་བརྒྱད་པ (page30) is root (Peter, build 312)

RAIL = {
    **{k: ("red", "scaffold") for k in RED_SCAFFOLD},
    **{k: ("red", "root") for k in RED_ROOT},
    "page92": ("indigo", "root"), "page431": ("indigo", "root"),
    "page430": ("indigo", "scaffold"), "page483": ("indigo", "scaffold"), "TOC_PhurpaDuDang": ("indigo", "scaffold"),
    "p104": ("verdigris", "root"), "page115": ("verdigris", "insert"),
    **{k: ("ochre", "root") for k in OCHRE_ROOT},
    "page418": ("ochre", "scaffold"),
    **{k: ("slate", "insert") for k in SLATE_INSERT},
    **{k: ("slate", "scaffold") for k in SLATE_SCAFFOLD},
    **{k: ("plum", "root") for k in PLUM_ROOT},
    **{k: ("plum", "insert") for k in PLUM_INSERT},
}

HEAD = re.compile(r'^<h[12] class="tocpage1"[^>]*\bid="([^"]+)"')
OPEN = re.compile(r'^<div class="rail(-m|-i)?\b')


def strip(lines):
    """Remove existing rail wrappers, whatever their layout, and collapse the
    blank lines that leaves behind."""
    out, stack = [], []
    for ln in lines:
        if OPEN.match(ln):
            stack.append("rail"); continue
        if ln.strip() == "</div></div></div>" and stack and stack[-1] == "rail":
            stack.pop(); continue
        if ln.strip() == "</div>" and stack and stack[-1] == "rail":
            stack.pop(); continue
        if "<div" in ln and "</div>" not in ln:
            stack.append("other")
        elif ln.strip() == "</div>" and stack:
            stack.pop()
        if ln.strip() == "" and out and out[-1].strip() == "":
            continue
        out.append(ln)
    return out


def wrap(lines):
    heads = [i for i, ln in enumerate(lines) if HEAD.match(ln)]
    end = max(i for i, ln in enumerate(lines) if ln.strip() == "</div>")   # the .text div
    out, i = [], 0
    for n, h in enumerate(heads):
        stop = heads[n + 1] if n + 1 < len(heads) else end
        hid = HEAD.match(lines[h]).group(1)
        hue, pat = RAIL.get(hid, DEFAULT)
        assert hue in HUES and pat in PATS, hid
        out.extend(lines[i:h + 1])
        out.append(f'<div class="rail hue-{hue} pat-{pat}">\n\n<div class="rail-m">\n\n<div class="rail-i">\n')
        # keep the blank line before the next heading outside the wrapper
        body = lines[h + 1:stop]
        while body and body[-1].strip() == "":
            body.pop()
        out.extend(body)
        out.append("</div>\n</div>\n</div>")
        out.append("")
        i = stop
        while i < len(lines) and lines[i].strip() == "" and i < (heads[n + 1] if n + 1 < len(heads) else end):
            i += 1
    out.extend(lines[i:])
    return out


def main(argv):
    check = "--check" in argv
    changed = []
    for f in FILES:
        old = f.read_text(encoding="utf-8")
        new = fmt.format_html("\n".join(wrap(strip(old.split("\n")))))
        if new != old:
            changed.append(f.name)
            if not check:
                f.write_text(new, encoding="utf-8")
    unused = set(RAIL) - {HEAD.match(ln).group(1) for f in FILES for ln in f.read_text(encoding="utf-8").split("\n") if HEAD.match(ln)}
    if unused:
        print("rails.py: ids in RAIL with no heading:", ", ".join(sorted(unused)))
        return 1
    print(("would change" if check else "rewrote") + f" {len(changed)} of {len(FILES)} files" + (" — " + ", ".join(changed) if changed else ""))
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
