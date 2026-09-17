#!/usr/bin/env python3
"""Reflow the prayer documents so that the source reads like the page.

    python3 tools/fmt.py            rewrite src/OPS/*.htm in place
    python3 tools/fmt.py --check    exit 1 if any file would change (CI)
    python3 tools/fmt.py FILE…      only these files

WHAT IT DOES. The line breaks in these files were the ~120-column wrap of the
EPUB the book was rebuilt from: a line began mid-verse and a closing tag
opened the next one. This tool lays the same markup out so that

  - every heading, comment and <div> stands on its own line with a blank
    line before it;
  - every inline element that is preceded by whitespace — a span, a jump
    link, a jewel — starts a new line; elements glued together with no
    whitespace between them stay glued, because in Tibetan every space is a
    visible gap and the glue is the pecha's own (a size change inside one
    phrase: མཆོད་པར་</span><span class="tibyigchung">བསམ༔);
  - a span whose text opens with ༈, the mark that begins a new text, gets a
    blank line before it;
  - long content wraps at an existing space after about WRAP characters,
    continuation lines indented two spaces;
  - runs of whitespace collapse to one space or one break.

WHAT IT NEVER DOES. It never adds whitespace where there was none and never
removes all whitespace from where there was some. Every change is one run of
ASCII whitespace exchanged for another, and in HTML those render alike: runs
collapse to a single space, and whitespace beside a block boundary is dropped
either way. NO-BREAK SPACE (U+00A0) is not whitespace here and is never
touched. The proof is in --check's twin, `verify()`: the two versions must be
byte-identical once whitespace runs are collapsed and whitespace beside block
tags is stripped, and the tool refuses to write otherwise.

Everything before <body> is left as it is. Run it over all ten files and
commit the result on its own, so that `git blame` on the Tibetan stays useful.
"""
import re
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent / "src"
FILES = sorted(p for p in (SRC / "OPS").glob("*.htm") if p.name != "titlepage.htm")
WRAP = 90      # wrap content at the first existing space past this column
SWITCH = 40    # …or at a register switch once the line is this long

BLOCK_TAGS = ("h1", "h2", "h3", "h4", "h5", "h6", "div", "p", "dl", "dt", "dd", "hr", "ol", "ul", "li", "body", "html")
ASCII_WS = " \t\r\n"   # str.strip() would also eat U+00A0 — never use it bare here
WS = re.compile(r"[ \t\r\n]+")
# Atomic pieces: a comment, a whole heading, any other tag, or a run of text.
TOKEN = re.compile(
    r"<!--.*?-->"                     # comment, whole
    r"|<h[1-6]\b[^>]*>.*?</h[1-6]>"   # heading, whole (short, kept on one line)
    r"|<[^>]+>"                       # any other tag
    r"|[^<]+",                        # text
    re.S,
)


def tag_name(tok):
    m = re.match(r"</?([a-zA-Z][a-zA-Z0-9]*)", tok)
    return m.group(1).lower() if m else ""


def is_block(tok):
    return tok.startswith("<!--") or tag_name(tok) in BLOCK_TAGS


def collapse(s):
    return WS.sub(" ", s)


def normalise(html):
    """The render-equivalence key: whitespace runs collapsed, whitespace beside
    block boundaries and at the ends dropped."""
    s = collapse(html)
    s = re.sub(r" ?(<!--.*?-->) ?", r"\1", s, flags=re.S)
    s = re.sub(r" ?(</?(?:%s)\b[^>]*>) ?" % "|".join(BLOCK_TAGS), r"\1", s)
    return s.strip(ASCII_WS)


