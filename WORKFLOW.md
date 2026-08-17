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

The source of truth is **`src/`** — the unpacked EPUB, 75 plain files.

```
edit      src/…                        in VSCode, alongside Claude
check     python3 tools/check.py       structural QA (links, anchors, manifest)
preview   tools/preview.sh             builds, then opens the Calibre viewer
build     tools/pack.sh                -> build/Ka-Nying-Chos-spyod.epub
commit    git add src/ && git commit    real, readable, line-level diffs
```

`build/` is generated output and is git-ignored. Never edit anything in it;
it is overwritten on every build.

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
