# How this book is edited

## ⚠️ Do not edit the book in Calibre any more

The Calibre **editor** ("Edit book") is no longer part of this project.

Editing there rewrites the whole `.epub` as one 4 MB binary blob. Git can't
diff a blob, reviewers can't read it, Claude can't check it, and every change
— a fixed anchor, a lost prayer, an accidental deletion — looks exactly the
same in the history: `Binary files differ`. Twenty commits of this project's
history are already opaque for that reason.

Calibre stays installed and stays useful, but **only as a viewer**:

| Use Calibre for | Do NOT use Calibre for |
| --- | --- |
| `ebook-viewer` — reading the built book | "Edit book" / the Tweak EPUB editor |
| Checking how it renders on the shelf | Any change to text, TOC, CSS or links |

A git pre-commit hook blocks commits that modify `calibre/*.epub`, so an
accidental Calibre session can't quietly enter the history.

## The actual loop

The source of truth is **`src/`** — the unpacked EPUB, 76 plain files.

```
edit      src/…                        in VSCode, alongside Claude
nav       python3 tools/nav.py         derive prev/next arrows (report only)
check     python3 tools/check.py       structural QA (links, anchors, manifest)
stacks    python3 tools/stacks.py      Tibetan stacks that look like slips
jewels    python3 tools/jewels.py      regenerate the Jewel Jumps page (src/jewels.htm) from every landing jewel; --check to preview
ncx       python3 tools/ncx_playorder.py  renumber playOrder in toc.ncx after adding or moving an entry (--write to apply)
validate  epubcheck build/<file>.epub      the EPUB 2 validator; the tree must stay at 0 errors
preview   tools/preview.sh             builds, then opens the Calibre viewer
build     tools/pack.sh                -> build/Ka-Nying-Chos-spyod-<version>.epub (runs check.py first; --force to build anyway)
commit    git add src/ && git commit    real, readable, line-level diffs
CI        .github/workflows/check.yml  every push: check.py, nav.py (must find nothing), ncx_playorder.py, build, epubcheck
```

`build/` is generated output and is git-ignored. Never edit anything in it;
it is overwritten on every build.

## Why a rebuilt book can look unchanged

Apple Books keys its library on the EPUB's **unique identifier**. Import a
file whose identifier it has already seen and it shows you the *cached* book —
so your CSS edit appears not to have happened. This cost one debugging session
already.

`tools/pack.sh` therefore stamps every build:

| stamp | value | behaviour |
| --- | --- | --- |
| version | `<VERSION>+<build no.>+<hash>` | build no. always increases |
| identifier | a UUID derived from `<base uuid>` + `<hash>` | changes **iff** `src/` changed |

(A suffix on the base UUID, the first design, did not work: Books matched the
UUID-shaped prefix and treated every dev build as one book, opening its oldest
cached copy. Found 2026-09-16 with a fresh-UUID probe.) The hash covers every
filename and byte in `src/`, so the derived UUID is content-derived,
not random: change a file and the identifier moves, so Books imports it fresh;
rebuild unchanged content and it stays put, so the library does not fill with
duplicate copies of an identical book. Revert an edit and the previous
identifier comes back.

`src/` is never touched — the stamp is applied to a staged copy, so `git
status` stays clean across builds. The build string is also written to
`build/version.txt` and into the OPF as `<meta name="build">`.

```bash
tools/pack.sh                 # release build — stable identifier
tools/pack.sh --dev           # dev build — identifier busted per content
tools/pack.sh --plain-title   # leave the version off the title
```

The version is in the filename as well as on the title page:

| | file |
| --- | --- |
| release | `build/Ka-Nying-Chos-spyod-1.1.epub` |
| dev | `build/Ka-Nying-Chos-spyod-1.1+15-dev.epub` — 3 newest kept |

`build/Ka-Nying-Chos-spyod.epub` stays as a symlink to the newest build, so
`preview.sh` and anything else using the old fixed name keeps working.

**The filename is invisible in a library.** Apple Books reads `dc:title` and
`dc:creator` out of the metadata and discards the filename on import, so the
version is appended to the title as well:

| | `dc:title` |
| --- | --- |
| release | `ཆོས་སྤྱོད། (chos spyod) 1.1` |
| dev | `ཆོས་སྤྱོད། (chos spyod) 1.1+22` |

`--plain-title` leaves it off. `src/content.opf` keeps the clean title either
way — like every other stamp, this is applied to the staged copy.

**Ship the release build, never a `--dev` one.** `--dev` deliberately mutates
the identifier to force Apple Books past its cache; to a standards-compliant
reader that makes each build a separate publication rather than an update.
`preview.sh` passes `--dev` for you.

If Books still shows a stale copy, delete the book from the library and
re-add it; the identifier only helps on a fresh import.

## Apple Books' Night theme repaints text colour

Measured with a probe built into the book, not guessed:

| | |
| --- | --- |
| `@media (prefers-color-scheme: dark)` | **fires** — the dark palette is live |
| element text colour | **repainted white**, unstoppably |
| generated content (`:before`/`:after`) | **keeps its author colour** |

Nine techniques were tried on element text and all nine came out white:
`color`, `color !important`, `-webkit-text-fill-color` and its `!important`,
both together, a gradient clipped to the text, and a colour declared only
inside the dark query.

**So no signal may depend on text colour alone.** Anything that must survive
Night belongs in generated content, in a border, or in something that is not
hue at all — size, weight, spacing, a rule. That is why the `༼ ༽` repeat
braces stay red in Night while a prayer title does not, and why the title's
divider rule carries `--accent-rule`: a border survives, so in Night the rule
is the only red still marking a title.

## Layout

