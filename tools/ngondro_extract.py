#!/usr/bin/env python3
"""Split the Ngondro Kunsang Thuktik proof PDF into three verbatim streams.

THE PDF'S SHAPE, measured rather than assumed:

  * Every sheet is A4 landscape (842x595) carrying TWO printed pages stacked
    one above the other.  Printed page = 2*sheet-1 (top) and 2*sheet (bottom);
    all 33 sheets were checked against the folios printed on them and none
    disagreed, so pages 1..66 are exact.
  * The Tibetan is NOT Tibetan Unicode on the page.  It is the 8-bit TCC
    encoding sitting on Latin codepoints, and it is converted here.  The
    embedded fonts are subsetted and the PDF calls them CIDFont+F1..F8, but
    their TrueType name tables survived and say what they really are:

        F1  TibetanChogyal        the main font      tibwn.ini column 1
        F6  TibetanChogyalSkt1    Sanskrit stacks               column 2
        F5  TibetanChogyalSkt2                                  column 3
        F7  TibetanChogyalSkt3                                  column 4
        F2 F3 F4 F8  Times_TCC    the Latin, left alone

    That is the same family the pecha is set in, so this reuses
    tools/pecha2uni.py's table loader and its WinAnsi/PUA recovery rather than
    keeping a second copy of either.
  * Which stream a run of text belongs to is therefore decided by its FONT,
    never by its codepoints:
        F1 F5 F6 F7   the Tibetan
        F2 F3 F4 F8   the Latin -- English, Sanskrit, and the phonetics
    Lines mix the two freely (a Tibetan head mark followed by an English
    sentence), so the decision is made per SPAN, not per line.

NOTHING IS CLEANED.  Spelling, doubled spaces, stray commas and absent
diacritics are all reproduced as they stand: this text exists to be proofread
against the printed book, so a silent correction here would hide the very
thing being looked for.  The PDF's own line breaks are kept, so a line here is
a line on the page.

ONE THING NEEDED CARE, and getting it wrong INVENTS errors that are not in
the book.  A run of text is assigned to a stream by its font -- but the
document sometimes types the space BETWEEN TWO ENGLISH WORDS in the Tibetan
font, at Tibetan size: a 20-point space in CIDFont+F1 sitting between 'hung'
and 'ha'.  Filing that space under Tibetan alone welds the Latin on either
side of it into 'hungha', 'yidamtsik', 'mebhawasarwa' -- misspellings that
exist nowhere but in the extractor.  So WHITESPACE IS SCRIPT-NEUTRAL here and
goes to both streams, though never as the first thing in one, so no line
picks up a leading space it does not have.

There are no bare positioning gaps to worry about: measured across the whole
document, no gap between two non-space characters anywhere exceeds 0.06 em.
Every space you see in the print is a real space character, so an encoded
double space is a real double space -- a typing slip stays visible, and a
phantom one is never created.
"""
import os, re, sys, unicodedata
import pymupdf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pecha2uni

SRC = "resources/Ngöndro Künsang Thuktik 3.pdf for proof DO NOT SHARE.pdf"
OUT = "resources/ngondro-proof"
# PDF font name -> tibwn.ini column, via the real names in the name tables
TIB_FONTS = {"CIDFont+F1": 1, "CIDFont+F6": 2, "CIDFont+F5": 3, "CIDFont+F7": 4}
TABLE = pecha2uni.load_table(
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "..", "resources", "pecha-unicode", "tibwn.ini"))
UNKNOWN = {}
SPLIT_Y    = 350    # the empty band between the two printed pages on a sheet
LEFT_EDGE  = 110    # a line ending before this is the left running head
RIGHT_EDGE = 700    # a line starting after this is the folio

def render(spans):
    """Return (whole line, Tibetan only, Latin only). See the module docstring
    on why whitespace goes to both streams rather than to its font's."""
    out = {"all": [], "tib": [], "lat": []}
    live = {"tib": False, "lat": False}
    for sp in spans:
        where = "tib" if sp["font"] in TIB_FONTS else "lat"
        for ch in sp["chars"]:
            out["all"].append(ch["c"])
            if ch["c"].isspace():
                for k in ("tib", "lat"):
                    if live[k]:
                        out[k].append(ch["c"])
                continue
            glyph = ch["c"] if where == "lat" else tibetan(ch["c"], sp["font"])
            out[where].append(glyph)
            if where == "tib":
                out["all"][-1] = glyph
            live[where] = True
    return tuple(unicodedata.normalize("NFC", "".join(out[k]))
                 for k in ("all", "tib", "lat"))


