# Ten perspectives on the chos spyod eBook — a quality assessment

Written 2026-09-17 at master `86e0a22`, dev build 249, for Peter to read later.
Independent, critical, evidence-based: every count below was measured in the
tree that day. Where a judgement is mine rather than a measurement, it says so.
Each perspective closes with a verdict and the three moves that would matter
most. A summary of the top ten actions across all perspectives stands at the
end.

**The book in numbers.** 106 prayers under red titles, 21 sub-headings, about
505,000 Tibetan characters in ten documents. 126 jump links (83 forward, 43
back), 101 landing jewels, 59 repeat braces, 703 written-out refrains, 3
annotations, 9 visible TODO stubs. Release EPUB 4.2 MB, of which fonts 2.2 MB
and images 3.2 MB before compression. Valid EPUB 2, epubcheck 0/0, CI on every
push, 211 commits over 25 working days.

---

## 1. Literary and textual fidelity

*Is the text the pecha's text, and where it is not, does the reader know?*

1. **Provenance is honest and stated.** The acknowledgements say plainly that
   the book descends from an unauthorised 2561 EPUB of the third printing, not
   from the publisher's source. That honesty is the right foundation. It also
   means every character is at second hand: nobody has proof-read this text
   against the pecha end to end.
2. **Known variants are catalogued, not resolved.** The comparison with the
   fourth-printing EPUB found about 84 small differences (TODO F9), two of
   them probable errors on our side (ཏུ for དུ; a swapped ཤོ/ཤྭ in a mantra).
   Cataloguing is good work; leaving known probable errors in a book people
   recite is not. These two should be fixed or annotated now.
3. **Open editorial questions are written down** (E7): refrain counts that
   disagree by one, ཨོ་སྭསྟི against ཨོཾ་སྭསྟི, three spellings that differ
   from the Lumbini chantbook. Written down is half the job.
4. **Typing errors surface only by accident.** Today's find, བདུད་རྩིི with a
   doubled vowel, sat there for three years. `tools/stacks.py` lists
   suspicious stacks but its list has never been worked through and accepted.
   A systematic pass, syllable dictionary or eye, has not happened.
5. **The 703 written-out refrains are the largest editorial addition** and the
   most exposed to error, since each was typed by the editor. One was wrong
   (a doubled བ) and found by the editor reading on the iPad. A mechanical
   check exists now for one failure shape; the others (wrong line written out,
   wrong count) have none.
6. **Added texts are sourced and marked.** The zur yig's additions name the
   Lumbini 2024 chantbook; the symbolic script on p. 88 names the Rinchen
   Terdzö. That is scholarly practice and should stay the rule.
7. **The key page distinguishes printed from added** by colour and by shape,
   and says so in words. A reader can always tell what the pecha says.
8. **Colophons are kept**, in yig chung, as printed. Good: they are part of
   the text's authority.
9. **Sanskrit is left in Tibetan transliteration only**, as the pecha has it.
   Correct for fidelity; see perspective 8 for what it costs.
10. **The 3rd/4th printing question is unresolved in principle.** Which
    printing is this book? The title page does not say. Readers with a fourth
    printing in hand will find differences and not know why.
11. **Headings are the printed TOC's titles**, verified; 30 tooltip/heading
    spelling disagreements remain (E7) and nobody has said which side is
    right.

**Verdict: good provenance, honest labelling, no proof-reading.** The text is
probably better than 99.9% right and the last tenth of a percent is in mantras
and refrains, where it matters most.

**Three moves:** fix or annotate the two known probable errors; work through
`stacks.py --accept` once; state the printing on the title page.

---

## 2. Usability in practice

*A practitioner in the shrine room, phone in one hand, chanting with a hundred
others. Does the book keep up?*

1. **The book knows what it is for.** Jumps follow the order things are
   actually recited at Ka-Nying and the Gomdes, not the order of the print.
   That is the whole reason to prefer this to a PDF and it delivers.
2. **Return paths exist everywhere a jump leaves the text.** Each landing
   jewel has its way back; the Tara sadhana's three rounds each return to
   their own spot. This is the hardest part of the design and it is done.
