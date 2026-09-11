# TODO — adversarial review of the source

The EPUB source read as a software project: what is broken, what is debt, what
is merely inherited from calibre and never questioned. Every item was measured
against the tree, not recalled — counts and file:line references are real and
were produced by the commands in **How this was measured** at the bottom.

Severity is about the reader, not about tidiness:

| | meaning |
|---|---|
| **A** | the reader sees something wrong today |
| **B** | structural debt — nothing visibly broken, but it makes every future change harder |
| **C** | convention and naming — cheap to fix, pays back on every read |
| **D** | tooling and process |
| **E** | recorded, deliberately not being done now |

Items are struck through and marked RESOLVED as they close, with what was
actually done — a closed item often leaves something behind that the rest of
the list needs to know about.

---

## A. The reader sees this today

### A1. ~~`c_fastjump.htm` has no `<head>`~~ — RESOLVED by retiring the page

The Fastjump page had no `<head>` at all: no stylesheet, no font, no title.
Every reading of it was browser defaults, which is why it looked nothing like
the book. Retired 2026-09-11 rather than repaired — rarely used, and fixing it
properly meant a head, valid markup (it was 22 `<ul>` elements holding bare
text with no `<li>`), a layout, and an editorial pass. Out of the manifest,
spine and NCX; the file lives in `retired/` with a note.

**Two traps it left behind, both live:**

1. Those 22 entries were the only inbound links to roughly twenty anchors —
   `TOC_KunzangDorjeChang`, `TOC_37Mandala`, `TOC_Mahakala`, `TN_Tsog` and the
   rest. They are now anchors nothing links to, which is exactly what **B7**
   says to delete. **Do not.** The curated list is the valuable part of that
   page; a future Fastjump needs those anchors to exist.
2. `pack.sh` copies all of `src/` into the book *regardless of the manifest*,
   so the retired file still shipped as an unreferenced resource until it was
   moved out of `src/`. See **D5**.

### A2. Six documents link `stylesheet.css` but not `fonts.css`

```
src/OPS/c_87.htm   src/OPS/c_91.htm   src/OPS/p362.htm
src/OPS/titlepage.htm   src/pn.htm   src/repeats.htm
```

`@font-face` lives only in `fonts.css`. These six ask for
`font-family: Monlam Uni OuChan2` and are handed whatever the reading system
substitutes. On a device where Monlam is not installed — which is most
devices — they are set in a different typeface from the rest of the book.

**Fix:** add the `fonts.css` link. Better: stop having a separate `fonts.css`
at all (see B4).

### A3. Nine spine documents are not in the NCX

```
titlepage.xhtml   OPS/titlepage.htm   acknowledgements.htm   key.xhtml
OPS/p362.htm      OPS/c_87.htm        OPS/c_91.htm
pn.htm            repeats.htm
```

`OPS/p362.htm`, `OPS/c_87.htm` and `OPS/c_91.htm` are real content a reader
would want to reach, and there is no way to navigate to them. These are also
three of the four documents with no `tocpage` heading, and three of the six in
A2 — the same three documents keep turning up, which suggests they were added
to the spine by hand and never finished.

**Fix:** decide for each whether it is content (give it a heading, an NCX
entry, and the missing links) or apparatus (leave it out of the NCX
deliberately, and say so in `WORKFLOW.md`).

### A4. `titlepage.xhtml` declares itself English

```
src/titlepage.xhtml:2   xml:lang="en"
```

It is the Tibetan title page. It is also the only document in the book that
declares a language at all — see E1.

### A5. Seven `???` and 70 `TODO` markers remain in the source

`.jumpTODO` renders a literal `TODO ` prefix to the reader, by design, so 11 of
these are visible in the book. The `???` are `pageno-unknown` placeholders,
hidden from the reader by CSS but still standing work.

**Fix:** work them down. They are tracked; they are not forgotten.

---

## B. Structural debt

### B1. The whole liturgy is inline `<span>`. There are no paragraphs.

```
span  2702        p  20        div  8
```

`.tibnormal` computes to `display: inline` — measured, not assumed. Every verse
in the book is an inline run, so consecutive verses flow together as one
continuous text and separation comes from source newlines collapsing to spaces.

