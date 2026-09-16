#!/usr/bin/env python3
"""One-time merge of the 54 prayer documents into 10, by the printed book's
sections (Peter, 2026-09-16). Every file boundary forced a page break, and on
a phone a two-line prayer alone on a page wasted the screen; within one file
prayers run on under their red dividers.

Records the grouping and does the whole rewrite: concatenates the text
wrappers, writes new files named by the printed pages they cover, deletes
the old, and rewrites every href (content, toc1.htm, toc.ncx, content.opf
manifest/spine/guide) to the new locations — a link into the same new file
becomes a bare fragment, a file-only link points at the file's first heading.
Ids were verified unique within each group beforehand (no renames needed).
Kept for the record; running it twice does nothing.
"""
import re, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent; SRC = ROOT / "src"; OPS = SRC / "OPS"
GROUPS = [
 ('p004-084.htm',['p1_4_27_30_34_39_48.htm','p60_61_62_64_70_77_84.htm']),
 ('p088-115.htm',['p88_91_104_115.htm']),
 ('p133-214.htm',['p133_135_137_148_154_161_170_175_177_179.htm']),
 ('p219-254.htm',['p219_220_247.htm']),
 ('p257-313.htm',['p257_leu_bdun_ma.htm']),
 ('p319-418.htm',['p319_328_330_bar_chad_lam_sel.htm','p334_thugs_sgrub_brgyud_debs.htm','p362.htm','p378_.htm','p418_.htm']),
 ('p420-534.htm',['c_53.htm','c_56.htm','c_58.htm','c_59.htm','c_60_468.htm','c_64.htm','c_66.htm','c_67.htm','c_68.htm','c_71.htm','c_72.htm','c_73.htm','c_74.htm','c_75.htm','c_76.htm']),
 ('p543-615.htm',['c_77.htm','c_78.htm','c_79.htm','c_80.htm','c_81.htm','c_82.htm','c_83.htm','c_84.htm']),
 ('p624-744.htm',['c_85.htm','c_86.htm','c_87.htm','c_88.htm','c_89.htm','c_90.htm','c_91.htm','c_92.htm','c_93.htm','c_95.htm','c_101.htm','c_102.htm','c_103.htm','c_104.htm','c_105.htm','c_106.htm','c_107.htm']),
 ('zur-yig.htm',['c_extra.htm']),
]
HEAD = re.compile(r'<h[1-6][^>]*\bclass="tocpage[12][^"]*"[^>]*\bid="([^"]+)"[^>]*>(.*?)</h[1-6]>', re.S)
TAGS = re.compile(r'<[^>]+>')