3. **Finding your place cold is slow.** A latecomer knows the prayer name and
   perhaps a page number. The route is: Books menu, TOC, scroll a 135-entry
   list. The English TOC page is faster but is at the back of the book. There
   is no "go to page N" and no way to search by page number.
4. **One-handed use is untested.** Jump links are small inline Tibetan text
   in braces. Tap targets on a phone are near the minimum; two links a line
   apart are easy to confuse. No measurement has been made.
5. **The reader must know the system.** Braces, triangles, jewels and red
   refrains carry meaning only after reading the key page. New readers do
   not read key pages. The system is learnable in a minute, but nothing
   invites that minute.
6. **Speed is now confirmed** on the iPad with Monlam embedded; page turns
   and jumps are quick. The 1.5 MB font is the one cost and it is paid once.
7. **Repeats are countable.** A brace with ༣ says three times; the closing
   brace jumps back to the start for long passages. Better than the print,
   which says ལན་གསུམ in yig chung and leaves you to find the beginning.
8. **The written-out refrains remove the single most common stumble** in
   group recitation, the abbreviated line. This is a real service to
   non-fluent chanters and to anyone reading in dim light.
9. **44 of 106 prayers have no jump, jewel or repeat mark at all.** Some need
   none. But protectors, torma texts and the dhāraṇīs are recited in fixed
   sequences too, and the routes there are not yet drawn.
10. **Nothing remembers where you were.** Books remembers the last page, but a
    practitioner following the Trinley Nyingpo route through five files has
    no "back to where I came from" beyond the jewel the editor placed. A
    reader who taps a wrong link is lost.
11. **Two grades of seven-branch prayer are still TODO stubs**, visible in
    the bodhicitta ritual. A reader hits a dead end there.
12. **The daily-practice abbreviations** (Tara p. 113) are handled with jumps
    up into the full text. Elegant, but the reader must trust six TODO
    stubs until a lama has checked the sequence.

**Verdict: excellent for the routes it covers, thin elsewhere, and it assumes
an initiated reader.** The jump system is the book's best idea and it is about
60% drawn.

**Three moves:** draw the routes for the protector and torma sections; put the
English TOC, or a one-screen "where am I" page, at the front; get the lama
pass done on Tara so the stubs go.

---

## 3. Dark mode and themes

*Books offers White, Sepia, Gray and Night. Does the book survive all four?*

1. **The platform behaviour is measured, not guessed.** The stylesheet's
   PLATFORM NOTE records what Night repaints and what it leaves: element text
   repainted, generated content and opacity respected, images untouched. Every
   decision downstream leans on that. This is unusually good engineering.
2. **The marks survive Night by construction.** Braces, jewels, triangles and
   repeat counts are generated content with colour declared on the
   pseudo-element, so they stay red. Verified on the iPad.
3. **The red title text does not survive.** In Night, prayer titles are white
   like everything else; only their position and size mark them. The heading
   rule was removed on 2026-09-16, so the last red on a Night title is gone.
   Peter judged the result "totally ok". It is acceptable, not designed.
4. **Written-out refrains lose their red in Night** and keep only reduced
   opacity (0.75, measured at 8.2:1). The signal "this is the editor's" is
   weaker exactly where a chanter most needs to know what is printed.
5. **The symbolic script on p. 88 is now a glyph**, so it takes Night's ink.
   Three image-based attempts failed first, and the failure modes are
   recorded. The right end, reached the hard way.
6. **Contrast is documented per token**: accent 6.8:1 on white, 7.0:1 in
   Night, green 5.4:1 and 8.8:1. These meet WCAG AA and mostly AAA. Someone
   did the arithmetic.
7. **Sepia and Gray are untested as far as the record shows.** Red on sepia
   should hold; the green preference on gray may not.
8. **`-webkit-text-fill-color` is declared 21 times** while the platform note
   says Night defeats it on element text (TODO B2). Harmless, but it is
   belt-and-braces code that nobody has confirmed does anything.
9. **The yig chung green preference** has a Night pair, and the switch is a
   link because Books swallows taps on checkboxes. Thoughtful.