This is arguably right for a pecha, which is continuous text, and it should not
be "fixed" reflexively. But it has costs worth naming:

- there is no paragraph structure for a screen reader to navigate by
- `page-break-inside` and orphan/widow control have nothing to apply to
- every piece of vertical rhythm has to be reconstructed by hand, which is
  exactly the work the unbreakable-heading box had to do

**Decide deliberately**, and write the decision down. If it stays, it stays for
a stated reason.

### B2. `-webkit-text-fill-color` is declared 21 times and the PLATFORM NOTE says it does not work

The note at the top of `stylesheet.css` records that
`-webkit-text-fill-color` was tried against Books' Night theme and defeated —
it is one of the nine techniques listed as failing. It is nonetheless still
paired with `color:` on 21 rules.

That is a contradiction a future reader will trip over: either it does
something the note does not credit it with (on some other reading system?), in
which case the note should say so, or it does nothing and should come out.

**Fix:** determine which, then make the code and the comment agree.

### B3. 88 ids are duplicated across documents

Mostly `page<N>` colliding between a content document and `pn.htm`. Ids are
per-document in EPUB so nothing is technically broken, but:

- `pp9` is duplicated between `p88_91_104_115.htm` and
  `p1_4_27_30_34_39_48.htm` — two *content* documents
- `example6b` is in both `p88_91_104_115.htm` and `key.xhtml`

and more practically, `#page543` is ambiguous to a human reading a link and to
any tool that does not track which document it is in. `check.py` already
catches duplicates *within* a document; it does not flag these.

### B4. `fonts.css` is a separate file for no reason

Three stylesheets — `stylesheet.css`, `page_styles.css`, `fonts.css` — and two
of them are tiny. `page_styles.css` is six lines of `@page`. `fonts.css` is two
`@font-face` blocks. Splitting them buys nothing and it is the direct cause of
A2: a document can link one and miss the other.

**Fix:** fold all three into `stylesheet.css`. One link per document, one file
to keep in the manifest, one less way to be half-configured.

### B5. calibre residue in the package metadata

```
src/content.opf:19   <dc:contributor opf:role="bkp">calibre (3.7.0) …
src/content.opf:22   <dc:identifier opf:scheme="calibre">e5eb13dc-…
src/content.opf:23   <meta name="calibre:title_sort" …
src/content.opf:24   <meta name="calibre:timestamp" content="2017-09-28…"/>
src/content.opf:26   <meta name="calibre:author_link_map" …
src/content.opf:20   <dc:date>0101-01-01T00:00:00+00:00</dc:date>
```

`pack.sh` repairs `dc:date` at build time, which means the source carries a
value that is known-wrong and is fixed downstream — the repair belongs in the
source. The rest is a record of which program touched the file in 2017.

### B6. The `<guide>` is calibre debris

```
src/content.opf:169   <reference href="OPS/p1_…htm" title="C2"/>
src/content.opf:170   <reference href="OPS/p1_…htm#page27" title="C3"/>
src/content.opf:171   <reference href="OPS/p1_…htm#page34" title="C5">
```

`C2`, `C3`, `C5` are meaningless. There is also no `type="text"` reference,
which is what a reading system uses to decide where "Start Reading" lands — so
it currently guesses.

### B7. Twenty-nine anchors nothing links to

```
return_from_37_mandala   TOC_ChangchubSemchog   TOC_SashiPochu
TOC_NangdragRigsum       TOC_LEU1               TOC_Torma1
TOC_FrontMandala         TOC_Siddhis            refuge37   know44   …
```

Some are deliberate landing spots for a Fastjump entry that was never written;
some are dead. `return_from_37_mandala` renders a visible `༼࿉༽` target mark
with nothing pointing at it, which tells the reader "you can land here" about a
place no link goes.

**Fix:** for each, either add the link that was intended or delete the anchor.

> **Read A1 first.** About twenty of these lost their only inbound link when
> Fastjump was retired, and they are exactly the ones a future Fastjump needs.
> Deleting them would throw away the curated list that was the point of that
> page. Check an anchor against `retired/c_fastjump.htm` before removing it.

