#!/usr/bin/env python3
"""Surface Tibetan stacks that look like typing accidents.

A stack is a base letter with one or more subjoined letters under it —
ཕྱ, སྒྲ, དྱ. The source of this book contains 180-odd distinct ones, and the
overwhelming majority occur dozens or hundreds of times. The interesting ones
are the stacks that occur ONCE.

This exists because of ཏངྱ. The dhāraṇī in ཆགས་མེད་བདེ་སྨོན། read ཏ ང ྱ where
tadyathā needs ཏ ད ྱ — nga for da, one letter — and ངྱ is not a stack Tibetan
or Sanskrit writes. Nothing could catch it:

  check.py     the characters are valid Unicode and every link resolved
  nav.py       it is not a link
  a reading    the eye reads through a one-letter slip in a mantra

It was found in Apple Books, which drew a dotted circle over the orphaned
ya-tak, weeks after it was written. Neither HarfBuzz nor CoreText reproduces
that — both ligate ངྱ happily through Monlam's GSUB — so the dotted circle is
Books validating the stack itself, and it is the only validator the book had.

Frequency is the signal this tool uses instead, and it is a good one: a
one-letter slip almost always produces a stack that appears nowhere else,
while every real stack in a liturgy recurs. It is a SIGNAL, not a verdict.
Rare stacks are reported, never changed — ཀྵྞ and རྫྙ are singletons too, and
they are correct Sanskrit.

    python3 tools/stacks.py            report stacks needing review
    python3 tools/stacks.py --all      every stack with its count
    python3 tools/stacks.py --accept   record today's rarities as reviewed
    python3 tools/stacks.py --strict   exit non-zero if any need review

Reviewed stacks live in tools/stacks-known.txt, one per line, so the report
shrinks to what is NEW. Run --accept only after reading the report.
"""

import argparse
import collections
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
KNOWN = Path(__file__).resolve().parent / "stacks-known.txt"

# Tibetan base letters and the subjoined forms that sit under them.
BASE = r"ཀ-ཬ"
SUBJOINED = r"ྐ-ྼ"
STACK = re.compile(f"[{BASE}][{SUBJOINED}]+")

# Everything that is not the Tibetan text: tags, entities, CSS-escaped marks.
TAG = re.compile(r"<[^>]+>")
ENTITY = re.compile(r"&#?\w+;")
COMMENT = re.compile(r"<!--.*?-->", re.S)

# How many occurrences still counts as "rare enough to look at".
RARE = 2


def documents():
    """Every markup document in src/, in a stable order."""
    return sorted(
        p for p in SRC.rglob("*")
        if p.suffix in (".htm", ".html", ".xhtml") and p.is_file()
    )


def blank(match):
    """Same length, same newlines, no content.

    Blanking markup with plain spaces is not enough: a tag or a comment that
    spans lines would take its newlines with it, and every line number after
    it in the file would be reported low. Newlines are kept, everything else
    becomes a space, so a match position still maps to the line it is really
    on — a report that points at the wrong line is worse than no line at all.
    """
    return re.sub(r"[^\n]", " ", match.group(0))


def text_of(path):
    """The document's Tibetan text, with markup blanked and offsets kept."""
    raw = path.read_text(encoding="utf-8")
    raw = COMMENT.sub(blank, raw)
    raw = TAG.sub(blank, raw)
    raw = ENTITY.sub(blank, raw)
    return raw


def collect():
    """Every stack in the book: counts, and where each one occurs."""
    counts = collections.Counter()
    where = collections.defaultdict(list)
    for path in documents():
        text = text_of(path)
        rel = path.relative_to(ROOT)
        for m in STACK.finditer(text):
            stack = m.group(0)
            counts[stack] += 1
            if len(where[stack]) < 4:
                line = text.count("\n", 0, m.start()) + 1
                lo = max(0, m.start() - 22)
                context = " ".join(text[lo:m.start() + 24].split())
                where[stack].append((f"{rel}:{line}", context))
    return counts, where


def known():
    if not KNOWN.exists():
        return set()
    return {
        line.split("#")[0].strip()
        for line in KNOWN.read_text(encoding="utf-8").splitlines()
        if line.split("#")[0].strip()
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--all", action="store_true",
                    help="list every stack with its count, commonest first")
    ap.add_argument("--accept", action="store_true",
                    help="record the stacks reported today as reviewed")
    ap.add_argument("--strict", action="store_true",
                    help="exit non-zero if any stack needs review")
    ap.add_argument("--rare", type=int, default=RARE, metavar="N",
                    help=f"treat N occurrences or fewer as rare (default {RARE})")
    args = ap.parse_args()

    counts, where = collect()
    total = sum(counts.values())
    print(f"{len(counts)} distinct stacks, {total} occurrences, "
          f"across {len(documents())} documents\n")

    if args.all:
        for stack, n in counts.most_common():
            print(f"  {n:5}  {stack}")
        return 0

    reviewed = known()
    rare = sorted(
        (s for s, n in counts.items() if n <= args.rare and s not in reviewed),
        key=lambda s: (counts[s], s),
    )

    if not rare:
        skipped = sum(1 for s, n in counts.items()
                      if n <= args.rare and s in reviewed)
        print(f"nothing to review  ({skipped} rare stacks already accepted "
              f"in {KNOWN.name})")
        return 0

    print(f"{len(rare)} stack(s) occurring {args.rare}x or fewer and not yet "
          f"reviewed.\nRare is a SIGNAL, not a verdict — Sanskrit stacks are "
          f"legitimately rare.\n")
    for stack in rare:
        print(f"  {stack}   x{counts[stack]}")
        for place, context in where[stack]:
            print(f"       {place}")
            print(f"       {context}")
        print()

    if args.accept:
        with KNOWN.open("a", encoding="utf-8") as fh:
            for stack in rare:
                fh.write(f"{stack}\n")
        print(f"accepted {len(rare)} stack(s) into {KNOWN.name}")
        return 0

    print(f"After reading these, record the ones that are correct:\n"
          f"    python3 {Path(__file__).relative_to(ROOT)} --accept")
    return 1 if args.strict else 0


if __name__ == "__main__":
    sys.exit(main())
