#!/usr/bin/env python3
"""Convert the TCC-encoded pecha PDF (TibetanChogyal fonts) to Unicode text.

    python3 tools/pecha2uni.py resources/"cover+karchag+chojod All in One.pdf" \
        > resources/pecha-unicode/pecha-unicode.txt

The PDF's Tibetan is set in Tony Duff's TibetanChogyal family, one of the
Tibetan Computer Company fonts, whose 8-bit "TCC" encoding is the one the
Tibetan Machine fonts use (main font + four Sanskrit sub-fonts Skt1–4). The
glyph table is Jskad's tibwn.ini (THDL, resources/pecha-unicode/tibwn.ini):
column 2 is 'ord,fn' in the Tibetan Machine fonts (fn 1 = main, 2–5 = Skt1–4),
column 11 the Unicode code points. Text is read with PyMuPDF span by span, so
each character keeps its font; the WinAnsi code is recovered by encoding the
character as cp1252, and the five codes WinAnsi leaves undefined come back
from PyMuPDF as U+E010–E014 in order (0x81, 0x8D, 0x8F, 0x90, 0x9D) — the
PUA map below. Every page is written under a '===== PDF page N =====' line.

STATUS 2026-09-18: first pass, judged about 95% by eye on one page. Known
gaps: the Sanskrit sub-font mapping is the Tibetan Machine one and has not
been verified glyph by glyph against TibetanChogyalSkt1–4 (on PDF page 300
the word དྷ་ན་ཀོ་ཤ came out ངྷ — contact sheets of every Skt glyph are the
next step); one Skt3 character (U+E005 from PyMuPDF, 3 occurrences) is
unmapped and printed as ⟦4:?⟧; the pecha's marginal folio words and Latin
page numbers are kept in the stream where they fall.
"""
import sys, unicodedata
import pymupdf

FN = {"TibetanChogyal": 1, "TibetanChogyalSkt1": 2, "TibetanChogyalSkt2": 3,
      "TibetanChogyalSkt3": 4, "TibetanChogyalSkt4": 5}
PUA = {0xE010: 0x81, 0xE011: 0x8D, 0xE012: 0x8F, 0xE013: 0x90, 0xE014: 0x9D,
       0x2212: 0xAD, 0x03BC: 0xB5}      # minus sign for soft hyphen, Greek mu for micro


def load_table(path):
    m = {}
    for line in open(path, encoding="utf-8", errors="replace"):
        if line.startswith("//") or "~" not in line:
            continue
        c = line.rstrip("\n").split("~")
        if len(c) < 11 or not c[1].strip():
            continue
        try:
            o, f = [int(x) for x in c[1].split(",")]
        except ValueError:
            continue
        u = c[10].strip()
        if not u or u == "none":
            continue
        m[(f, o)] = "".join(chr(int(h, 16)) for h in u.split(","))
    return m


def code(ch):
    if ord(ch) in PUA:
        return PUA[ord(ch)]
    try:
        return ch.encode("cp1252")[0]
    except UnicodeEncodeError:
        return None


def convert_page(page, table, unknown):
    out = []
    for b in page.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                fn = FN.get(s["font"].split("+")[-1])
                if fn is None:
                    out.append(s["text"])
                    continue
                for ch in s["text"]:
                    if ch.isspace():
                        out.append(" ")
                        continue
                    o = code(ch)
                    u = table.get((fn, o)) if o is not None else None
                    if u is None:
                        unknown[(fn, o, ch)] = unknown.get((fn, o, ch), 0) + 1
                        out.append(f"⟦{fn}:{o if o is not None else '?'}⟧")
                    else:
                        out.append(u)
            out.append("\n")
    return unicodedata.normalize("NFC", "".join(out))


def main(argv):
    pdf = argv[1]
    table = load_table(argv[2] if len(argv) > 2 else "resources/pecha-unicode/tibwn.ini")
    doc = pymupdf.open(pdf)
    unknown = {}
    for i, page in enumerate(doc):
        sys.stdout.write(f"\n===== PDF page {i + 1} =====\n")
        sys.stdout.write(convert_page(page, table, unknown))
    if unknown:
        print(f"{sum(unknown.values())} unmapped glyph occurrences, {len(unknown)} distinct:", file=sys.stderr)
        for k, v in sorted(unknown.items(), key=lambda kv: -kv[1])[:20]:
            print(f"  font {k[0]} code {k[1]} {k[2]!r} ×{v}", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
