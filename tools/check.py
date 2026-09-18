#!/usr/bin/env python3
"""Structural QA for the unpacked EPUB in src/.

Checks, in order of how much they actually bite this book:

  1. XML well-formedness of every markup file
  2. Manifest <-> disk consistency (orphan files, missing files)
  3. Spine idrefs resolve
  4. Internal link integrity — every href target file exists, and every
     #fragment resolves to a real id/name in that file
  5. Duplicate ids within a file
  6. Unreferenced media (images/fonts nobody links to)
  7. Tibetan text that cannot be shaped — a vowel sign, subjoined letter or
     other combining mark with nothing to sit on, a halanta or anusvara in
     the middle of a stack, a doubled vowel sign, a tsheg between a letter
     and its vowel. Each one is a dotted circle or a doubled mark on the
     page (25 found on 2026-09-18, all keying slips). When hb-shape
     (HarfBuzz) is installed the text is also shaped with the book's own
     font and any dotted-circle glyph it produces is an error — the ground
     truth the rules approximate.

Usage:  python3 tools/check.py [--quiet]
Exit 0 if no errors (warnings alone do not fail).

Boundary with nav.py: this tool asks only whether a path RESOLVES — the file
exists, the fragment is an id in it. It cannot see meaning: a link to a
wrong-but-existing anchor passes here. What a link SHOULD point at, and
whether the prev/next arrows agree with the book, is nav.py's job.
"""

import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from urllib.parse import unquote, urldefrag

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "src")

MARKUP_EXT = {".htm", ".html", ".xhtml", ".opf", ".ncx", ".xml"}
MEDIA_EXT = {".jpeg", ".jpg", ".png", ".gif", ".svg", ".ttf", ".otf", ".woff", ".woff2"}

errors, warnings = [], []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def rel(path):
    return os.path.relpath(path, SRC)


def all_files():
    out = []
    for root, dirs, names in os.walk(SRC):
        dirs[:] = [d for d in dirs if d != ".git"]
        for n in sorted(names):
            if n == ".DS_Store":
                continue
            out.append(os.path.join(root, n))
    return sorted(out)


# --- 1. well-formedness -----------------------------------------------------

trees = {}  # relpath -> ElementTree root


def parse_all(files):
    for p in files:
        if os.path.splitext(p)[1].lower() not in MARKUP_EXT:
            continue
        try:
            trees[rel(p)] = ET.parse(p).getroot()
        except ET.ParseError as e:
            err(f"{rel(p)}: not well-formed XML — {e}")


# --- helpers ----------------------------------------------------------------

