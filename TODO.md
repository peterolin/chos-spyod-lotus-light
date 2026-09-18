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
the list needs to know about. Closed items are moved out of their section to
**Completed** at the end of this file, so the sections above it hold only what
is still open; the ids do not change, and cross-references such as "see B4"
still resolve there.

Since 2026-09-16 the built EPUB validates with epubcheck at 0 errors and 0
warnings, and CI (`.github/workflows/check.yml`) keeps it there. Anything that
breaks that is an A-severity item by definition.

---

## A. The reader sees this today

### A5. `???` and `TODO` markers remain in the source

Inventoried 2026-09-16. Rendered to the reader that day: 42 — 34 `<dd>TODO</dd>`
glosses in the English TOC, 7 `.jumpTODO` links (the class prints a literal
`TODO ` prefix by design), and the hidden `#TODO` jewel listed on the Jewel
Jumps page (G8). Worked down the same day: 30 glosses filled in and 4 links
finished (two into the ཟུར་ཡིག, labelled `ཟུར་ཡིག` in place of a page number since
the supplement has none; one within Thubchok, where the skip over དགེ་བ་འདི་ཡིས is
the intended order; one from the ཟུར་ཡིག back to page 30).

Still standing, and each needs a decision, not just work:

- `toc1.htm` — glosses for 254 གང་སེར་མ།, 474 མ་དག་མ།, 699 ནོར་བུ་ལས་བདེ་བ་ཅན་དུ་སྐྱེ་བའི་སྨོན་ལམ།
  (which ནོར་བུ). Need the texts, not the titles.
- `c_79.htm` བྱིན་རླབས་མཁའ་ལ → `c_80.htm#line76` — a working link missing its
  printed page; c_80 carries no page anchors past 558 to read it from.
  2026-09-17: the link's words now end in a shad, and a visible `pecha:` stub
  stands beside it (p543-615.htm) until Peter reads the page off the pecha.
- `p1_4:314–315` — two `href`-less stubs, "Medium/Long 7 branch in bzang spyod".
  The pecha says རྒྱས་བསྡུས, two grades not three; the extensive one is this
  prayer's own seven branches (pp. 4–27). Replace with one link, or delete.
- `p1_4:51` — the hidden `#TODO` jewel (G8). Delete and regenerate jewels.htm.
- One `???` page placeholder, `p1_4:265`, hidden by `.pageno-unknown`.
- Two HTML comments: `p1_4:312` (the stubs above), `p60:263` (verify against
  the printed text).
- `p088-115.htm` — six `lama:` stubs in the ཟབ་ཏིག་སྒྲོལ་ཆོག (2026-09-17), each a
  visible `.jumpTODO` beside the spot, to be verified with a lama and then
  removed: the added third-round offerings jump; the ཚར་བདུན་རྫོགས return moved
  after the benefits; the jump removed after the dissolution; the
  སྒྲོལ་ཆོག་རྫོགས link's target; the possibly redundant jump after the long
  supplication; the abbreviated ཨོཾ་ཨ་ཀཱ་རོ mantra with no expansion. See commit
  ab32f7b for the reasoning.
- Two jump labels corrected from impossible values to the target heading's page, not verified against the pecha: བཟང་སྤྱོད། ཕྱག་འཚལ་བ་དང་སོགས། 577 (was 263, `p1_4`) and ཕྱི་མཆོད། 346 (was 344, twice, `p334`).

---

## B. Structural debt

### B2. `-webkit-text-fill-color` is declared 21 times and the PLATFORM NOTE says it does not work

The note at the top of `stylesheet.css` records that
`-webkit-text-fill-color` was tried against Books' Night theme and defeated —
it is one of the nine techniques listed as failing. It is nonetheless still
paired with `color:` on 21 rules.

That is a contradiction a future reader will trip over: either it does
something the note does not credit it with (on some other reading system?), in
which case the note should say so, or it does nothing and should come out.

**Fix:** determine which, then make the code and the comment agree.

**Status:** Not done 2026-09-16: needs the device. The PLATFORM NOTE says the declaration does nothing in Books; removing it must be checked on Books, not assumed.

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

**Status:** Not touched 2026-09-16, on purpose: these are landing spots kept for a future Fastjump (A1) or page markers kept by decision (E2). Deleting is the wrong reflex here.

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

**Status:** Not done 2026-09-16: same reason as C7 — a convention to choose first, then a script.

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

### C4. `.invisible` and `.invisibleRepeat` display, and carry an open TODO

```css
.invisible       { display: none;   /* TODO Set to "none" or "inline" */ }
.invisibleRepeat { display: inline; /* TODO Set to "none" or "inline" */ }
```

`.invisibleRepeat` is used 17 times, all in `p257_leu_bdun_ma.htm`, and it
renders — the name says the opposite of what the rule does. Both carry the
same unresolved TODO, which means the decision they record was never made.

Anyone reading `<span class="invisibleRepeat">` in the source will believe
that text does not appear in the book. It does.

**Fix:** make the decision, then either delete the class or rename it to what
it actually does.

**Status:** Not done 2026-09-16: an editorial decision (publish vs edit view). The yig chung switch built 2026-09-16 shows how a reader-facing toggle would work if that is the answer.

---

## D. Tooling and process

---

## E. Recorded, not being done now

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
- ~~2 arrow mismatches in the `page63` lineage chain~~ — resolved 2026-09-15: the heading was a fabricated placeholder ("?? == Lineage prayers == ??") and Peter had it removed; the chain runs 62 → 64
- `p319` refrain line counts: `དགོངས་པས` ×11 and `གུས་པས` ×10 where six other
  refrain lines appear ×12
- `ཨོ་སྭསྟི` in three ཞབས་རྟེན། verses where the rest of the book writes `ཨོཾ་སྭསྟི`;
  `བཞེན་དོན` / `ཡོགས་སུ` against Lumbini's `བཞེད་དོན` / `ཡོངས་སུ`
- the swift-return prayer's two verses are in; Düdjom Rinpoche's long
  supplication for CNR is available in Lumbini X.2 and deliberately not included
- `མཎྜལ་༢་རྗེས་སུ། 110` — a label carrying a stray page number
- Three jump links whose page number is earlier than the heading their target
  sits under, found by the D8 check — impossible, so one of the two is wrong:
  `p334…:141` `སྐུ་གསུམ་བླ་མའི་ལྷ་ཚོགས། 334` → `#TN_KusumLamey` (under 346), and
  `p334…:160`/`:291` `ཨོཾ་ཨཱཿ ཧཱུྃ༔ ཕྱི་མཆོད། 344` → `#TOC_Offerings` (under 346)
- ~~`p257_leu_bdun_ma.htm:468` and `:570`~~ — fixed 2026-09-12, both set to
  match the written-out refrain used elsewhere in the file. **Peter to check
  against the pecha**: 468 had lost the `ལ` after `གནས`, and 570 was a
  `repeatFirstOcc` ending in a `༴` with the tail absent.

### E8. The 33 spaced boundaries in A7's mirror case — space, or a large shad? (low priority)

Peter, 2026-09-16. A7's mirror pass put a space between a yig chung span ending
in ། or ༔ and the large letters following it, 33 places (commit bdbbcb1). A
space may be the wrong answer in some: the shad might belong to the large run
instead. Too picky to settle now; the rows are 13 prayer title lines running
into their first large word, 8 instructions ending in ནི།/ནི༔, and 12 other
instructions. Two look like something else: `c_53:77` is a small span holding
a lone shad (a stray?), `c_76:50` reads as one phrase split across the two
sizes (སྟེང་། then large གཡོན་). Regex to list them again:
`<span class="tibyigchungH?">[^<]*[།༔]</span><span class="tibnormal"> `.

---

## F. Asked for, not yet built

Not findings from the review — work requested since. Kept here so the whole
backlog is in one place.

### F6. Jump links through the refuge sequence: red → white → red → ཆོས་རྣམས་ཐམས་ཅད།

Requested 2026-09-12. Three jumps to build:

1. from the red refuge to the white refuge;
2. from the white refuge onward to the red;
3. from the red to the teaching of `ཆོས་རྣམས་ཐམས་ཅད།` (p154 — already a
   divider after F3, and already a link target from several places; see F1
   for the `ཆོས་རྣམས་ཐམས་ཅད། 154` links that exist).