def tibetan(ch, font):
    """One TCC glyph to Unicode. An unmapped one is shown, never dropped."""
    fn = TIB_FONTS[font]
    o = pecha2uni.code(ch)
    u = TABLE.get((fn, o)) if o is not None else None
    if u is None:
        UNKNOWN[(fn, o, ch)] = UNKNOWN.get((fn, o, ch), 0) + 1
        return "\u27e6%d:%s\u27e7" % (fn, o if o is not None else "?")
    return u

def halves(page):
    """Yield (which, lines) for the top and bottom printed page of a sheet."""
    top, bot = [], []
    for blk in page.get_text("rawdict")["blocks"]:
        for ln in blk.get("lines", []):
            if not render(ln["spans"])[0].strip():
                continue
            (top if ln["bbox"][1] < SPLIT_Y else bot).append(ln)
    return top, bot

def read(lines):
    """Split one printed page into its folio and its body, in reading order."""
    folio, body = None, []
    for ln in sorted(lines, key=lambda l: (round(l["bbox"][1]), l["bbox"][0])):
        x0, x1 = ln["bbox"][0], ln["bbox"][2]
        text, tib, lat = render(ln["spans"])
        if x0 > RIGHT_EDGE:                       # the folio, with or without
            m = re.search(r"(\d+)\s*$", text)     # the running head before it
            if m:
                folio = int(m.group(1))
            continue
        if x1 < LEFT_EDGE:                        # the left running head
            continue
        body.append((text, tib, lat))
    return folio, body

def rule(n):
    return "\n%s  p. %-3d %s\n" % ("─" * 24, n, "─" * 24)

def main():
    doc = pymupdf.open(SRC)
    pages, bad = [], []
    for i, sheet in enumerate(doc, 1):
        for half, lines in zip((2 * i - 1, 2 * i), halves(sheet)):
            folio, body = read(lines)
            if folio is not None and folio != half:
                bad.append((i, half, folio))
            pages.append((half, body))
    if bad:
        print("FOLIO MISMATCH -- stopping rather than writing a wrong page number:")
        for s, exp, got in bad:
            print("   sheet %d: expected p.%d, folio says %d" % (s, exp, got))
        return 1

    head = ("Ngondro Kunsang Thuktik -- %s\nExtracted verbatim from: %s\n"
            "Pages 1-66, two to a sheet. NOTHING IS CORRECTED: spelling, spacing,\n"
            "punctuation and diacritics stand exactly as the PDF has them.\n")
    streams = {
        "ngondro-english.txt":     ("the Latin text (English, Sanskrit, phonetics)", 2),
        "ngondro-tibetan.txt":     ("the Tibetan, converted to Unicode", 1),
        "ngondro-interleaved.txt": ("Tibetan and Latin together, in reading order", 0),
    }
    counts = {}
    # A standing caveat, because these files outlive the conversation that
    # produced them: the PDF's own Tibetan is incomplete.  The title and
    # opening yig chung are absent (they stand on folios 208-209 of the
    # pecha), and there are further gaps elsewhere (Peter, 2026-09-19).
    # What is here is a faithful conversion of what the PDF contains; it is
    # not a complete text, and it should not be used as one.
    GAPS = ("NOTE: the PDF's own Tibetan is INCOMPLETE. The title and opening\n"
            "yig chung are missing (pecha folios 208-209), and there are further\n"
            "gaps elsewhere. What follows is a faithful conversion of what the\n"
            "PDF holds, not a complete text. Do not use it as one.\n")
    for name, (what, idx) in streams.items():
        n = 0
        with open("%s/%s" % (OUT, name), "w", encoding="utf-8") as fh:
            fh.write(head % (what, SRC))
            if idx != 2:
                fh.write("\n" + GAPS)

            for folio, body in pages:
                got = [t[idx] for t in body if t[idx].strip()]
                fh.write(rule(folio))
                for line in got:
                    fh.write(line.rstrip() + "\n")
                n += len(got)
        counts[name] = n
    for name in sorted(counts):
        print("  %-26s %5d lines" % (name, counts[name]))
    if UNKNOWN:
        print("  UNMAPPED TIBETAN GLYPHS: %d occurrences, %d distinct"
              % (sum(UNKNOWN.values()), len(UNKNOWN)))
        for k, v in sorted(UNKNOWN.items(), key=lambda kv: -kv[1])[:15]:
            print("     column %d code %s %r x%d" % (k[0], k[1], k[2], v))
    else:
        print("  every Tibetan glyph mapped")
    print("  pages 1-%d, all folios agreed" % pages[-1][0])
    return 0

if __name__ == "__main__":
    sys.exit(main())
