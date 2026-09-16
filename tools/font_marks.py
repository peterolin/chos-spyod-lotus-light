#!/usr/bin/env python3
"""Reduce the ring marks of Noto Serif Tibetan for the chos spyod e-book.

Noto draws the anusvara ཾ (U+0F7E) as a hollow ring 0.21em across, floating
clear of the head line, and the candrabindu ྃ (U+0F83) with the same ring on
its crescent. The pecha, and every traditional uchen face (Kailasa, Jomolhari),
set a small ring or dot close to the letter. Peter: "the ugliest thing" on
the page, 2026-09-16.

This scales the three ring glyphs about their own GPOS mark anchor, so the
positioning the font was chosen for is untouched, and drops them a little
towards the head line. Everything else in the font is as Google shipped it.

    python3 tools/font_marks.py            # pristine -> src/fonts/NotoSerifTibetan.ttf

Input:  resources/fonts-original/NotoSerifTibetan-2.103-pristine.ttf
Output: src/fonts/NotoSerifTibetan.ttf  (the embedded font)

Licence: SIL OFL 1.1, which permits modification; Noto declares no Reserved
Font Name, so the family name may stay. The version string records the
change, and src/fonts/MODIFICATIONS-NotoSerifTibetan.txt describes it.
"""
import re
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "resources/fonts-original/NotoSerifTibetan-2.103-pristine.ttf"
OUT = ROOT / "src/fonts/NotoSerifTibetan.ttf"

# glyph-name prefix -> (scale about the anchor, shift down in font units)
SCALE = {"uni0F7E": (0.62, -20), "uni0F83": (0.78, -10), "uni0F82": (0.78, -10)}
NOTE = "; anusvara and candrabindu rings reduced for the chos spyod e-book (tools/font_marks.py, 2026-09-16)"


def main():
    f = TTFont(SRC)
    glyf, gs = f["glyf"], f.getGlyphSet()
    targets = [n for n in f.getGlyphOrder() if re.match(r"uni0F7E|uni0F82|uni0F83", n)]
    anchor = {}
    for lk in f["GPOS"].table.LookupList.Lookup:
        for st in lk.SubTable:
            if getattr(st, "LookupType", lk.LookupType) == 4:
                for n in targets:
                    if n in st.MarkCoverage.glyphs:
                        r = st.MarkArray.MarkRecord[st.MarkCoverage.glyphs.index(n)]
                        anchor.setdefault(n, (r.MarkAnchor.XCoordinate, r.MarkAnchor.YCoordinate))
    for n in targets:
        s, dy = SCALE[re.match(r"uni0F8[23]|uni0F7E", n).group(0)]
        ax, ay = anchor[n]
        pen = TTGlyphPen(gs)
        gs[n].draw(TransformPen(pen, (s, 0, 0, s, ax - s * ax, ay - s * ay + dy)))
        glyf[n] = pen.glyph()
        glyf[n].recalcBounds(glyf)
        print(f"{n}: x{s} about ({ax},{ay}), dy {dy} -> y{glyf[n].yMin}..{glyf[n].yMax}")
    for rec in f["name"].names:
        if rec.nameID == 5 and NOTE not in rec.toUnicode():
            rec.string = rec.toUnicode() + NOTE
    f.save(OUT)
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