Build as round trips where the reader comes back, following the four already
in place (dkar sur ↔ dmar sur, ཨེ་མ་ཧོ p378↔p418, མདུན་བསྐྱེད p88, ཐུགས་སྒྲུབ་ refuge
p334). Survey every refuge occurrence first — there are several refuge verses
in the book and the link must anchor on the one Peter means, not the first one
that greps. Confirm the two sections with Peter before wiring them.

### F17. Complete the ལུས་སྦྱིན་བསྡུས་པ practice sequence

Requested 2026-09-18. The chö text on pp. 546–556 is not yet walkable as a
practice: its sequence has gaps where prayers the practice needs are not in
the text, and where the reader is expected to know what to insert. Walk it
through with Peter and, for each gap, either link to the prayer where it
already stands in the book (with a return jewel, following the seven-branch
and sur round trips) or add what is missing. Candidates for what is needed
are refuge and bodhicitta, the seven branches, and the dedication and
aspiration at the end; Peter decides which, and from where. Verify in
practice afterwards and add it to "Verified in practice" below.

### F18. One-handed use on a phone — low priority, next release

Requested 2026-09-18. A reader holding a phone in one hand during practice
reaches only the lower half of the screen with the thumb, and only one edge
comfortably. Look at what that means for this book: jump links and repeat
braces that fall near the top of a page, the arrow row above every title,
the rails on the right edge, and whether the tap targets are large enough
for a thumb. Books' own page-turn zones take the edges, so nothing of ours
should depend on them. Not for this release; note findings here first,
then decide what, if anything, the markup or stylesheet should do.

### F19. The Lantsa title line as text — a future release, 2028 or later

