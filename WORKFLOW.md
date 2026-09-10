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
preview   tools/preview.sh             builds, then opens the Calibre viewer
build     tools/pack.sh                -> build/Ka-Nying-Chos-spyod-<version>.epub
commit    git add src/ && git commit    real, readable, line-level diffs
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
| identifier | `<base uuid>-b<hash>` | changes **iff** `src/` changed |

The hash covers every filename and byte in `src/`, so it is content-derived,
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

The version is in the filename as well as on both title pages:

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

## Layout

```
src/              unpacked EPUB — THE SOURCE OF TRUTH
  content.opf       manifest + spine
  toc.ncx           navigation
  toc1.htm          the visible table of contents
  c_fastjump.htm    quick-jump routes
  stylesheet.css / page_styles.css / fonts.css
  OPS/              53 content documents (c_NN.htm chapters, pNN_…htm merged pages)
  fonts/            Monlam Uni OuChan2, Courier New
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