def main():
    old2new = {}; first_id = {}; bodies = {}; titles = {}
    for new, olds in GROUPS:
        if not all((OPS/o).exists() for o in olds):
            print('already merged'); return
        parts = []; page_lo = page_hi = None; ttl = None
        for o in olds:
            s = (OPS/o).read_text(encoding='utf-8')
            m = re.search(r'<div class="text">\n?(.*?)\n?</div>\s*</body>', s, re.S); assert m, o
            parts.append(m.group(1).strip('\n'))
            heads = HEAD.findall(s)
            first_id[o] = heads[0][0] if heads else None
            for hid, inner in heads:
                pg = re.search(r'<span class="pageno">(\d+)</span>', inner)
                if pg:
                    p = int(pg.group(1)); page_lo = p if page_lo is None else min(page_lo, p); page_hi = p if page_hi is None else max(page_hi, p)
                if ttl is None:
                    ttl = ' '.join(TAGS.sub('', re.sub(r'<span class="pageno">.*?</span>', '', inner)).split())
            old2new[o] = new
        titles[new] = (f'{ttl} · {page_lo}–{page_hi}' if page_lo else ttl) or new
        bodies[new] = '\n\n'.join(parts)
    lang = 'bo'
    def rewrite_href(href, in_file):
        # href forms: "X.htm", "X.htm#f", "OPS/X.htm", "OPS/X.htm#f", "#f", external
        m = re.match(r'^(OPS/)?([^/#]+\.htm)(#.*)?$', href)
        if not m or m.group(2) not in old2new: return href
        pre, old, frag = m.group(1) or '', m.group(2), m.group(3) or ''
        new = old2new[old]
        if not frag and first_id.get(old): frag = '#' + first_id[old]
        if in_file == new: return frag or '#' + (first_id.get(old) or '')
        return pre + new + frag
    def rewrite_all(text, in_file):
        return re.sub(r'(href|src)="([^"]+)"', lambda m: f'{m.group(1)}="{rewrite_href(m.group(2), in_file)}"', text)
    # write the new files
    for new, olds in GROUPS:
        body = rewrite_all(bodies[new], new)
        doc = f'''<?xml version='1.0' encoding='utf-8'?>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="{lang}">
<head>
  <title>{titles[new]}</title>
  <link href="../stylesheet.css" rel="stylesheet" type="text/css"/>
  <script type="text/javascript" src="../toggle.js"></script>
</head>

<body class="calibreBody">
<div class="text">
{body}
</div>
</body>
</html>
'''
        (OPS/new).write_text(doc, encoding='utf-8')
        for o in olds: (OPS/o).unlink()
        print(f'{new:14s} <- {len(olds):2d} file(s)  {len(doc.encode())//1024} KB  "{titles[new][:40]}"')
    # root documents
    for f in ['toc1.htm', 'toc.ncx', 'key.xhtml', 'acknowledgements.htm']:
        p = SRC/f; t = p.read_text(encoding='utf-8'); t2 = rewrite_all(t, None)
        if t2 != t: p.write_text(t2, encoding='utf-8')
    # OPF: manifest, spine, guide
    opf = (SRC/'content.opf').read_text(encoding='utf-8')
    item_id = {}
    for m in re.finditer(r'<item (?:href="OPS/([^"]+)" id="([^"]+)"|id="([^"]+)" href="OPS/([^"]+)")[^>]*/>\n?', opf):
        old = m.group(1) or m.group(4); iid = m.group(2) or m.group(3)
        if old in old2new: item_id[old] = iid
    for old, iid in item_id.items():
        opf = re.sub(r'\s*<item (?:href="OPS/%s" id="%s"|id="%s" href="OPS/%s")[^>]*/>' % tuple(map(re.escape, (old, iid, iid, old))), '', opf, count=1)
    new_items = ''.join(f'    <item href="OPS/{new}" id="{new[:-4]}" media-type="application/xhtml+xml"/>\n' for new, _ in GROUPS)
    opf = opf.replace('<item href="OPS/titlepage.htm" id="titlepage" media-type="application/xhtml+xml"/>\n', '<item href="OPS/titlepage.htm" id="titlepage" media-type="application/xhtml+xml"/>\n' + new_items, 1)
    # spine: the first member's itemref becomes the new one; the rest vanish
    first_of = {olds[0]: new for new, olds in GROUPS}
    def spine(m):
        iid = m.group(1); old = next((o for o, i in item_id.items() if i == iid), None)
        if old is None: return m.group(0)
        return f'    <itemref idref="{first_of[old][:-4]}"/>\n' if old in first_of else ''
    opf = re.sub(r'    <itemref idref="([^"]+)"/>\n', spine, opf)
    opf = rewrite_all(opf, None)
    (SRC/'content.opf').write_text(opf, encoding='utf-8')
    # tools that name files
    nav = (ROOT/'tools/nav.py').read_text(encoding='utf-8').replace('SUBTEXT_FILES = {"p257_leu_bdun_ma.htm"}', 'SUBTEXT_FILES = {"p257-313.htm"}')
    (ROOT/'tools/nav.py').write_text(nav, encoding='utf-8')
    cs = ROOT/'tools/compare_source.py'
    if cs.exists():
        t = cs.read_text(encoding='utf-8').replace("'OPS/c_extra.htm'", "'OPS/zur-yig.htm'"); cs.write_text(t, encoding='utf-8')
    print('done')

if __name__ == '__main__':
    main()