def local(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag


def attr(el, name):
    """Get an attribute ignoring namespace (handles xlink:href etc.)."""
    for k, v in el.attrib.items():
        if local(k) == name:
            return v
    return None


def ids_in(relpath):
    """Set of anchorable names in a document: id=... and legacy name=..."""
    root = trees.get(relpath)
    if root is None:
        return None
    out = set()
    for el in root.iter():
        for key in ("id", "name"):
            v = attr(el, key)
            if v:
                out.add(v)
    return out


def dup_ids(relpath):
    root = trees.get(relpath)
    if root is None:
        return []
    seen = defaultdict(int)
    for el in root.iter():
        v = attr(el, "id")
        if v:
            seen[v] += 1
    return [k for k, n in seen.items() if n > 1]


# --- 2/3. manifest and spine ------------------------------------------------

def check_opf(files):
    root = trees.get("content.opf")
    if root is None:
        err("content.opf missing or unparseable — skipping manifest checks")
        return set()

    manifest = {}  # id -> href (relative to the OPF, i.e. to src/)
    for item in root.iter():
        if local(item.tag) != "item":
            continue
        iid, href = attr(item, "id"), attr(item, "href")
        if iid and href:
            manifest[iid] = unquote(href)

    declared = set()
    for iid, href in manifest.items():
        target = os.path.normpath(os.path.join(SRC, href))
        declared.add(os.path.normpath(href))
        if not os.path.exists(target):
            err(f"content.opf: manifest item '{iid}' -> {href} does not exist on disk")

    on_disk = set()
    for p in files:
        r = os.path.normpath(rel(p))
        if r in ("mimetype", "content.opf") or r.startswith("META-INF"):
            continue
        on_disk.add(r)

    for r in sorted(on_disk - declared):
        warn(f"{r}: on disk but not in the OPF manifest (dead weight, or a missed entry)")

    spine_ids = []
    for el in root.iter():
        if local(el.tag) == "itemref":
            v = attr(el, "idref")
            if v:
                spine_ids.append(v)
    for sid in spine_ids:
        if sid not in manifest:
            err(f"content.opf: spine itemref '{sid}' has no matching manifest item")

    if not spine_ids:
        err("content.opf: spine is empty")

    return declared


# --- 4/5. links -------------------------------------------------------------

LINK_ATTRS = ("href", "src")
# Any href with a URI scheme is external and not ours to check: http(s),
# mailto, tel, sms (the colophon's share links), data, javascript.
SKIP_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", re.I)


def check_links():
    referenced = set()
    for relpath, root in sorted(trees.items()):
        base = os.path.dirname(relpath)

        for d in dup_ids(relpath):
            err(f"{relpath}: duplicate id '{d}' (anchors become ambiguous)")

        for el in root.iter():
            for a in LINK_ATTRS:
                raw = attr(el, a)
                if not raw or SKIP_SCHEME.match(raw):
                    continue
                target, frag = urldefrag(unquote(raw.strip()))

                if not target:  # same-document anchor
                    own = ids_in(relpath)
                    if frag and own is not None and frag not in own:
                        err(f"{relpath}: link '#{frag}' — no such id in this file")
                    continue

                tpath = os.path.normpath(os.path.join(base, target))
                full = os.path.join(SRC, tpath)
                if not os.path.exists(full):
                    err(f"{relpath}: {a}='{raw}' — target file {tpath} does not exist")
                    continue

                referenced.add(tpath)

                if frag:
                    tids = ids_in(tpath)
                    if tids is None:
                        continue  # unparseable; already reported
                    if frag not in tids:
                        err(f"{relpath}: link '{target}#{frag}' — no id '{frag}' in {tpath}")

    return referenced


# --- 6. unreferenced media --------------------------------------------------

def check_media(files, referenced):
    css_refs = set()
    for p in files:
        if os.path.splitext(p)[1].lower() != ".css":
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        base = os.path.dirname(rel(p))
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)['\"]?\s*\)", text):
            u = m.group(1).strip()
            if SKIP_SCHEME.match(u):
                continue
            css_refs.add(os.path.normpath(os.path.join(base, unquote(u))))

    for p in files:
        r = os.path.normpath(rel(p))
        if os.path.splitext(p)[1].lower() not in MEDIA_EXT:
            continue
        if r not in referenced and r not in css_refs:
            size = os.path.getsize(p)
            warn(f"{r}: not referenced by any document or stylesheet ({size // 1024} KB)")


# --- Tibetan shaping ---------------------------------------------------------

TIBETAN_FONT = os.path.join(SRC, "fonts", "MonlamUniOuChan2.ttf")
DOTTED_CIRCLE = 0x25CC
# Characters supplied by the other embedded fonts — not Monlam's to shape.
OTHER_FONTS = "\ue000\u0fd9"

def _is_letter(c):    return "\u0f40" <= c <= "\u0f6c"
def _is_sub(c):       return "\u0f90" <= c <= "\u0fbc"
def _is_vowel(c):     return c in "\u0f71\u0f72\u0f73\u0f74\u0f75\u0f76\u0f77\u0f78\u0f79\u0f7a\u0f7b\u0f7c\u0f7d\u0f80\u0f81"
def _is_mark(c):      return c in "\u0f7e\u0f7f\u0f82\u0f83\u0f84\u0f86\u0f87\u0f18\u0f19\u0f35\u0f37\u0f39\u0fc6"
def _in_stack(c):     return _is_letter(c) or _is_sub(c) or _is_vowel(c) or _is_mark(c) or c == "\u0f01"   # ༁ carries ྃ (gter tsheg)


def tibetan_text(path):
    """The text of a markup file with tags removed, one string per line."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    text = re.sub(r"<[^>]+>", " ", raw)
    return text.translate({ord(c): None for c in OTHER_FONTS}).split("\n")


def check_shaping():
    """Rule 7: sequences no Tibetan shaper can form."""
    shaped_files = []
    for path in all_files():
        if os.path.splitext(path)[1] not in {".htm", ".html", ".xhtml"}:
            continue
        lines = tibetan_text(path)
        for n, ln in enumerate(lines, 1):
            for i, c in enumerate(ln):
                if not ("\u0f00" <= c <= "\u0fff"):
                    continue
                prev = ln[i - 1] if i else ""
                where = f"{rel(path)}:{n}  …{ln[max(0, i - 12):i + 6]}…"
                if (_is_sub(c) or _is_vowel(c) or _is_mark(c)) and c != "\u0f7f" and not _in_stack(prev):
                    err(f"combining mark with nothing to sit on: {where}")
                elif _is_vowel(c) and _is_vowel(prev) and "\u0f71" not in (c, prev):
                    err(f"two vowel signs on one letter: {where}")
                elif _is_vowel(c) and prev in "\u0f84\u0f7e":
                    err(f"vowel after a halanta/anusvara (wrong order in the stack): {where}")
                elif _is_sub(c) and (_is_vowel(prev) or prev == "\u0f84"):
                    err(f"subjoined letter after a vowel or halanta: {where}")
        shaped_files.append(path)

    # Ground truth, when HarfBuzz is at hand: shape with the book's font and
    # look for the dotted circle it inserts for a mark it could not place.
    import shutil, subprocess
    if not shutil.which("hb-shape") or not os.path.exists(TIBETAN_FONT):
        warn("hb-shape not installed — Tibetan text checked by rule only, not shaped with the font")
        return
    try:
        from fontTools.ttLib import TTFont
        tt = TTFont(TIBETAN_FONT)
        gname = tt.getBestCmap().get(DOTTED_CIRCLE)
        dc_id = tt.getGlyphOrder().index(gname) if gname else None
    except Exception as e:  # fontTools missing or font unreadable
        warn(f"could not read {rel(TIBETAN_FONT)} ({e}) — shaping check skipped")
        return
    if dc_id is None:
        return
    import tempfile
    for path in shaped_files:
        lines = tibetan_text(path)
        # one hb-shape per file: --text-file shapes each line separately and
        # prints one result line per input line, so line numbers survive.
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as tf:
            tf.write("\n".join(ln if ln.strip() else "་" for ln in lines))
            tmp = tf.name
        try:
            out = subprocess.run(["hb-shape", "--font-file", TIBETAN_FONT, "--no-glyph-names",
                                  "--no-positions", "--no-clusters", "--text-file", tmp],
                                 capture_output=True, text=True).stdout
        finally:
            os.unlink(tmp)
        results = out.split("\n")
        for n, (ln, res) in enumerate(zip(lines, results), 1):
            ids = [int(x) for x in re.findall(r"\d+", res)]
            if dc_id in ids:
                err(f"dotted circle when shaped with Monlam ({ids.count(dc_id)}): {rel(path)}:{n}  {ln.strip()[:70]}")


# --- main -------------------------------------------------------------------

def main():
    quiet = "--quiet" in sys.argv

    if not os.path.isdir(SRC):
        print("error: no src/ — run tools/unpack.sh first", file=sys.stderr)
        return 2

    files = all_files()
    parse_all(files)
    check_opf(files)
    referenced = check_links()
    check_media(files, referenced)
    check_shaping()

    print(f"checked {len(files)} files ({len(trees)} markup documents) in src/\n")

    if warnings and not quiet:
        print(f"WARNINGS ({len(warnings)})")
        for w in warnings:
            print(f"  ~ {w}")
        print()

    if errors:
        print(f"ERRORS ({len(errors)})")
        for e in errors:
            print(f"  ! {e}")
        return 1

    print("no errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