10. **The cover and deity images do not adapt** and should not; they are
    pictures. But the first-folio scan on p. 1 is a black-on-white bitmap that
    becomes a white slab in Night. It could be a transparent PNG like the
    symbolic script was.
11. **No dark-scheme test exists in CI**, and cannot, since Books' Night is
    not a CSS media query in the normal sense. The only test is the iPad.

**Verdict: robust where it matters, and better documented than most
commercial EPUBs.** The Night theme is survived, not styled.

**Three moves:** decide whether Night titles deserve a mark of their own
(weight, or a generated ornament); make the p. 1 folio transparent; test Sepia
and Gray once and record it.

---

## 4. Readability and typography

*Can it be read at arm's length, at speed, for an hour?*

1. **The font decision was made properly**: 22 faces compared in Books, one
   chosen for on-screen reading at body size, its mark positioning verified,
   its licence confirmed. Monlam Uni OuChan2 is a defensible choice for a
   chant book, less so for a scholarly page; it is heavier and rounder than
   the pecha's face.
2. **Head-line alignment is done by arithmetic**, and the arithmetic is in
   the stylesheet: yig chung raised 0.118 em, jewels 0.202 em, so small and
   large letters hang from the same line as on the printed page. This is a
   detail almost no Tibetan eBook gets right.
3. **Body size is the reader's own** (1em), after two rounds of tuning
   against a fallback font that turned out never to have loaded. Correct
   decision; every reader has a size control.
4. **Line-height 1.5 is generous for Tibetan**, which stacks deep but has no
   ascender-heavy letters. It could go tighter on a phone; nobody has tried
   1.35.
5. **Yig chung at 0.8 em and 0.85 opacity** reads as a second voice, as it
   should. In bright light 0.85 grey on white is a little faint; the green
   preference exists for exactly this reason.
6. **Digits are set in the Latin face** because Monlam's digits clipped on
   the iPad. Right call, slightly foreign look. The page numbers inside jump
   links are consequently tiny Latin numerals in a Tibetan line.
7. **Page numbers under titles are 0.4 em** (TODO E5), roughly 6 px at Books'
   default. Unreadable for anyone over fifty without zooming.
8. **Shads at size boundaries were audited** (A7) and 21 fixed; 33 remain
   deliberately spaced and await a decision. Fine detail, properly parked.
9. **Gaps are padding, not characters**, since Monlam lacks glyphs for the
   thin spaces. That protects the text from font fallback. The gter tsheg
   gap after ༔ is still a plain space and looks slightly wide.
10. **Justification and line breaking are left to the reader**, and Tibetan
    breaks after tsheg only. Books does this acceptably; long mantras
    sometimes leave ragged lines. No hyphenation exists for Tibetan, so this
    is the ceiling.
11. **Long stretches of tibnormal run without visual rest** in the longer
    prayers, since the flow is continuous by decision (B1). The pecha has the
    same density. On a phone in portrait it is a wall.
12. **Two fonts for marks** (a two-glyph Jomolhari subset for ࿙, a one-glyph
    trace for p. 88) is the right way to fill a gap without swapping faces.

**Verdict: professionally set for a chant book, with the numerals as the one
visible compromise.** The typography is better than the original print in
consistency and worse in only one respect: it cannot be held.

**Three moves:** raise `.pageno` to something legible; try a tighter
line-height on a phone; decide the gter tsheg gap.

---

## 5. Jumpability and navigation

*The book's own word for its purpose. How well does the machinery work?*

1. **The navigation model is coherent**: forward and back triangles, one for
   inside the prayer and two for leaving it, jewels for landing, braces for
   repeats, prev/next arrows on every title. Four ideas, consistently applied.
2. **The machinery is verified by tools on every push.** nav.py reports
   mismatched labels, wrong-way arrows, out-of-order sections, labels below
   their target's page, and missing arrows. Today all report zero. This is
   the book's strongest engineering asset.
3. **Every jump has a page number label**, so a reader with the printed book
   can follow along. 18 jumps carry a page but no words; the surrounding text
   is the label, by design, but a reader landing mid-line may not know that.