---

## C. Naming and convention

### C1. Five id conventions coexist

```
 732  page<N>            printed page
  66  pp<N>              invisible page marker
  48  TOC_PascalCase
  41  snake_case         namo_rigdzin, rigpa_kadag, bdag_gi_bsod_nams_di_yis_ni
  19  lowercase          zuryig, shabten, fastjump, top
  17  word<N>            leu1, refuge37, know44, example6b
   6  tn_ / TN
```

`page<N>` and `pp<N>` are systematic and fine. The other four are four
different people's habits — and `TOC_` is a lie in most cases, since those
anchors are landing spots, not table-of-contents entries.

**Propose:** `page<N>` and `pp<N>` keep their meaning. Everything else becomes
one scheme, ideally one that says what the id *is* — `jump-<slug>` for a
landing spot, `sec-<slug>` for a section. Mechanical, and `nav.py` +
`check.py` can verify nothing broke.

### C2. Class naming is four styles at once

```
camelCase   inlineAnchor  jumpDown  repeatNextOcc  tibyigchungH
lowercase   tibnormal  tibyigchung  pageno  caption  colophon
kebab       pageno-unknown
snake       margin_eh2_ee
```

`tibnormal` and `tibyigchung` are the two most-used classes in the book and
they are the ones that do not follow the dominant camelCase.

### C3. Classes whose names say nothing

```
lh   st   just   wrap   eh2   line191   count237   invisiblec   ipnpx   ppnp
```

`line191` and `count237` are named after a line number and a count that were
true once. `ipnpx` and `ppnp` are used 16 and 4 times respectively and are
load-bearing — `ipnpx` hides the 65 invisible page markers — but nothing in
the name or the stylesheet says so.

**Fix:** rename to what they do. `ipnpx` → `pageMarker`, `ppnp` → whatever it
actually is. Each rename is a mechanical find-and-replace verifiable by
`check.py` and a diff of the built HTML.

### C4. Four classes used with no rule, seven rules with no element

```
used, undeclared:   eh2   just   line191   margin_eh2_ee
declared, unused:   jumpTodO  nextlink  pagenumber  pn  pnh  prevlink  unit
```

Both halves are dead weight. `jumpTodO` is worse than dead — it differs from
`jumpTODO` only in case, and a reading system that matches classes
case-insensitively will apply one rule to the other. That already bit once
(commit `3df8d67`), and it will bite again while the selector exists.

### C5. File naming is two schemes

```
c_53.htm … c_107.htm                      sequence number, meaning nothing
p219_220_247.htm                          printed pages, no title
p334_thugs_sgrub_brgyud_debs.htm          printed pages + Wylie title
p418_.htm  p378_.htm                      trailing underscore, no title
c_extra.htm  c_fastjump.htm  c_60_468.htm
```

A `p*` name lists the printed pages the document covers, which is genuinely
useful. A `c_*` name is a calibre sequence number and tells you nothing — you
cannot find the ཆགས་མེད་བདེ་སྨོན། file without grepping. The trailing underscore
in `p418_.htm` and `p378_.htm` is a truncated title that was never finished.

**Propose:** `p<pages>_<wylie-title>.htm` throughout, which the better half of
the tree already uses. Renames touch the OPF, the NCX and every cross-document
link, so this wants a script and one commit.

---

## D. Tooling and process

### D1. No tests, no CI

```
tools/check.py   264 lines
tools/nav.py     386 lines
tools/pack.sh    266 lines
tools/preview.sh  14 lines
tools/unpack.sh   30 lines
```

960 lines of tooling, no test for any of it, no CI. `nav.py --write` rewrites
123+ links across 40 files in one run; its only safety net is that the tree is
in git. The `link_to` bug fixed in `1a1ddac` had been latent since the tool was
written and was only found because a new section happened to link across a
directory — a fixture with one document in `OPS/` and one at the root would
have caught it on day one.

**Fix:** a `tests/` directory with a small fixture book and a handful of
round-trip assertions. `check.py` on a known-bad fixture should report exactly
the expected errors; `nav.py --write` on a known fixture should produce a known
output.