Noted 2026-09-18. The top line of the printed title page is the Sanskrit
title in Lantsa (the Tibetan form of Rañjanā), reproduced today as part of
the photograph of the first folio. Setting it as text would make it crisp at
any size and let it take the reader's ink in Night. Two obstacles, one
moving: Rañjanā is not in Unicode (a block is reserved at U+11500 and the
proposal was still active in late 2025), so no Unicode text can carry it
yet; and the one free font, Nithya Ranjana (SIL OFL,
https://github.com/EkType/Nithya-Ranjana), follows the Newar calligraphic
form rather than the wider Tibetan Lantsa hand, so a reader who knows Lantsa
would see the accent. Revisit when Rañjanā is encoded and a Tibetan-style
Lantsa font exists under a free licence; until then the photograph stands.
The transliteration line beneath it gives the text to set.

### F20. Incipit instructions without a jump — a future release

Surveyed 2026-09-18: every yig chung instruction that names an incipit with
སོགས or ནས ("from X …") was checked for a jump beside it. 46 found; 23 have
one. Of the rest, five need nothing (syllables, a colophon, "a dedication of
your choice"). The remaining 18 fall in three groups; the first is decided, two remain:

1. **The eight offering words, abbreviated ཨརྒྷཾ་ སོགས/ནས … ཤབྡ, nine times** —
   DECIDED 2026-09-18, Peter: **out.** Not to be completed or linked. Every
   practitioner knows them by heart and writing them out only makes the
   text wordy. The ཨ་ཀཱ་རོ mantra is the exception: its two other
   abbreviations, the Tsog on 170 and the protectors' torma on 445, were
   completed in red the same day, in the refrain style of the Tara's on 111
   (Peter: "we need the refrain style for the two shortened occurrences").
2. **Texts that stand elsewhere in the book, link candidates:** the
   Drolchog daily version on 113 (མདུན་གྱི་ནམ་མཁར་ སོགས → the Drolchog's own
   start on 105, whose jewel was removed 2026-09-18; a labelled jewel would
   come back); Könchog Jedren 168 (འདི་བསྒྲུབས་པ་ལས་བྱུང་ ཞེས་སོགས → the verse
   a few lines earlier); the Trinley Nyingpo's closing instruction on 355
   (five incipits: བླ་མ་ཡི་དམ → 468, ཧོཿ རང་གི་ཐུགས་ཀའི, ཕྱི་མཆོད་འདོད་ཡོན →
   the མཆོད་པ། jewel, ངོ་བོ་འོད་གསལ, སྙིང་པོ་བྱང་ཆུབ་སེམས → the prayer's own
   passages); Narak 417 (ཡོན་ཏན་ཕུན་ཚོགས → the kangwa on 400, བླ་མ་ཡི་དམ →
   468); Lüjin 546 (དཔལ་ལྡན་རྩ་བའི་བླ་མ → the verse on 704; part of F17);
   Khorwa Dongtruk 558 (འབྱུང་པོ་གང་དག → the dismissal verse on 135, 157,
   735).
3. **A round trip inside one prayer:** Jampal Tsenjö 179, སྟོང་པའི་ངང་ལས་
   … ཞེས་པ་ནས … གསལ་བར་གྱུར་ ཅེས་པའི་བར་གོང་བཞིན — the prayer's own
   visualisation "as above", a few pages earlier. Build as the seven-branch
   chain is built: a jewel at the start, a jump there, a return jewel after.

The survey is a one-liner to rerun: yig chung spans containing སོགས or
opening with ནས/ཞེས་པ་ནས, with no `class="jump` within 300 characters.

### F21. The Trinley Nyingpo tsog conclusion as a walkable chain — and the same tail for the chö

Requested 2026-09-18 (Peter). After the Trinley Nyingpo's tsog the practice
runs through a fixed sequence of texts that stand scattered through the
book, and the reader should be able to jump through it and back:

1. **བསྐང་བ་གཡུ་ཞལ་མ**, the Turquoise Chamber kangwa, 357 (heading exists).
2. **ཡེ་ཤེས་སྐུ་མཆོག**, the tsog confession — it is the བརྗོད་མེད་དོན་བཤགས, 420,
   whose text opens ཨོཾ། ཡེ་ཤེས་སྐུ་མཆོག་རང་བཞིན་དཀྱིལ་འཁོར་ནི (heading exists; it
   already wears the Trinley Nyingpo's red rail as part of this practice).
3. A link to **བླ་མ་ཡི་དམ**, the torma dedication, 468 (`TOC_LamaYidamStart`).
4. **ཞབས་བརྟན** — the long-life prayers, 543 and the ཟུར་ཡིག's set.
5. The standard "fairly long" **བསྔོ་སྨོན** run: ཕྱོགས་བཅུ་དུས་བཞི་མ 695
   (`TOC_ChokchuDushi`), པདྨ་འོད་དུ་བགྲོད་པའི་སྨོན་ལམ 703, "döme shidang"
   (identify: which text Peter means), རིག་པ་ཀ་དག (`rigpa_kadag`, in the
   aspirations file), དུས་གསུམ་སངས་རྒྱས 327 (`dusum_sangs_rgyas`), and more
   to be listed with Peter.
6. All of it ends with **སྣང་གྲགས་རིག་གསུམ** (`TOC_NangdragRigsum`).

Build it as the seven-branch chain is built: a labelled jewel at each
landing, links whose first words are the jewel's label, a return where the
chain comes back, the rail changing at each hop. The same conclusion, from
the བསྔོ་སྨོན run to སྣང་གྲགས་རིག་གསུམ, closes the chö (F17), so build the tail
once and let both practices link into it. Walk it with Peter first: order,
what is optional, where the returns go. Then verify in practice.

### F9. Adjudicate the variants between the 3rd and 4th printing

Added 2026-09-12. The newer source EPUB (`resources/…ཞལ་འདོན།.epub`, a Pages
export of the **fourth** printing; ours follows the third) has the same 101
texts as ours and nothing we lack. The two differ in about 50 small readings
seen from its side and 34 from ours, all listed with context in
`resources/extracted/comparison-2026-09-12.md` (sections C1, C2), with a
findings summary at the top. Each needs the pecha, not a guess. Two look like
errors on our side (a `ཏུ` for `དུ`, a swapped `ཤོ`/`ཤྭ` in a mantra); one where the
new book is probably wrong appears ten times in the Tārā sadhana. When lifting
text from that EPUB: NFC-normalise (it uses the deprecated precomposed vowel
U+0F75) and expect its ditto marks in place of our `༴` + written-out refrain.
Regenerate the report with the three commands at the top of
`tools/compare_source.py`.

### F12. Split the refuge-and-bodhicitta repeat in the ཐུགས་སྒྲུབ་ཟུར་འདེབས

Peter, 2026-09-15. In the zur 'debs (`p334_thugs_sgrub_brgyud_debs.htm`,
the `repeat5` span under སྐྱབས་སེམས་དང་བགེགས་གཏོར།) the abbreviated ན་མོཿ བདག་དང་
… སོགས་ནས་ … བསྒྲུབ་པར་བགྱི༔ is wrapped as one three-fold repeat. Refuge and
bodhicitta are to be split into two repeats. Needs the pecha for where the
break falls and what each part's count is; the jump to the Trinley Nyingpo
refuge at 346 sits inside the span and must keep working.

---

### F14. Prayer titles on a portrait phone: the arrows leave the title a slot

**DONE 2026-09-17, Peter's design, awaiting the phone look.** Not any of the
three options below. A measured variant (toggle.js deciding per title whether
the arrows fit beside it) was built first and reverted the same day: slow to
render in Books and not reliable. The design that landed: the title always has
the full width, and the arrows stand in one row under it with the page number
between them, `← 137 →`, at every size — on a narrow screen the row just
closes up. Plain flex with `order`; the title text is `<span class="title">`
(135 headings). Options and cautions below kept for the record.


Asked 2026-09-17 (Peter, iPad and phone). The prev/next arrows are absolutely
positioned at `left: 0` / `right: 0`, vertically centred on the heading
(`.tocpage1 > .left/.right`, stylesheet ~713). On a wide screen that is right:
title and arrows share one line. On a phone in portrait the arrows eat both
margins and a long title is squeezed into the slot between them and wraps to
three or four lines, each short.

Wanted: a layout that keeps arrows and title on one horizontal level where
there is room, and gives the title the full width where there is not — the
arrows then flow under the title, or sit above it as a small nav line.

Techniques, in order of robustness in Books' WebKit:

1. **A width media query.** `@media (max-width: 30em)` (or `26em`; measure)
   switches the arrows from `position: absolute` to `position: static;
   display: inline-block` and gives the heading `display: flex; flex-wrap:
   wrap; justify-content: center` with the title text wrapped in a span that
   takes `flex: 1 1 100%` so it sits on its own line and the two arrows drop to
   a line beneath (or, with `order: -1`, above). Media queries fire in Books —
   `prefers-color-scheme` already does. The heading markup has the title as
   bare text between the arrow anchors and the page number; wrapping it in
   `<span class="title">` is a mechanical edit across 128 headings and nav.py
   must keep matching (PRAYER regex is on the `<h1 … id>` tag, unaffected).
2. **Flex without a media query.** Heading as `display: flex; flex-wrap:
   wrap; align-items: baseline`; arrows as flex items with fixed width; title
   span with `flex: 1 1 auto; min-width: 12em`. When the title cannot get its
   minimum beside the arrows it wraps to its own line automatically, no
   breakpoint to tune. Elegant, but `min-width` on Tibetan of varying length
   needs care, and the arrows land under the title, never above.
3. **Arrows above the title everywhere** — one layout for all widths, a small
   nav line `◂ prev · next ▸` over the red title. Simplest and most predictable;
   costs a line of height on every screen, and on the iPad it would look like
   a change for the phone's sake.

Whatever is chosen: keep the arrows in the reader's link colour and at 85%,
keep `nav.py`'s arrow rules untouched (they check hrefs, not layout), and
test on a phone in portrait at the reader's default size and at one step
larger — the breakpoint must not sit between those two. The `.tocpage2.minor`
quiet sub-headings already use flex `order` for their triangles; that is the
precedent to extend rather than a second mechanism.

### F16. Sharing the book: Books' Share sheet and a store listing

Tested 2026-09-17 (build 275): for a sideloaded EPUB, Apple Books' Share
produces only the title and author — "ཆོས་སྤྱོད། (chos spyod) 1.1+275 / Peter
Olin". A second `dc:identifier` with `opf:scheme="URI"` holding the WordPress
address changed nothing; removed. No metadata field is known to feed the
share sheet for a sideloaded book. The only way Share becomes useful is a
store listing, where it sends the store link — and where a new version
reaches readers' copies by itself.

A free listing is possible (Apple Books for Authors, Google Play Books,
Kobo Writing Life; not Kindle). Apple wants EPUB 3 in practice, so the
package would need a nav document beside the NCX. **The blocker is rights:**
the colophon calls this an independent, unofficial edition of Ka-Nying
Shedrub Ling's book, and every store makes the uploader assert distribution
rights. First step is the monastery's blessing, ideally listing under their
name with Peter as editor. Until then the WordPress link in the colophon and
on the QR code is the way the book travels.

### F15. A WhatsApp link in the colophon — once the kind of communication is decided

Asked 2026-09-17. The colophon (`src/acknowledgements.htm`) carries the
download URL, the QR code and the GitHub issues link. Peter wants a WhatsApp
contact beside them but has not yet decided what it is for: a way to reach
the editor, or a sangha group around the book.

What is known:

- A link to a person is `https://wa.me/<number>` (international format, digits
  only; `?text=…` prefills a message). It publishes a phone number for the
  life of every copy of the book, and dies with the number.
- A group invite link is `https://chat.whatsapp.com/<code>` from the group's
  "Invite via link". It does not expire; it dies only if an admin resets it,
  the group is deleted, or the group is full (1,024). With the group set to
  **admin approval for joins**, the link can stay in the book forever and
  still be gated — that is the right setting for a distributed link.
- Either kind is a plain `<a href>`; Books hands it to the system, which
  opens WhatsApp where installed and the web otherwise. Books shows a
  confirmation the first time a link leaves the book.

To do, once decided: add the link to the colophon's links block, with the
date it was issued, and note here which kind and where the group's admin
list is kept.

## G. Markup and stylesheet review — 2026-09-15

A second pass over `src/`, measured, after a month of navigation work. Graded
by what it buys: G1–G4 change what a reader or the next editor meets; G5–G9
are hygiene that a script can do in an afternoon; G10–G12 are conventions to
adopt going forward rather than retrofit.

### G6. Six id conventions, one of them a typed accident

`page420` (650), `TOC_CamelCase` (58), `return_from_…_p52` (16),
`snake_case` (28), `TN_`/`tn_` (4 + 4, same section, two cases), `leu1`,
`line142`, `toc_1`, `TODO`, `example6b`. Only `page N` is systematic. A
convention worth having: `p<page>-<slug>` for everything a jump can land on
(`p340-refuge-tree`), `h<page>` for headings, `rep<page>-<n>` for repeats.
Rename with a script that rewrites every `href` and `id` together and runs
check.py; nav.py's tooltips derive from headings, not ids, so they survive.

**Status:** Not done 2026-09-16: see C1.

### G9. Two `:root` blocks and one long comment-to-code ratio

The stylesheet is 1,072 lines of which 77% is comment. The comments are
good — they are the design record — but the file has no section headers
and the rules are not in reading order: `.left:before` (the ← glyph) is at
line 924, 350 lines after the arrow layout rules; `.center`, `.unit`, the
`div.pn*` family and `ul`/`li` sit between the repeat marks and the table
styles. `:root` is declared twice (light at 61 within COLOUR SYSTEM, dark at
217), which is fine, but a reader has to know. Proposed order, each under a
one-line banner: tokens → page/body → titles (all `tocpage*` rules together)
→ body text (`tibnormal`, `tibyigchung*`) → page numbers → landing marks →
jump links (all direction/scope rules together) → repeats → TOC/key/jewels
pages → images → legacy (empty after G2). Pure reordering; diff it with the
extracted-CSSOM trick used for the font check to prove nothing changed.

**Status:** Not done 2026-09-16: a reorder changes cascade order wherever two rules of equal specificity meet, and proving equivalence needs a rendered comparison, not a text diff. Worth doing with the device at hand.

### G10. Class names: two vocabularies

Marks the editor added read as what they *do*: `jumpDown`, `inlineAnchor`,
`repeatWrap3`, `lpn`. Body text reads as what it *is*: `tibnormal`,
`tibyigchung`, `tibyigchungH`. Both fine; the seam is `lpn` (linked page
number), `ppnp`, `ipnpx` (C3), `tibyigchungH` (the H means "heading line",
not heading), `inlineAnchorReturn` (identical to `inlineAnchor` in every
rule — merge), `repeatEnd`/`repeatEnd3` (3 uses, styled only by a shared
`:before`). Rename on the same script as G6.

### G11. ~~`<span>` is doing `<p>`'s job~~ — DECIDED with B1, 2026-09-17: it stays a span; see B1 under Completed

### G12. Conventions to adopt from now on

- New headings: pick the tag by G4's mapping; always arrows as placeholders
  and let nav.py fill; always a page number or none, never `???`.
- New jewels: `p<page>-<slug>` id; run `tools/jewels.py` after.
- New links: never a file-only `href`; always a fragment.
- Never type Tibetan into a shell heredoc (five failures on record); lift
  from the source with a script.
- One concern per commit (today's four-way split by hunk was needed because
  three concerns shared files).

---

## Verified in practice

Sections whose sequence — jumps, repeats, landing points — has been recited
through and confirmed. A section listed here needs no lama check unless its
text changes.

- **རྒྱུན་གྱི་བཀོལ་བྱང་ 88–91** — Peter, in actual practice, 2026-09-17.
- **གསང་ཐིག་ཕུར་བ 430–440** (lineage prayer and sadhana) — Peter, in actual practice, 2026-09-17, on the tree before the landmark relabelling and the rails (i.e. before `93069c8`).
- **དཀར་གསུར 154–156** — Peter, in actual practice, 2026-09-17, same tree.
- **དམར་གསུར 157–160** — Peter, in actual practice, 2026-09-17, same tree.

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

---

## Completed

### B1. ~~The whole liturgy is inline `<span>`. There are no paragraphs~~ — DECIDED 2026-09-17: the continuous flow stays

The question was "decide deliberately, and write the decision down". Decided:
the liturgy stays one continuous inline flow inside `.text`, as the pecha
runs. Tried on branch `paragraphs` (tools/paragraphs.py wrapped the text in
1,274 `<p class="recite|note">`, text verified identical, dev build 251) and
dropped the same day. Reasons, Peter's and mine:

- Accessibility gains are nil: no assistive tool speaks Tibetan usefully, and
  nobody will navigate a liturgy by paragraph.
- Source readability was already won by `tools/fmt.py` (G7); paragraphs added
  nothing visible in the editor.
- No tool in the chain needs paragraphs.
- The only real change would have been the layout — chant-book lines in place
  of the pecha's run-on text — and that was never wanted.
- 1,274 heuristic breaks, some visibly wrong, each needing a read-through.

So the costs named above stand, knowingly: no paragraph for a screen reader,
no `page-break-inside` to lean on, vertical rhythm by hand. G11 is the same
question and closes with this. The branch was deleted; the converter lives in
its history (commits 4bc1878, aeb75cc) if it is ever wanted.


41 items, in the order of the sections they came from. Each keeps its id, its
strikethrough and its closing note.

*From A. The reader sees this today*

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

### A2. ~~Six documents link `stylesheet.css` but not `fonts.css`~~ — RESOLVED

`c_87`, `c_91`, `p362`, `OPS/titlepage.htm`, `pn.htm` and `repeats.htm` linked
no file containing an `@font-face`, so they asked for Monlam and were handed
whatever the reading system substituted. Fixed by removing the cause rather
than the symptom — see B4. Verified through the CSSOM of the built book: every
document now reports exactly one stylesheet carrying both `@font-face` rules.

The check that matters here is the CSSOM one, not `document.fonts.check()`.
That returned `true` for every document even before the merge, because Monlam
is installed system-wide on this machine — a false positive of exactly the kind
that made the ཏངྱ hunt take a morning. Ask whether the RULE reached the
document, not whether the FONT is available.

### A6. ~~Pages 142 and 137 are out of order, and the arrows follow~~ — RESOLVED 2026-09-15: section moved to its place between 137 and 148, NCX and TOC-page entries added, arrows re-derived

In `p133_135_137_148_154_161_170_175_177_179.htm`, the section for printed
page **142 sits between 135 and 137**:

```
line  18   page133   ཡི་དྭགས་ཆུ་སྦྱིན།
line  38   page135   ཆུ་སྦྱིན་སྤྱད་གྲོལ།
line  57   page142   ལྷ་རྣམས་མཉེས་བྱེད་བསང་མཆོད་     ← out of order
line 102   page137   ཛམྦྷ་ལའི་ཆུ་སྦྱིན།
line 150   page148   ཆ་གསུམ།
```

This is not cosmetic. `nav.py` derives the prev/next chain from **document
order**, which is the right rule and gives the wrong answer here:

```
page135  right → #page142    "ལྷ་རྣམས་མཉེས་བྱེད་བསང་མཆོད་ 142"
page137  left  → #page142
```

So stepping forward from 135 lands on 142, and stepping forward again goes to
137 — five printed pages backwards. `nav.py` reports zero problems, correctly:
document order is exactly what it was told to follow.

**Fix:** move the 142 section to its place after 137, then re-derive with
`nav.py --write`. Moving content in a 700-page liturgy is not something to do
blind — confirm against the printed pecha which order is right first, since it
is also possible the section belongs where it is and the heading's page number
is wrong.

Three more faults are visible in the same document while you are in there:

- the `page142` heading text begins `142ལྷ་རྣམས་…` — the page number is in the
  title *as well as* in its `pageno` span
- `page142` and `page148` carry no arrows at all (part of D6)
- ~~`page157` has an empty `pageno`~~ — fixed 2026-09-12. It had no `pageno`
  span at all; given `157`, which the book already asserted twice (the id,
  and `page161`'s left tooltip `དམར་གསུར། 157`). Tooltip disagreements 30 → 29.
- `chos_rnams_thams_cad` has `???` and a literal `TODO phys page` in its
  heading text — see F3

### A4. ~~`titlepage.xhtml` declares itself English~~ — RESOLVED 2026-09-16

```
src/titlepage.xhtml:2   xml:lang="en"
```

It is the Tibetan title page. It is also the only document in the book that
declares a language at all — see E1.

**Closed:** Now `lang="bo" xml:lang="bo"`. E1 (tagging the rest of the book) stands.

### A3. ~~Nine spine documents are not in the NCX~~ — RESOLVED 2026-09-16

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

**Closed:** `p362`, `c_87`, `c_91` turned out to carry a heading that was not a heading (an `<a>` with the class); made real, listed, arrows joined. `pn.htm` and `repeats.htm` retired (G3). The title page, acknowledgements and key are now listed in the NCX and the English TOC as front matter. The cover page too, since Apple Books offers no way to the cover otherwise (checked on the device).

### A7. ~~Shads at a size boundary carry the wrong size~~ — RESOLVED 2026-09-16

Peter, 2026-09-16. Where large letters (`tibnormal`) and yig chung meet, the
shad that closes one run often sits inside the span of the other, so it is
drawn at the wrong size — a yig chung sentence ends in a full-size shad, or a
large-letter line ends in a small one. The rule: a shad takes the size of the
letters it is aligned with and touches. A shad that closes a yig chung
instruction is yig chung; a shad that closes a large-letter line is large.

Measured 2026-09-16, the pattern "span of one class ends, the next span of
the other class OPENS with ། or ༔":

```
74   ། or ༔ opening a yig chung span straight after tibnormal text
15   ། or ༔ opening a tibnormal span straight after yig chung text
 5   spans holding nothing but shads and spaces
```

Not every one of the 89 is wrong — the pecha itself sometimes sets a shad
small after large text — so this is a survey and a fix by eye, not a script.
Narrowed 2026-09-16 to the one pattern that is a mismatch by construction: a
`tibnormal` span ENDING in a shad, followed by a yig chung span with no
whitespace between the tags. The list, with printed page, file, line and a
search string unique in its file, is `resources/A7-shad-boundaries.md`
(21 rows). Regex: `<span class="tibnormal">[^<]*[།༔]</span><span class="tibyigchungH?">`. Moving a
shad across a span boundary changes no text, so `extract_text.py` proves each
batch harmless. Page 40 checked against the print: the small shad there is
right, so not every row is a fix.

**Closed:** Peter walked the 21 rows, moving the shad where it belonged to the small letters and spacing the rest; the 18 still matching got a space at the start of the small span. The regex finds nothing. The mirror case — a yig chung span ending in a shad with large letters hard against it, `<span class="tibyigchungH?">[^<]*[།༔]</span><span class="tibnormal">[^\s<]` — had 33 hits, mostly title lines; all got a space the same way. `resources/A7-shad-boundaries.md` kept as the record of the method.

*From B. Structural debt*

### B4. ~~`fonts.css` is a separate file for no reason~~ — RESOLVED

The three stylesheets are one. `fonts.css` (two `@font-face` blocks) and
`page_styles.css` (six lines of `@page`) are folded into `stylesheet.css` and
deleted; 58 documents lost their redundant `<link>` elements and the manifest
lost two items. The book ships 72 files where it shipped 74.

A document can no longer be half-configured, which was the whole argument: the
split bought nothing and cost A2.

`@font-face` `src` is relative to the stylesheet, not to the document that
links it, so `fonts/…` resolves identically from `OPS/` and from the root. No
path needed changing.

### B5. ~~calibre residue in the package metadata~~ — RESOLVED 2026-09-16

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

**Closed:** Contributor, calibre identifier, title_sort, timestamp, author_link_map and the calibre namespace removed. `dc:date` is 2026-09-16 and `dcterms:modified` a valid ISO stamp; `pack.sh` still restamps both at build.

### B6. ~~The `<guide>` is calibre debris~~ — RESOLVED 2026-09-16

```
src/content.opf:169   <reference href="OPS/p1_…htm" title="C2"/>
src/content.opf:170   <reference href="OPS/p1_…htm#page27" title="C3"/>
src/content.opf:171   <reference href="OPS/p1_…htm#page34" title="C5">
```

`C2`, `C3`, `C5` are meaningless. There is also no `type="text"` reference,
which is what a reading system uses to decide where "Start Reading" lands — so
it currently guesses.

**Closed:** The C2/C3/C5 references and the stray EPUB 3 `<nav epub:type="toc">` that sat between spine and guide are gone. The `type="text"` reference already existed.

### B3. ~~88 ids are duplicated across documents~~ — RESOLVED 2026-09-16

Mostly `page<N>` colliding between a content document and `pn.htm`. Ids are
per-document in EPUB so nothing is technically broken, but:

- `pp9` is duplicated between `p88_91_104_115.htm` and
  `p1_4_27_30_34_39_48.htm` — two *content* documents
- `example6b` is in both `p88_91_104_115.htm` and `key.xhtml`

and more practically, `#page543` is ambiguous to a human reading a link and to
any tool that does not track which document it is in. `check.py` already
catches duplicates *within* a document; it does not flag these.

**Closed:** The four real cross-document duplicates fixed: `pp9` in the köljang was a mistyped `pp97`; `TOC_ChangchubSemchog` in the ཟུར་ཡིག renamed; `toc_1` on the title page renamed; a commented-out duplicate `TN_Tsog` removed. Repeat ids are unique book-wide (G5). check.py still checks within a document only; a cross-document check is cheap to add if the habit returns.

*From C. Naming and convention*

### C5. ~~Four classes used with no rule, seven rules with no element~~ — RESOLVED 2026-09-16, bar `line191`

```
used, undeclared:   eh2   just   line191   margin_eh2_ee
declared, unused:   jumpTodO  nextlink  pagenumber  pn  pnh  prevlink  unit
```

Both halves are dead weight. `jumpTodO` is worse than dead — it differs from
`jumpTODO` only in case, and a reading system that matches classes
case-insensitively will apply one rule to the other. That already bit once
(commit `3df8d67`), and it will bite again while the selector exists.

**Closed:** All dead rules gone (G2 took most; `.ppnp`, `.easyjump` today). `eh2`/`just`/`margin_eh2_ee` left with `pn.htm`. `line191` in the köljang file still needs Peter: jewel or plain class?

### C6. ~~Heading levels are arbitrary within one series~~ — RESOLVED before 2026-09-16

The seven chapters of the ལེའུ་བདུན་མ། are one series at one depth, and they are
marked up at two:

```
p257_leu_bdun_ma.htm   leu1 h2   leu2 h2   leu3 h3   leu4 h3
                       leu5 h2   leu6 h3   leu7 h2
```

All seven carry `class="tocpage2"`, so they look identical and behave
identically — the level is doing no work, which is exactly why it drifted.
It does work for a screen reader, which builds its document outline from the
levels and will report this series as jumping in and out of a subsection.

Elsewhere the same is true across the book: 106 `h1`, 18 `h2`, 8 `h3`, and the
choice between them tracks nothing.

**Fix:** pick the level from the structure — a prayer is `h1`, a chapter
within one is `h2` — and let `tocpage1`/`tocpage2` keep doing the styling.

**Closed:** All seven chapters are `<h3 class="tocpage2">` now; measured 2026-09-16.

### C7. ~~File naming is two schemes~~ — RESOLVED 2026-09-16 by the merge

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

**Status:** Not done 2026-09-16: renaming 30 files rewrites every href, the NCX, the OPF and the TOC. Mechanical, check.py would prove it, but the names are Peter's to choose.

**Closed:** 54 prayer files became 10, named by printed page range (`p004-084.htm` … `p624-744.htm`) plus `zur-yig.htm` — `tools/merge_docs.py`. The calibre `c_NN` names are gone with the files.

*From D. Tooling and process*

### D4. ~~No check for what only a reader can see~~ — RESOLVED, and it found one

`tools/stacks.py`. 180 distinct base+subjoined stacks across 36,285
occurrences; it reports the ones that occur twice or fewer, on the argument
that a one-letter slip almost always produces a stack found nowhere else while
every real stack in a liturgy recurs.

**36 stacks are outstanding for your review**, and one group is not Sanskrit:

```
ངྣ  ངྒྱ  ཌྒྱ      all three in  src/OPS/p88_91_104_115.htm:23
                 ངྣདྨངྒྱཌྒྱ༔ སྤྲོས་མེད་དོན་གྱི་རྣལ་འབྱོར་པས༔
```

Three singleton stacks in one eight-syllable run, sitting exactly where the
opening line of རྒྱུན་གྱི་བཀོལ་བྱང་། should be, and containing a recognisable `དྨ`.
That is what an encoding accident looks like. The other 33 are all in plain
mantra context and are almost certainly correct Sanskrit — `ཛྷ` is in the
Sanskrit alphabet recitation `ཀ་ཁ་ག་གྷ་ང་། ཙ་ཚ་ཛ་ཛྷ་ཉ།`, `ཁྭ` is the ordinary
Tibetan word for crow — but that is a judgement, so the tool reports and does
not decide.

Accepted stacks go in `tools/stacks-known.txt`, which ships empty, so the
report shrinks to what is new once you have been through these.

D4 is closed as tooling. **The ངྣདྨངྒྱཌྒྱ run is open as content — see E7.**

### D2. ~~`check.py` cannot see meaning, and that boundary is not written down~~ — RESOLVED 2026-09-16

A link to `#todo` resolves, so `check.py` passes it. `nav.py` exists because of
this. The division is real and sound — `nav.py` decides what a link should
point *at*, `check.py` decides whether the path *resolves* — but it is recorded
only in a commit message.

**Fix:** state it at the top of both tools.

**Closed:** Stated in both module docstrings.

### D1. ~~No tests, no CI~~ — CI RESOLVED 2026-09-16; unit tests not written

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

**Closed:** `.github/workflows/check.yml` runs check.py, nav.py (which must find nothing to fill, turn or restamp), ncx_playorder.py, a build, and epubcheck on every push. No unit tests for the tools yet; the CI run is the regression net.

### D3. ~~The build cannot fail on a bad tree~~ — RESOLVED 2026-09-16

`pack.sh` uses `set -euo pipefail` and traps its staging directory, which is
good. But it does not run `check.py`, so a build with dangling links succeeds
silently.

**Fix:** `pack.sh` runs `check.py` first and refuses to build on errors, with
an explicit `--force` for when you know better.

**Closed:** `pack.sh` runs `check.py --quiet` first and exits 1 on errors; `--force` builds anyway.

### D7. ~~`nav.py` cannot tell that document order disagrees with the book~~ — RESOLVED 2026-09-16

A6 is invisible to every tool the project has. `nav.py` already reads the
printed page number out of each heading — it puts it in the tooltips — so it
has both numbers in hand and never compares them.

**Fix:** when the next section in document order has a LOWER printed page than
the current one, report it. It must stay a report: whether the fix is to move
the section or to correct its page number is a judgement about the printed
pecha, and reordering a document automatically is exactly the kind of thing a
tool should never do. But a five-page backward step should not be something
only a reader can find.

Cheap, too — the data is already collected, it just needs one comparison and a
line in the report.

**Closed:** nav.py reports "sections out of printed-page order within a file". Report only. Currently 0.

### D8. ~~Nothing checks a jump link's page number against its target~~ — RESOLVED 2026-09-16

A jump link carries a printed page in its `.lpn` — `གསང་ཐིག་རྡོར་སེམས། 92` — and
nothing has ever compared that number with where the link actually goes. One
such link pointed at `c_78.htm`, which is page **546**, and only a reader
following it found out.

The check that works is one-sided, and that is what makes it usable. A target
deep inside a long section legitimately sits on a later printed page than its
heading, so "label ≠ heading page" is mostly noise — 49 hits, nearly all
correct. But a target can never sit on an **earlier** page than the heading it
falls under, so "label page < heading page" is impossible by construction.
That test returns 3.

**Fix:** add it to `nav.py`, which already parses every heading's printed page
and every link. Report only, like the tooltip audit — deciding whether the
label or the target is wrong is a reading of the pecha.

**Closed:** nav.py reports "jump labels with a page below their target's heading". It found the three: 263 → 577 (the བཟང་སྤྱོད seven-branch jump into ལྟུང་བ་བཤགས), 344 → 346 twice (ཕྱི་མཆོད in the Thugs sgrub). 577 and 346 are the heading pages, not verified against the pecha — see A5.

*From E. Recorded, not being done now*

### E1. ~~Language tagging~~ — RESOLVED 2026-09-16

`dc:language` is `bo`; not one content document declares a language, and the
sole exception is wrong (A4). Costs: VoiceOver reads Tibetan with an English
voice, the OS's language-aware font fallback gets no hint, and Tibetan
line-breaking heuristics get nothing. Fix is mechanical — `xml:lang="bo"
lang="bo"` on the Tibetan documents, `lang="en"` on the English runs.

**Closed:** `xml:lang="bo"` on every Tibetan document, `en` on the key and acknowledgements pages with their Tibetan runs tagged `bo`. XHTML 1.1 has `xml:lang` only, so no `lang`.

### E2. ~~The page-list exists, is in the wrong file, and is 7/64 done~~ — RETIRED 2026-09-16

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

**2026-09-16:** the dead `<nav epub:type="page-list">` block, stray `?` included, is deleted from `toc.ncx`. The real page-list is still to build.

**Closed:** Decision (Peter, 2026-09-16): no page list. Different printings paginate differently, so a "go to page" that is right for one pecha is silently wrong for another; making it edition-aware is not worth it. The dead `<nav>` is out of the NCX. **The 64 `ppNNN` markers stay in the text on purpose** — they are the only durable record of where the pages fall and would be the basis of any future page list; do not treat them as dead weight under B7.

### E3. ~~Accessibility metadata~~ — RESOLVED 2026-09-16

No `schema:accessMode`, `accessibilityFeature` or `accessibilitySummary`. Books
will not behave differently; accessibility-aware catalogues read them.

**Closed:** schema.org accessMode, accessModeSufficient, accessibilityFeature, accessibilityHazard and accessibilitySummary in the OPF, EPUB 2 name/content form.

### E4. ~~Two weak alt texts~~ — RESOLVED 2026-09-16

Six images. Three carry proper Tibetan alt. `page1.jpeg` has `alt="Image"` and
the cover has `alt="cover"`.

**Closed:** The cover reads "ཆོས་སྤྱོད། cover"; the first folio image names itself in Tibetan and English; the QR image has an alt.

*From F. Asked for, not yet built*

### F1. ~~A jump link for "incipit … སོགས"~~ — DONE, eleven of them

```
p1_4…:194   ཇི་སྙེད་སུ་དག་ཕྱོགས་བཅུའི་འཇིག་རྟེན་ན། ༼ 581 ▸༽ །ཞེས་སོགས་ནས།
p1_4…:241   མེ་ཏོག་དམ་པ་ཕྲེང་བ་དམ་པ་དང་། ༼ 582 ▸༽ །ཞེས་པ་ནས།
p1_4…:581   ཇི་སྙེད་སུ་དག་ ༼ 581 ▸༽ སོགས་ནས།
p1_4…:678   མེ་ཏོག་དམ་པ་ ༼ 582 ▸༽ སོགས་ནས།
p1_4…:690   འདོད་ཆགས་ཞེ་སྡང་ ༼ 583 ▸༽ སོགས་ནས།
p219…:213   ཇི་སྙེད་སུ་དག་ ༼ 581 ▸༽ སོགས་ཀྱིས་ཡན་ལག་བདུན་པ་འབུལ།
p334…:195   ཧོཿ རིག་འཛིན་བླ་མའི་དཀྱིལ་འཁོར་ ༼ 356 ▸༽ སོགས་བསྔོ་སྨོན་…
p88…:282    རྗེ་བཙུན་འཕགས་མ་སྒྲོལ་མ་དང་ ༼ 121 ▸༽ སོགས་ནས།
p88…:297    ཇི་སྙེད་སུ་དག་ ༼ 581 ▸༽ སོགས་ཡན་ལག་བདུན་པ་དང་།
p88…:355    ཨོཾ༔ དངོས་འབྱོར་ཡིད་ཀྱིས་ ༼ 109 ◂༽ མཆོད་པ་རྗེས་སུ་
p133…:272   སྐྱབས་སེམས་གང་རུང་བྱ། ༼ 154 ◂༽
```

**Done in two passes, and the first one was wrong.** It found five, because the
survey required a `སོགས` within ±45 characters of the link. Six more sit just
outside that window — the incipit itself can be 40 characters long, so the
`སོགས` that follows it lands at 50 or 60. The second survey asked a better
question: does the link's label repeat text on the page within ±220
characters, before or after? That returns 16, of which 11 are this pattern.

The lesson is the window, not the count. A proximity test tuned to the
examples you have in front of you will miss the ones you do not.

No CSS was needed, as predicted — the existing classes render a label-less
link correctly.

**Twelve of the seventeen candidates were left alone**, and the count was the
point of surveying rather than pattern-matching. Most name a *destination*
rather than echo an adjacent incipit — `ཆོས་རྣམས་ཐམས་ཅད། 154` beside
`སྡིག་པ་ཅི་ཡང་སོགས` is a correct link doing its job, not a duplication.

Two more were the right shape but refused for a stated reason:

- `c_79.htm:65` — `བྱིན་རླབས་མཁའ་ལ` sits exactly between its incipit and its
  `སོགས`, but it carries **no `.lpn`**. Stripping the label would leave an
  empty link, a brace pair with nothing inside. It is also a `.jumpTODO`,
  which the book deliberately renders unfinished. Give it a page number and
  it becomes the sixth.
- `p88…:349` — `ཕྱག་འཚལ་བ་ནི་ཉི་ཤུ་རྩ་གཅིག་ཚར་གཉིས། 115` echoes the printed incipit
  but *adds* `ཚར་གཉིས།`, "two times", which is not in the printed text. That is
  information, not duplication, and stripping the label would delete it.

Still open from the original entry: `.lpn` sets at about 60% of body text, a
size chosen for a number sitting beside a label. These five are now the only
thing inside their braces. Worth a look on device before deciding.

### F2. ~~The repeat braces should be clickable, back to the start~~ — DONE

```
༼ …repeated passage… ◂༽          repeatWrap  + jumpRepeat
༼ …repeated passage… ◂༽༣         repeatWrap3 + jumpRepeat3
༼ …repeated passage… ◂༽༢་༣་༧      the 21 Taras, unchanged
```

All 62 repeat spans converted: each gained an `id="repeatN"` and an empty
`<a class="jumpRepeat…" href="#repeatN">` after its closing `</span>`. The
span draws the opening `༼`; the link draws the closing `◂༽`, so the mark that
closes a repeat is also the control that returns you to its start.

The shape was not invented. `.repeatAnchor` + `.jumpRepeat` was already
designed, styled and documented for exactly this, and already in use once —
`p88…:498`, `<a class="jumpRepeat count237" href="#TOC_21Taras"></a>`, an
empty link whose mark comes from CSS. The 62 follow it.

`.repeatWrap:after` and `.repeatWrap3:after` are deleted; the closing brace
now has one source instead of two.

**One regression, stated rather than shipped quietly:** those 62 links are
empty elements. They have no accessible name, so a screen reader announces 63
unlabelled links. Generated content is not reliably read out, so the mark
itself does not supply one. The fix is a `title` on each — but the wording
should be Tibetan the book already uses, not something invented, so it needs
deciding. See E1, which this compounds.

### F3. ~~ཆོས་རྣམས་ཐམས་ཅད། has a heading it should not have~~ — RESOLVED

Removed 2026-09-12. The heading was the first four syllables of the verse
directly beneath it — the text repeated and promoted to a divider.

Clean, as predicted: nothing linked to the heading. The jump link that reaches
this passage (`c_78.htm:99`) targets `#TOC_ChonamThamche`, the `inlineAnchor`
on the line below, which is kept; the heading was absent from the NCX. Only
`page154`'s right arrow and `page157`'s left needed re-deriving, and they now
chain 154 ↔ 157 directly.

It paid the three dividends it promised: one fewer arrow-less heading (D6),
one fewer `???` page number (A5), and the last visible `TODO phys page` string
in the book is gone.

### F4. ~~Too much air above the title rule~~ — RESOLVED, provisionally

`margin-top` on `.tocpage1, .tocpage2` halved, 2.2em → 1.1em. That is the gap
between the end of the last prayer and the hairline that divides it from the
next; at 2.2em the rule floated clear of the text above rather than dividing
two things.

Explicitly a starting point, not a settled value — recorded here so the next
adjustment knows where it came from. The 0.15em below the title is untouched:
it is deliberately tight, and it is what groups a title with its own text.

### F5. ~~Phurba conclusion~~ — PLACED 2026-09-12 from the Lumbini chantbook

Requested 2026-09-12; first thought to need the Pyr pecha. The Lumbini 2024
chantbook (`kilaya.html`) has it: from the ཧཱུྃ༔ སྣང་སྲིད་ཕུར་བུའི verse to the
chapter's end — dissolution and re-arising, the departure mantra, and two
verses of aspiration and auspiciousness. Lifted verbatim (six paragraphs,
clean Unicode; the source's runs of spaces turned into line breaks, and one
missing break after a ༔ supplied). Third entry of the ཟུར་ཡིག
(`c_extra.htm#TOC_PhurpaDuDang`), NCX and TOC-page rows, a bare jewel target at
its head, and a jump to it from the end of ཚེ་རིང་མ (`c_68.htm`). The heading
`ཕུར་པའི་བསྡུ་ལྡང་།` is mine, built from the passage's own words — rename if
the book has a better one. Not yet read on device.

### F7. ~~Add: the ultimate guru sadhana of simplicity~~ — PLACED 2026-09-12, awaiting Peter's read

Requested 2026-09-12. Tulku Urgyen Rinpoche's short guru sadhana, 51 lines in
five parts. **Source:** `resources/TUR Guru Sadhana.pdf` pp. 6–8 (Bodhi
Translation, 2025). Its text layer is a legacy-font skeleton, so the Tibetan was
transcribed from the page images into `resources/extracted/tur-guru-sadhana.md`
and checked three ways (every surviving skeleton character in order, the
phonetics on pp. 9–10, and every stack against the two big corpora). Two things
for Peter's eye before it goes in: the seed syllable is read as `ཨཿ` (the PDF
shows a visarga; the layer dropped it), and `ཨོ་ཌྷི་ཡ་ན` is spelt as printed, which
occurs nowhere else in the book. The PDF's `༌` before a shad after `བཟང`/`ཡང` is
kept as printed; our book uses a plain tsheg there. Placed second in the ཟུར་ཡིག
(`c_extra.htm#TOC_TromeLadrub`), with its own NCX entry under ཟུར་ཡིག and a row on
the TOC page. Not yet read on device. Not in the newer
source EPUB (`comparison-2026-09-12.md`, finding 1).

### F8. ~~Add: calling the guru from afar~~ — PLACED 2026-09-12, awaiting Peter's read

Requested 2026-09-12. A text to be added to the book. Source, placement, and
title not yet given. Same handling as F7. If it goes alongside F7, decide the
order and whether the two share a heading level with the ཞབས་རྟེན། section.

**2026-09-12:** not in the newer source EPUB. **Source found:** Jamgön Kongtrul's
text in `resources/Lumbini 2024 Chantbook En-Tib.epub` (`calling_the_guru.html`),
61 clean-Unicode paragraphs lifted verbatim; instruction paragraphs became
yigchung. Its title line there is in a legacy font with private-use glyphs, so
the title was supplied from the standard wording and checked syllable by
syllable against the surviving skeleton. Placed first in the ཟུར་ཡིག
(`c_extra.htm#TOC_LamaGyangbo`), NCX entry under ཟུར་ཡིག, row on the TOC page.
Peter to confirm this is the version Ka-Nying recites. Not yet read on device.

### F10. ~~The embedded Monlam font is patched~~ — SUPERSEDED: the book now embeds Noto Serif Tibetan

2026-09-15. Two rendering faults were traced to Monlam Uni OuChan2 itself: no
mark positioning, so ཾ and ྃ sat right of centre on wide letters (རཾ་ཡཾ་ཁཾ);
and no glyphs for the en space and hair space the text uses ~5,300 times, so
those gaps were drawn by whatever fallback font Books picked. A font patch
fixed both and was then invisible on device for four builds, because the Mac
has Monlam installed under the same name and Books used the installed copy.

Peter's call: a font that works out of the box, on Apple and Android, over a
patched one. Jomolhari was tried first (build 109) and failed the same way in
Books: it has no GPOS mark-to-base table, and the substitutions it relies on
instead are honoured by Chrome but not by CoreText. Rendering the candidates
through Quick Look's WebKit — the engine Books uses — showed **Noto Serif
Tibetan** (Google Fonts, v2.103, SIL OFL) centring the marks and setting the
visarga tight; it has a real mark-to-base table and is Android's own Tibetan
font. Comparison sheets: `resources/extracted/font-comparison-2026-09-15.png`.
Licence ships as `src/fonts/OFL-NotoSerifTibetan.txt`.

Consequences recorded in the stylesheet: body size 1.5em → 1.25em (its letter
body is ~23% taller), head-line raises recomputed from H = 0.678 (yig chung
0.170em, jewel marks 0.291em). Lesson for the file: test Tibetan shaping in
WebKit (`qlmanage -t` on an HTML page), not only in Chrome.

To check on device (build 110+): the anusvara; the gap after ཨཱཿ; overall size
against the printed book — 1.25em is a computed guess; the jump-brace spacing;
the yig chung head-line alignment; and the ༔ gaps, which now come from the
reader's fallback font again (sane under WebKit in the test).

### F11. ~~ཁོར་བ་དོང་སྤྲུག has no prev/next arrows — and nav.py cannot see that~~ — RESOLVED 2026-09-16

Peter, 2026-09-15. The heading at `c_80.htm#page558` carries no `<a class="left">`
/ `<a class="right">` at all, so the section has no prev/next. `nav.py` only
fills arrows that exist as placeholders; a heading with none is silently
skipped, so "0 fillable, 0 unfillable" was true and still hid this. The survey
below lists every heading in the same state (some are deliberate: ཟུར་ཡིག and
the ཞབས་རྟེན། sub-collection headings). Fix: insert the two placeholder anchors
into the heading and run `python3 tools/nav.py --write`; and teach nav.py to
report linkable headings that have no arrows, so this cannot hide again.

**2026-09-16:** arrows inserted and filled by `nav.py --write` (← 557 ལུས་སྤྱིན… lineage prayer, → 578 པད་གཙུག་ལྷུང་བཤགས།). Teaching nav.py to report arrow-less headings is still open.

**Closed:** Arrows filled earlier; nav.py now reports "headings without arrows" (quiet sub-headings and the ཟུར་ཡིག head excepted). The sweep it enabled found three more arrow-less prayers that were also fake headings — see A3.

### F13. ~~Relabel the ཟུར། 159 link~~ — RESOLVED 2026-09-16

Peter, 2026-09-15. In `p133_…htm` (the གསུར section, line ~260) a jump reads
`ཟུར། 159` and points at `#dedications`. "zur" alone says nothing to the
reader; the label should name what is there — the dedication and aspiration
verses, བསྔོ་བ་སྨོན་ལམ། or wording of Peter's choice. Lift the words from
the destination's own text rather than typing them.

**Closed:** Now `ཧོཿ ཆོས་དབྱིངས་རྣམ་པར་དག་པ། 159`, the destination's own opening words.

*From G. Markup and stylesheet review — 2026-09-15*

### G3. ~~`pn.htm` and `repeats.htm` are spine pages nobody can reach~~ — RETIRED 2026-09-15 to `retired/`; the 64 in-word page anchors keep their ids and lose their dead href

`pn.htm` is the old page-number list: 631 `.ppnp` anchors, 511 of them
inside comments, no NCX entry, no inbound link since the fastjump page was
retired. `repeats.htm` is 13 `<aside epub:type="footnote">` stubs from an
abandoned pop-up-footnote experiment, also unreachable. Both are linear
spine items, so a reader paging through the book meets two junk pages
between the ཟུར་ཡིག and the English TOC. Retire both to `retired/` as
`c_fastjump.htm` was, remove them from spine and manifest, and let check.py
confirm nothing pointed there. (E2's page-list, if wanted, is a
`nav epub:type="page-list"` in the NCX/nav document, not a page.)

### G4. ~~Heading levels do not encode structure~~ — FIXED 2026-09-15: the four h2 chapter headings became h3; the mapping is recorded above the `.tocpage` rules in the stylesheet

103 prayer titles are `h1.tocpage1`; 6 are `h2.tocpage1` (the ཟུར་ཡིག
sub-collections and the two ཐུགས་སྒྲུབ sections); the seven chapters are
`h2.tocpage2` for 1, 2, 5, 7 and `h3.tocpage2` for 3, 4, 6 — the same rank,
two levels, at random; the quiet sub-headings are `h3.tocpage2.minor`. The
class carries the meaning and the tag is noise, which is why CSS and nav.py
both key on the class. Decide one mapping and apply it mechanically: prayer
= `h1.tocpage1`, section of a collection = `h2.tocpage1`, sub-heading of a
prayer = `h3.tocpage2` (chapters) or `h3.tocpage2.minor` (quiet). Screen
readers and the NCX depth both benefit; nothing visual changes.

### G2. ~~Ten CSS classes with no element, four elements with no rule~~ — RESOLVED 2026-09-16, bar `line191`

Never used: `.center` (and its `(` `)` pseudo-content), `.invisiblec`,
`.jumpTodO`, `.nextlink`, `.prevlink`, `.pagenumber`, `div.pn`, `div.pnh`,
`.unit`, `.ttf`, plus `.pageno-unknown` as a bare class (`div#pagenumberlist`
is used once, in `pn.htm`, and goes with it in G3).
Used but unstyled: `eh2`, `just`, `margin_eh2_ee` (calibre residue in
`pn.htm`) and `line191` — a jewel id typed into the class slot in
`p88_…:380`, so that "anchor" has never been a jewel. Delete the ten,
fix the one, drop the three with `pn.htm` (G3).

**Closed:** The ten dead rules deleted (`.invisiblec`, `.center` ×3, `.unit`, `div#pagenumberlist`, `div.pn`, `div.pnh`, `div.pagenumber`, `.prevlink`, `.nextlink`) and `.jumpTodO` dropped from the shared selector. `.pageno-unknown` kept and put to use (G8). Still open: `line191` in `p88_…:380` — jewel or plain class? Needs intent.

### G7. ~~Whitespace and line shape~~ — trailing whitespace RESOLVED 2026-09-16; line-breaking RESOLVED 2026-09-17 by tools/fmt.py (render-identical reflow, enforced in CI)

1,551 lines end in trailing whitespace; 449 lines exceed 400 characters
(several over 2,000). Neither affects rendering, both make diffs unreadable
and hide real changes — the tsheg batch today diffed as 343 hunks partly
because of it. A one-time normalisation (strip trailing space, break after
every `</span>` and before every `<span class=`, never inside Tibetan) would
make future diffs show what changed. Do it as one commit with nothing else
in it, and verify with `extract_text.py` that the extracted text is
byte-identical before and after.

**Closed:** 268 trailing-space lines stripped across 53 files; `extract_text.py` output byte-identical before and after. The second half (breaking long lines at span boundaries) is a separate one-commit job and stays open here as G7b.

### G8. ~~Three inline `style=` and one hidden jewel~~ — RESOLVED 2026-09-16

`p1_4_…:50` — `<span id="TODO" style="display:none" class="inlineAnchor">`,
a jewel named TODO, hidden by an inline style, and listed on the Jewel Jumps
page as such. Resolve or delete. `acknowledgements.htm` and
`titlepage.xhtml` carry one inline style each; the key page's `<col>` widths
are the only defensible ones. Also three empty `tibyigchung(H)` spans
(`c_56:20`, `p1_4:538`, `p219:305`) and one `.calibreBody`-less body among
the four helper pages.

**Closed:** The hidden `#TODO` jewel deleted and jewels.htm regenerated (97 jewels); the last empty yig chung span deleted; the two inline styles became classes (`.signature`, `.coverimg`); `acknowledgements.htm` got `calibreBody`. The `???` page placeholder in p1_4 now carries `pageno-unknown`, so it is hidden from the reader as A5 always claimed.

### G1. ~~The TOC page styling never applies~~ — RESOLVED 2026-09-16

`.toctib1` and `.toctib2` are written as `ul .toctib1` / `ul .toctib2`, but
`toc1.htm` has no `<ul>`: the lists are `<dl class="toctib1">`. Both rules are
dead, and the TOC page renders at raw browser defaults. Fix: `dl.toctib1`,
`dl.toctib2`, and while there give `dt`/`dd` the sizes the rule intended.

**Closed:** `dl.toctib1` / `dl.toctib2`; dt/dd spaced; nested lists inherit size and opacity instead of shrinking twice.

### G5. ~~Ninety-six ids duplicated across documents~~ — RESOLVED 2026-09-16

64 are `page N` / `ppN` pairs that exist in both a prayer file and `pn.htm`
— gone with G3. The rest are `repeat1…repeat13` reused in 15 files: a
same-document link, so harmless today, and a landmine the day two files are
merged (which G7 and the page-break question both point toward). Rename to
`repeat-<page>-<n>` or prefix with the file's first page.

**Closed:** `repeat<n>` → `rep<page>-<n>`, 62 renamed with their hrefs. Nothing is duplicated across documents now (B3).

### G7b. ~~Break long lines at span boundaries~~ — RESOLVED 2026-09-16

The second half of G7: 449 lines exceed 400 characters. Break after every `</span>` and before every `<span class=`, never inside Tibetan, as one commit with nothing else in it, verified with `extract_text.py`.

**Closed:** Broken only where whitespace already stood (a space between tags, an ASCII space after a shad on a long line); extracted text byte-identical. Longest line 1,957 → 703; the rest is Tibetan whose only breaks are en-space entities.