4. **The Jewel Jumps page lists every landing point** in reading order with
   its prayer and page. It is the closest thing to a map of the book and it is
   the last page. It would serve better as the first.
5. **Depth is two.** The NCX has 135 entries, sub-headings nested one level.
   Books renders this flat enough to scroll; a third level (the Leu Dünma's
   chapters within the Thugs sgrub within the Barchey Künsel) would help and
   is possible in NCX.
6. **29 anchors have nothing pointing at them** (B7), one of which draws a
   visible jewel that no link reaches. Dead ends are worse than no ends.
7. **Cross-file jumps are marked "out" automatically.** After the ten-file
   merge the rule needed an exception for an embedded root text, and got it.
   The rule now depends on a hand-kept list; that is a smell.
8. **Jump labels are the destination's opening words**, which is exactly what
   a chanter hears from the umdze. Better than titles.
9. **There is no "return to where I jumped from" that follows the reader.**
   Each return is a fixed link to a fixed spot. For the common routes that is
   right; a reader who explores is on their own. EPUB 2 offers nothing better
   without JavaScript, and JavaScript for this would be fragile in Books.
10. **Nine TODO stubs are visible in the text**, six of them lama questions
    placed today, three older. The design makes unfinished work visible,
    which is right; it also means a released book must have zero.
11. **The Tara sadhana walk found four sequence errors** in one prayer. No
    other complex prayer (Thugs sgrub, Kilaya, Narak) has had the same walk.
    Assume similar errors exist there.
12. **The köljang is verified in practice**; one of 106. A "verified" ledger
    now exists in TODO.md and should fill.

**Verdict: the machinery is sound and tested; the content it carries has been
verified in one prayer and found wanting in another.** Structure 9/10,
verification 3/10.

**Three moves:** walk the Thugs sgrub, Kilaya and Narak sequences the way Tara
was walked; resolve the 29 orphan anchors; move the Jewel Jumps page forward.

---

## 6. UI design and visual language

*Does the book look designed, and does the design carry meaning?*

1. **Two colours, two rules.** Red for what the editor supplied, the reader's
   link colour for what can be tapped, black for the pecha. A rule this simple
   is the mark of a designed system, and it is stated on the key page.
2. **Shape carries meaning too**, so colour is never the only signal:
   braces, triangles, jewel. Colour-blind safe by construction, and it
   survives Night. Textbook, and rare.
3. **The marks are Tibetan glyphs from the text's own font**: ༼ ༽ ༴ ࿉ and
   digits. They belong to the page. The triangles ▸ ◂ are the one foreign
   element and are small enough to pass.
4. **The cover is competent, not distinctive**: a painting of Guru Rinpoche
   cropped to portrait, the title in white Monlam on a saffron band. The band
   is the right colour for a Ka-Nying book; the painting is a stock
   reproduction at modest resolution and the crop cuts the throne. It says
   "Nyingma liturgy". It does not say "this edition".
5. **The title page is a text file.** Two lines of Tibetan, a version, a
   URL, a report-errors link. Functional, unstyled. The first thing a reader
   sees after the cover is the least designed page in the book.
6. **Prayer titles are red, centred, with the page number under and arrows
   flush to the name.** After the rule was removed they are quieter; on a
   long page the reader's eye finds them, on a phone they can slip past.
7. **The key page is well written and correctly ordered**: what is printed,
   what the editor added, preferences, typography. Its examples are live
   markup, so they cannot drift from the real thing. Its one weakness is
   length: nobody reads eleven legend entries before chanting.
8. **Three deity line drawings open the book** with captions, framed and
   centred. Good. They are the only images inside the text, so the book has
   no visual rhythm after page 4.
9. **The English TOC has 131 entries with glosses**, 14 with links to
   translations. The glosses vary from four characters to a sentence; some
   are titles, some descriptions. It reads as a working document, not a
   designed page.
10. **The Annotations page borrows the Jewel Jumps layout** rather than
    getting its own. Fine for three notes; it will need its own design at
    thirty.
11. **Nothing signals the edition's identity** inside the book: no
    ornament, no consistent yig mgo treatment, no colophon page in Tibetan.
    A Tibetan book announces itself; this one is anonymous once past the
    cover.
