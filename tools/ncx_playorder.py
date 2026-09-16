#!/usr/bin/env python3
"""Renumber playOrder in src/toc.ncx.

EPUB 2 wants playOrder to be a sequence with no gaps, in document order, and
two entries that point at the SAME target must carry the SAME number (the
ཟུར་ཡིག divider and the ཟུར་ཡིག entry do). A naive 1,2,3… renumbering breaks
the second rule; giving the pair one number then breaks the first. This does
both: walks the navPoints in order, bumps the counter only when the target
changes. Report-only unless --write.

Usage:  python3 tools/ncx_playorder.py [--write]
"""
import re, sys
from pathlib import Path

NCX = Path(__file__).resolve().parent.parent / "src" / "toc.ncx"
POINT = re.compile(r'(<navPoint\b[^>]*\bplayOrder=")(\d+)(".*?<content src=")([^"]+)(")', re.S)

def renumber(text):
    n = 0; last = None; out = []
    def sub(m):
        nonlocal n, last
        if m.group(4) != last:
            n += 1; last = m.group(4)
        if int(m.group(2)) != n:
            out.append((m.group(2), n, m.group(4)))
        return f"{m.group(1)}{n}{m.group(3)}{m.group(4)}{m.group(5)}"
    return POINT.sub(sub, text), out

def main():
    text = NCX.read_text(encoding="utf-8")
    new, changed = renumber(text)
    print(f"{len(POINT.findall(text))} navPoints; {len(changed)} playOrder values to change")
    for old, n, src in changed[:20]:
        print(f"  {old} -> {n}  {src}")
    if "--write" in sys.argv and changed:
        NCX.write_text(new, encoding="utf-8"); print("written")
    elif changed:
        print("report only; re-run with --write to apply")

if __name__ == "__main__":
    main()