### D2. `check.py` cannot see meaning, and that boundary is not written down

A link to `#todo` resolves, so `check.py` passes it. `nav.py` exists because of
this. The division is real and sound — `nav.py` decides what a link should
point *at*, `check.py` decides whether the path *resolves* — but it is recorded
only in a commit message.

**Fix:** state it at the top of both tools.

### D3. The build cannot fail on a bad tree

`pack.sh` uses `set -euo pipefail` and traps its staging directory, which is
good. But it does not run `check.py`, so a build with dangling links succeeds
silently.

**Fix:** `pack.sh` runs `check.py` first and refuses to build on errors, with
an explicit `--force` for when you know better.

### D4. No check for what only a reader can see

The dotted circle in `ཏངྱ` was found by eye, in Books, weeks after it was
written. The character sequence was valid Unicode and resolved fine, so no tool
had anything to say about it.

**Fix:** a stack checker. Enumerate every base+subjoined cluster in the book —
there are 180 distinct ones — and flag the rare ones for review. A sweep of the
singletons already turns up `ངྣདྨངྒྱཌྒྱ` in `p88_91_104_115.htm:25`, sitting where
an opening line should be, which looks like a second encoding accident of the
same family. **This one is worth doing next.**

### D5. `pack.sh` ships every file in `src/`, manifest or not

```
tools/pack.sh:107   cp -R "$SRC"/. "$STAGE"/
```

The build copies the whole tree and never consults the manifest. Any stray
file in `src/` — a retired document, a scratch copy, an editor backup — is
published inside the EPUB as a resource no manifest entry references. This was
found by retiring Fastjump: removing it from the manifest and spine did not
stop it shipping.

**Fix:** `pack.sh` stages only files the manifest lists (plus `mimetype` and
`META-INF/`), and fails loudly on a `src/` file that is not manifested — that
second half is the part that catches the mistake rather than hiding it.

### D6. `nav.py` fills arrows but never adds a missing one

Fifteen `tocpage` headings carry no `<a class="left">` or `<a class="right">`
at all, so they are simply outside the navigation:

```
c_80.htm page558     c_81.htm page578      c_82.htm page581
c_95.htm kun_bzang_rdo_rje_chang           c_95.htm dbud_bzhi_las_rgyal
c_101.htm page704    c_106.htm snang_grags_rigs_gsum
c_extra.htm zuryig   c_extra.htm shabten
p133… page142, page148, chos_rnams_thams_cad
p334… page340, tn_om_ah_hung, tn_offerings
```

`nav.py` derives and repairs the arrows in elements that exist; it has no way
to create one. So a heading that was never wired stays unwired forever, and
the tool reports everything as fine.

**Fix:** `--write` inserts the pair when a heading has neither, which makes
"every linkable section is reachable by arrow" an invariant the tool can hold
rather than an accident of which headings someone remembered.

---

## E. Recorded, not being done now

### E1. Language tagging

`dc:language` is `bo`; not one content document declares a language, and the
sole exception is wrong (A4). Costs: VoiceOver reads Tibetan with an English
voice, the OS's language-aware font fallback gets no hint, and Tibetan
line-breaking heuristics get nothing. Fix is mechanical — `xml:lang="bo"
lang="bo"` on the Tibetan documents, `lang="en"` on the English runs.

### E2. The page-list exists, is in the wrong file, and is 7/64 done

Correcting what an earlier draft of this list said. There *is* a page-list —
it is just not reachable by anything:

```
src/toc.ncx:682   <nav epub:type="page-list">   ← EPUB 3 markup inside an NCX
src/toc.ncx:690   ?</ol>                        ← stray character
                  7 <li> entries (pp4–pp10) of 64 available anchors
                  0 <pageTarget> elements, which is what EPUB 2 reads
```

An EPUB 3 `<nav>` cannot live inside `toc.ncx`; a nav document is a separate
XHTML file declared in the manifest with `properties="nav"`, and there isn't
one. So EPUB 2 readers look for `<pageList>` and find nothing, EPUB 3 readers
look for a nav document and find nothing, and this element is dead in both
directions. It also covers pages 4–10 of a ~700-page book.

The underlying opportunity stands, and it is a good one:

```
137  printed page numbers rendered in headings
 64  distinct  id="ppNNN"  anchors already in the content
```

A real page-list is what makes "go to page" follow the *printed* book — for a
text where the umdze calls "page 319", that is the difference between finding
it and scrolling. Decide EPUB 2 `<pageList>` or an EPUB 3 nav document, build
it from the anchors that already exist, and delete the thing in the NCX either
way. Books' support for NCX `pageList` is uneven, so probe before committing.

### E3. Accessibility metadata

No `schema:accessMode`, `accessibilityFeature` or `accessibilitySummary`. Books
will not behave differently; accessibility-aware catalogues read them.

### E4. Two weak alt texts

Six images. Three carry proper Tibetan alt. `page1.jpeg` has `alt="Image"` and
the cover has `alt="cover"`.

### E5. `.pageno` at `0.4em`

Roughly 6–7px at Books' default, and it stays proportionally tiny as the reader
enlarges the text. Invisible to anyone with reduced vision.

### E6. Media overlays

Synchronised read-aloud with the text highlighting in time — transformative for
this book specifically, and EPUB 3 only. The decision to stay on EPUB 2 + NCX
was made deliberately for compatibility. This is the thing that would make you
revisit it, and it is a large piece of work.

### E7. Open editorial questions

- 30 tooltip/heading disagreements — `nav.py` lists them; several are the
  *heading* being the wrong spelling
- 2 arrow mismatches in the `page63` lineage chain, pending a Tibetan heading
- `p319` refrain line counts: `དགོངས་པས` ×11 and `གུས་པས` ×10 where six other
  refrain lines appear ×12
- `ཨོ་སྭསྟི` in three ཞབས་རྟེན། verses where the rest of the book writes `ཨོཾ་སྭསྟི`;
  `བཞེན་དོན` / `ཡོགས་སུ` against Lumbini's `བཞེད་དོན` / `ཡོངས་སུ`
- the swift-return prayer's two verses are in; Düdjom Rinpoche's long
  supplication for CNR is available in Lumbini X.2 and deliberately not included
- `མཎྜལ་༢་རྗེས་སུ། 110` — a label carrying a stray page number

---

## What is already right

Worth stating, so a future pass does not "fix" it:

- **Zero `!important` declarations.** The only occurrence in the tree is inside
  a comment describing a technique that failed.
- **Zero hard-coded colours outside `:root`.** Every colour is a token with a
  light/dark pair and a measured contrast ratio in the comment beside it.
- **Seven inline `style=` attributes in 60 documents**, all of them widths on
  the key-page table and the cover image.
- **No deprecated presentational tags** — no `<font>`, `<center>`, `<b>`,
  `<u>`, `<big>`, `<tt>`.
- `pack.sh` has `set -euo pipefail` and cleans up its staging directory on exit.
- The PLATFORM NOTE records platform behaviour that was *measured with a probe
  in the book*, not guessed, and says which techniques failed. That is the
  single best thing in this codebase and the reason several of the fixes above
  are even possible to reason about.

---

## How this was measured

```bash
# element and class census
python3 - <<'PY'
import glob, re, collections
files = glob.glob('src/OPS/*.htm')+glob.glob('src/*.htm')+glob.glob('src/*.xhtml')
tags = collections.Counter()
for p in files:
    for m in re.finditer(r'<([a-zA-Z][a-zA-Z0-9]*)[\s/>]', open(p,encoding='utf-8').read()):
        tags[m.group(1).lower()] += 1
print(tags.most_common())
PY

# dead CSS both ways
# (defined selectors minus used classes, and the reverse)

# documents missing a stylesheet or the font link
for f in src/OPS/*.htm src/*.htm src/*.xhtml; do
  grep -q "stylesheet.css" "$f" || echo "no stylesheet: $f"
done

# spine documents absent from the NCX
# orphan anchors: every id, minus every href fragment
# computed display/colour: headless Chrome against the built EPUB
```

`.tibnormal` being `display: inline`, the `--jump` contrast ratios, the
`content` string truncation and the `.jumpTodO` case collision were all
measured in headless Chrome against the built book, not read off the source.