12. **Vertical rhythm is by hand** (B1 decision) and mostly consists of the
    heading margins. It works because the text is dense by nature.

**Verdict: a real design system with a thin skin.** The semantics are
excellent; the presentation layer, cover, title page, TOC page, has had no
design pass.

**Three moves:** design the title page and give the edition a name and a
Tibetan colophon; commission or licence a cover image at full resolution;
normalise the TOC glosses to one form.

---

## 7. Tibetanness

*Would a Tibetan-educated reader recognise this as a proper book of their
tradition, or as a Western digital object holding Tibetan text?*

1. **The text runs continuously as a pecha does**, decided today against
   paragraphing. That is the single largest Tibetan-ness decision and it went
   the right way.
2. **The yig mgo ༄༅ opens texts as printed**, colophons close them in yig
   chung, the sbrul shad ༈ separates. The apparatus of the page is respected.
3. **The gter tsheg ༔ is kept for terma texts** and ordinary shad for
   others, as printed. Many digital editions normalise these; this one does
   not.
4. **Symbolic script is reproduced, not typed around.** The köljang's ḍākinī
   line is a traced glyph from the Rinchen Terdzö. A Tibetan reader would
   expect exactly that line to be there.
5. **Repeat marking uses ang khang ༼ ༽ and Tibetan numerals**, close to
   what a Tibetan editor would pencil in. The triangles are foreign. A
   Tibetan reader would understand them; a Tibetan editor would not have
   chosen them.
6. **The annotation mark ࿙ is the mchan rtags**, the traditional way to hang
   a marginal note. Choosing it over a superscript numeral was right, and it
   was chosen by looking.
7. **Page numbers are the printed book's**, so a reader with the pecha can
   follow. The book knows it is a companion to a physical object.
8. **The title is only Tibetan** in the metadata and on the title page, with
   a Wylie gloss. Good. But the edition has no Tibetan name of its own: it is
   "the chos spyod, edited". A Tibetan book would have a title that names the
   edition.