```
src/              unpacked EPUB — THE SOURCE OF TRUTH
  content.opf       manifest + spine
  toc.ncx           navigation
  toc1.htm          the visible table of contents
  c_fastjump.htm    quick-jump routes
  stylesheet.css / page_styles.css / fonts.css
  OPS/              53 content documents (c_NN.htm chapters, pNN_…htm merged pages)
  fonts/            Noto Serif Tibetan (OFL, licence beside it), Courier New
  META-INF/

build/            generated .epub (git-ignored)
tools/            pack.sh, unpack.sh, preview.sh, check.py
calibre/          FROZEN pre-split baseline .epub + the Tibetan source PDF
iBooksAuthor/     legacy iBooks Author files
```

## tools/check.py

Structural QA over `src/`. Catches the class of bug this book is most prone
to — navigation that points at nothing:

1. XML well-formedness of all 63 markup documents
2. Manifest ↔ disk consistency (orphan files, missing files)
3. Spine idrefs resolve
4. **Every `href`/`src` target file exists, and every `#fragment` resolves to
   a real `id` in that file**
5. Duplicate ids within a file
6. Media referenced by nobody

Run it before every commit. Exit code is non-zero if there are errors.

**`check.py` has one blind spot worth knowing:** it verifies that a link's
target *exists*, not that it is *meaningful*. A placeholder pointing at
`../pn.htm#todo` resolves, so it passes QA while dead-ending for the reader.
`tools/nav.py` is what catches that class.

## tools/nav.py

Prev/next arrows are not worth typing: the `tocpage1`/`tocpage2` headings,
walked in spine order, already *are* the reading order of the book. `nav.py`
derives each arrow from that order.

```bash
python3 tools/nav.py           # report only — the default
python3 tools/nav.py --write   # apply
```

It is deliberately conservative, and the split matters:

- **It fills** arrows still holding a placeholder (`../pn.htm#todo`, `#TODO`,
  `title="todoprev"`, `#??`), and fixes tooltips that repeat the page number
  twice (`ཇ་མཆོད། 175 175`). Both are mechanically certain.
- **It only reports** anything needing judgement: an arrow whose target
  disagrees with document order, and tooltips whose wording or spelling
  differs from their heading. Many of those differences are Tibetan
  orthography (`མཆོག་གླིངརྣམ` vs `མཆོག་གླིང་རྣམ`, `རྒྱུན་ཀྱི` vs `རྒྱུན་གྱི`) and in
  several the *heading* is the wrong one — so rewriting tooltips from headings
  would spread typos, not fix them. That call is the editor's.

Re-running after `--write` reports nothing to do, so it is safe in a loop.
Add a section anywhere and re-run to wire it into the chain.

### It also audits the jump arrows

An arrow pointing the wrong way is worse than no arrow, and nothing else
catches it: the link still resolves, so `check.py` passes it, and the page
looks fine — you only find out by following it and landing in the wrong place.

`nav.py` measures where each jump link actually goes, from real reading order
(spine index, then position within the document), and compares that with the
direction its class claims. `--write` swaps the class, since the direction is
a fact rather than a judgement. Four live arrows were reversed when this check
was first run.

Two groups are deliberately exempt: `key.xhtml`, whose rows demonstrate each
class *by name*, and `.jumpTODO`, which renders a literal `TODO ` prefix and
should not be dressed up as finished. A class that draws no arrow at all
(`jump`, `easyjump`) is reported, never auto-changed — whether it was chosen
deliberately is a judgement.

## tools/stacks.py

A stack is a base letter with subjoined letters under it — ཕྱ, སྒྲ, དྱ. The book
contains 180 distinct ones across 36,285 occurrences, and almost all of them
recur constantly. The interesting ones occur **once**.

This exists because of `ཏངྱ`. The dhāraṇī in ཆགས་མེད་བདེ་སྨོན། read `ཏ ང ྱ` where
*tadyathā* needs `ཏ ད ྱ` — nga for da, a single letter — and `ངྱ` is not a
stack that Tibetan or Sanskrit writes. Nothing in the toolchain could see it:
the characters are valid Unicode, every link resolved, so `check.py` passed it;
it is not a link, so `nav.py` had nothing to say; and the eye reads straight
through a one-letter slip in the middle of a mantra.

It was caught in Apple Books, which drew a dotted circle over the orphaned
ya-tak — weeks after it was written. Worth knowing: **neither HarfBuzz nor
CoreText reproduces that.** Both ligate `ངྱ` happily through Monlam's GSUB, so
Books is validating the stack itself, and it was the only validator this book
had.

```bash
python3 tools/stacks.py            # report stacks needing review
python3 tools/stacks.py --all      # every stack with its count
python3 tools/stacks.py --accept   # record today's rarities as reviewed
python3 tools/stacks.py --strict   # exit non-zero if any need review
```

Frequency is the signal, and **it is a signal, not a verdict.** Rare stacks are
reported and never changed: `ཀྵྞ` and `རྫྙ` are singletons too, and they are
correct Sanskrit. Judgement stays with you, which is the same division `nav.py`
draws.

Reviewed stacks go in `tools/stacks-known.txt` so the report shrinks to what is
**new**. Read the report before running `--accept` — it accepts everything
outstanding, which would bury the one you were meant to catch.

## Importing an EPUB (rare)

`tools/unpack.sh some.epub` replaces `src/` with that file's contents. It
refuses to run if `src/` has uncommitted changes, so `git diff` always shows
exactly what the import did. You need this only for a legacy or externally
produced EPUB — not as part of normal editing.

## First-time setup on a new machine

```bash
git config core.hooksPath .githooks
```

(Git hooks are not transferred by `clone`; this points git at the tracked
`.githooks/` directory.)