def layout(body):
    """body: the text from <body…> to </body> inclusive, whitespace already
    collapsed to single spaces. Returns the laid-out text."""
    toks = TOKEN.findall(body)
    lines = []          # finished lines
    cur = ""            # line being built
    pending_space = False

    def flush():
        nonlocal cur
        if cur.strip(ASCII_WS):
            lines.append(cur.rstrip(ASCII_WS))
        cur = ""

    def blank():
        flush()
        if lines and lines[-1] != "":
            lines.append("")

    def newline(indent=""):
        flush()
        nonlocal cur
        cur = indent

    i = 0
    while i < len(toks):
        tok = toks[i]
        if not tok.startswith("<"):
            # text: split into words on the single spaces; leading/trailing
            # space become pending_space flags around the words.
            lead = tok.startswith(" ")
            trail = tok.endswith(" ")
            words = tok.split(" ")
            words = [w for w in words if w != ""]
            if lead:
                pending_space = True
            for k, w in enumerate(words):
                if k:
                    pending_space = True      # the space that split the words
                if pending_space:
                    if len(cur) >= WRAP and cur.strip(ASCII_WS):
                        newline("  ")
                    elif cur:
                        cur += " "
                    # cur == "" means a line break stands here already
                    pending_space = False
                cur += w
            if trail:
                pending_space = True
            i += 1
            continue

        # a tag (or comment / whole heading)
        if is_block(tok):
            # blank line before a block opener; own line for everything block
            opening = not tok.startswith("</")
            if opening:
                blank()
            else:
                flush()
            lines.append(tok)
            cur = ""
            pending_space = False
            i += 1
            continue

        # inline tag
        closing = tok.startswith("</")
        if closing:
            # Glued to what it closes. A pending space before it is a space
            # inside the element: keep it, or make it the break. When the
            # closing tag is itself glued to the next opener — a register
            # switch inside one run, མཆོད་པར་</span><span …>བསམ༔ — break here
            # once the line has some length, so the switch opens a line and
            # can be seen; it is the only legal break in such a chain.
            glued_on = i + 1 < len(toks) and toks[i + 1].startswith("<") and not toks[i + 1].startswith("</") and not is_block(toks[i + 1])
            if pending_space:
                if cur.strip(ASCII_WS) and (len(cur) >= WRAP or (glued_on and len(cur) >= SWITCH)):
                    newline("  ")
                else:
                    cur += " "
                pending_space = False
            cur += tok
            i += 1
            continue

        # inline opener (or self-closing): own line when whitespace precedes it
        if pending_space:
            starts_text = False
            if i + 1 < len(toks) and not toks[i + 1].startswith("<"):
                nxt = toks[i + 1].lstrip("  ")
                starts_text = nxt.startswith("༈")
            if starts_text or 'class="tibyigchungH"' in tok:
                blank()
            else:
                newline()
            pending_space = False
        cur += tok
        i += 1

    flush()
    # squeeze repeated blank lines and a blank line right after an opener
    out = []
    for ln in lines:
        if ln == "" and (not out or out[-1] == ""):
            continue
        out.append(ln)
    return "\n".join(out).rstrip(ASCII_WS) + "\n"


def format_html(html):
    m = re.search(r"<body\b", html)
    if not m:
        raise SystemExit("no <body>")
    head, body = html[: m.start()], html[m.start():]
    body_c = collapse(body).strip(ASCII_WS)
    new_body = layout(body_c)
    new = head.rstrip("\n") + "\n" + new_body
    verify(html, new)
    return new


def verify(old, new):
    a, b = normalise(old), normalise(new)
    if a != b:
        # locate the first difference for the message
        n = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        raise SystemExit(
            "REFUSING TO WRITE: the reflow would change the rendered document.\n"
            f"  first difference at collapsed offset {n}:\n"
            f"  old: …{a[max(0, n-60):n+60]}…\n"
            f"  new: …{b[max(0, n-60):n+60]}…"
        )


def main(argv):
    check = "--check" in argv
    args = [a for a in argv if not a.startswith("--")]
    files = [Path(a) for a in args] if args else FILES
    changed = []
    for f in files:
        old = f.read_text(encoding="utf-8")
        new = format_html(old)
        if new != old:
            changed.append(f)
            if not check:
                f.write_text(new, encoding="utf-8")
    verb = "would change" if check else "reflowed"
    print(f"{verb}: {len(changed)} of {len(files)} files" + ("" if not changed else " — " + ", ".join(p.name for p in changed)))
    return 1 if (check and changed) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