9. **Arabic digits appear in the Tibetan line** as jump-link page numbers and
   under titles. A Tibetan reader would expect ༡༢༣. This was a rendering
   compromise (Monlam's digits clipped), not a choice, and it is the most
   visible un-Tibetan element in the running text.
10. **English intrudes in three places**: the TODO stubs (temporary), the
    English TOC and key page (deliberate and separate), and the Annotations
    page's notes, which are in English. Notes on Tibetan text for Tibetan
    readers should be in Tibetan; the short form is, the long form is not.
11. **The zur yig is a real Tibetan genre**, the supplementary sheet, and
    the book treats it as one: separate section, its own divider, sourced
    additions. Good.
12. **No Tibetan-language front matter.** Acknowledgements, key, TOC are
    English. A monk at Ka-Nying who does not read English is served by the
    Tibetan text and nothing else.

**Verdict: the text layer is deeply Tibetan; the apparatus layer is
English-first.** For the Gomde reader that is right. For the shedra monk it
leaves the book half-explained.

**Three moves:** find a way back to Tibetan numerals (a digits-only subset
of a face whose digits render); write the Annotations' long notes in Tibetan
as well; give the edition a Tibetan name and a Tibetan colophon.

---

## 8. Accessibility for non-native Tibetans

*The Gomde practitioner who reads Tibetan slowly, or not at all, and chants
by ear.*

1. **The English TOC with glosses is the main aid**, and it is substantial:
   131 entries, all glossed but three. It tells a Westerner what each prayer
   is. It does not tell them what it is for or when it is recited.
2. **Links to translations exist for 14 of 131 entries**, to Lotsawa House
   and Lhasey Lotsawa. Both sites hold far more of this book than 14 texts.
   This is the cheapest large improvement available.
3. **No transliteration anywhere.** A reader who chants from Wylie or
   phonetics has nothing. Adding a phonetic layer would double the book and
   is probably out of scope, but a toggle to show Wylie for mantras alone
   would serve many.
4. **Sanskrit mantras are in Tibetan script only.** The non-native reader
   who knows a mantra in IAST cannot find it by eye.
5. **The written-out refrains are a real accessibility feature**, as much for
   the slow reader as for the group.
6. **Jump labels are Tibetan.** A reader who cannot read the destination's
   opening words gets only a page number. English glosses on hover do not
   exist in Books.
7. **Reading preference for green yig chung** helps distinguish instruction
   from recitation for a reader who cannot tell them by content. It is
   hidden behind the key page.
8. **The key page is in clear English** and explains the whole system in a
   page. It is the non-native reader's best friend and they will not find it
   unless they browse the TOC.
9. **No glossary, no pronunciation guide, no introduction** to what a chos
   spyod is, how Ka-Nying uses it, or what the routes are. The acknowledgements
   page is the only prose.
10. **Search in Books works on Tibetan text** as far as is known, but nobody
    has tested it, and a non-native reader cannot type Tibetan anyway.
11. **Page numbers are the bridge to the English chantbooks** (Lumbini 2024
    and the Ka-Nying English books) that non-natives actually hold. The book
    does not mention that these exist or map to them.
12. **Accessibility metadata is present and honest** (textual, visual,
    structural navigation). It is metadata for catalogues, not help for the
    reader.

**Verdict: the book is for people who read Tibetan. It says so implicitly
and serves them well.** For the Gomde practitioner it is a beautiful thing
they mostly cannot use without a teacher beside them.

**Three moves:** fill the translation links (both sites, all texts that
exist there); add a one-page English introduction to the routes; consider a
Wylie toggle for mantras only.

---

## 9. EPUB and eBook best practices

*Measured against what a publisher's production department would require.*

1. **Valid EPUB 2 at 0 errors, 0 warnings**, from 2,083 errors a week ago.
   The book is now a well-formed object, not a Calibre export.
2. **EPUB 2 is a deliberate choice for Books compatibility** and the record
   says so. It forecloses pop-up footnotes, media overlays (E6), and the
   accessibility metadata proper. Books and Thorium both handle EPUB 3 well
   today; the reason to stay on 2 is thin and should be re-examined before
   the next major version.
3. **Fonts are embedded, licensed and documented**, except one: Courier New
   is a Microsoft font and its redistribution licence is not in the tree.
   It is used for one thing, the colophon's version stamp. Replace it with a
   system monospace and drop 672 KB and a licence risk.
4. **Image weight is out of proportion.** Three 600-pixel line drawings
   total 2.4 MB, more than the Tibetan font. They are JPEGs of line art at
   high quality; as greyscale PNG or lower-quality JPEG they would be a tenth
   the size. The cover at 1245×1587 is the right size for stores.
5. **Metadata is minimal**: title, one creator, language, one subject, no
   description, no publisher, no rights statement, no ISBN or edition
   statement, no English title. A store or catalogue would show almost
   nothing.
6. **The identifier scheme is thought through**: a stable UUID for releases,
   derived UUIDs for dev builds so Books treats them as separate books. That
   solved a real problem and is documented.
7. **The NCX is complete and renumbered by tool.** The `<guide>` has the
   five references a reader uses. Cover is declared in metadata.
8. **JavaScript in an EPUB 2** for the yig chung preference is unusual and
   works in Books. It degrades cleanly where scripts do not run. Kindle would
   strip it; the book does not target Kindle and says so nowhere.
9. **Language tagging** is `bo` on the package and on the two English pages'
   Tibetan samples; the ten prayer files carry `xml:lang` at the root. Good.
10. **File size 4.2 MB** is fine for phones. Half of it is unnecessary
    (Courier New and the JPEGs).
11. **Validation runs in CI on every push**, with the book's own structural
    checks before it. This is beyond what most publishers do.
12. **No reading-system matrix is recorded.** Books on iPad is the test bed;
    Thorium was used once for fonts. Android readers, Kobo, Calibre viewer:
    unknown. The README says "can be opened on macOS" as if that were news.
13. **The dev-build watermark ("Do not ship") lives in pack.sh output**, not
    in the book. A dev build that leaks looks identical to a release except
    for its build number.

**Verdict: technically clean, commercially undressed.** A production
department would pass it on validation and send it back on metadata, image
weight and font licensing.

**Three moves:** drop Courier New; recompress the three line drawings; write
the metadata a store would need.

---

## 10. Engineering, process and release

*Can this book be maintained by someone other than its author and their
assistant, and can it be released?*

1. **The source of truth is plain files in git**, edited in an editor and
   built by a script. The Calibre era is over and WORKFLOW.md says how to
   work. This is the right shape for a long-lived book.
2. **The toolchain is real**: check.py (structure), nav.py (navigation),
   ncx_playorder.py, jewels.py (generated page), fmt.py (layout), pack.sh
   (build), extract_text.py (identity), compare_source.py (variants). Each
   has a docstring that explains why it exists.
3. **CI enforces the gates** and went from red to green on its first day
   because the local report had been ignored. The lesson is recorded: a
   report nobody reads is not a gate.
4. **There are no unit tests** (D1). The tools are tested by running them on
   the book. When nav.py's scope rule broke after the merge, only CI caught
   it, by accident of a strict grep. A dozen small tests on fixture snippets
   would have caught it in seconds.
5. **Documentation is unusually rich**: WORKFLOW.md, a 1,200-line TODO.md
   with reasoning, a stylesheet that is 18% comment, commit messages that
   explain the why. The risk is the opposite of the usual one: the reasoning
   is so voluminous that the next person will not read it.
6. **TODO.md is a ledger, not a plan.** 19 open items, each with paragraphs
   of context, no priority, no owner, no target version. Good memory, poor
   steering.
7. **The GitHub issues were 48 open from 2023** until today; 27 were already
   done. Two tracking systems (issues and TODO.md) drifted apart for three
   years. Pick one.
8. **Release process is manual and undocumented as a checklist.** pack.sh
   builds; who bumps the version, writes release notes, uploads to the
   WordPress site, and updates the QR target is not written down.
9. **Version 1.1 has been "in progress" through 211 commits.** No tag marks a
   release; no changelog exists for readers. A reader with an old copy has no
   way to know what changed.
10. **Distribution is a WordPress URL and a QR code**, plus "click here to
    report errors". Fine for a sangha. There is no mechanism for readers to
    learn a new version exists.
11. **The author is the only reviewer of Tibetan content.** The lama check
    is planned for one prayer. A second Tibetan-reading eye on the whole
    book, even once, is the biggest single quality lever left.
12. **Working habits are recorded as conventions** (G12): ids, links,
    headings, one concern per commit. Following them is voluntary; nothing
    checks id conventions, and five coexist (C1, G6).
13. **Private and work concerns are separated correctly**: the personal
    knowledge base is elsewhere, this repo holds only the book.

**Verdict: a well-engineered solo project.** Everything needed to hand it
over exists except tests, a release checklist, and a second reader.

**Three moves:** write the release checklist and tag 1.1 when the stubs are
gone; add fixture tests for nav.py's rules; close the GitHub issue tracker
or make it the only one.

---

## The ten actions that matter most, across all perspectives

Ordered by what a reciting reader would notice, then by risk.

1. **Get a second Tibetan reader through the whole text once**, mantras and
   refrains first. Everything else is polish next to this.
2. **Fix or annotate the two known probable errors** from the fourth-printing
   comparison.
3. **Walk the Thugs sgrub, Kilaya and Narak sequences** the way Tara was
   walked, and fill the "verified in practice" ledger.
4. **Fill the translation links** for every text Lotsawa House or Lhasey
   Lotsawa holds.
5. **Find a way back to Tibetan numerals** in jump labels and under titles.
6. **Raise the page-number size** under titles to something legible.
7. **Drop Courier New and recompress the line drawings**: half the file and a
   licence risk, for an afternoon's work.
8. **Design the title page** and give the edition a name, in Tibetan and
   English, with the printing it follows.
9. **Write the store metadata** and a one-page English introduction to the
   routes.
10. **Write the release checklist, tag 1.1, and reconcile the two trackers.**

Three things the book already does better than any Tibetan eBook I know of,
and should not lose: the two-colour, shape-first mark system; the head-line
arithmetic in the typography; and the tooling that proves every push has not
broken the text.
