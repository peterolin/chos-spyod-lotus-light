#!/usr/bin/env bash
# Build build/<name>.epub from src/.
#
# src/ is the source of truth. This script is the ONLY way an .epub
# should come into existence in this repo.
#
# VERSION, YEAR, BUILD:
# These placeholders are filled in on a staged copy, so src keeps them and the
# tree stays clean across builds:
#
#   {{VERSION}}  read from the VERSION file at the repo root. Set BY HAND at
#                release — it is the number readers see, so it should mean
#                something to them, which a build counter cannot.
#   {{YEAR}}     the year at build time, so the book stops claiming 2023.
#   {{BUILD}}    an automatic counter from .buildnum (git-ignored, and kept
#                outside build/ so wiping output cannot reset it). Appears on
#                the key page and in the metadata: it is what identifies a
#                build in a bug report.
#
# METADATA — the compatible choices:
# The package stays EPUB 2.0 with its NCX. EPUB 2 is read by essentially
# everything and converts to Kindle far more reliably than EPUB 3, which
# matters more here than any EPUB 3 feature would gain.
#
# EPUB 3 defines the Release Identifier as dc:identifier + dcterms:modified:
# the identifier stays STABLE and the modified date marks each revision. So a
# release build leaves the identifier exactly as src has it, and only bumps
# dcterms:modified. Version metadata is written EPUB 2 style
# (<meta name=... content=...>), which EPUB 2 readers understand.
#
# --dev DEFEATS that on purpose. Apple Books keys its library on the
# identifier, so re-importing a file it has seen shows the CACHED book and
# your CSS changes appear not to have happened. --dev suffixes the identifier
# with a hash of src/, making each changed build a different book to Books.
# Never ship a --dev build: to a standards-compliant reader it is a separate
# publication rather than an update. tools/preview.sh passes it for you.
#
#   tools/pack.sh                 release build — stable identifier
#   tools/pack.sh --dev           dev build — identifier busted per content
#   tools/pack.sh --stamp-title   also append the build to the visible title
set -euo pipefail

STAMP_TITLE=0
DEV=0
for arg in "$@"; do
  case "$arg" in
    --stamp-title) STAMP_TITLE=1 ;;
    --dev) DEV=1 ;;
    *) echo "usage: pack.sh [--dev] [--stamp-title]" >&2; exit 2 ;;
  esac
done

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/src"
OUT="$REPO/build/Ka-Nying-Chos-spyod.epub"

[ -d "$SRC" ] || { echo "error: no src/ — run tools/unpack.sh first" >&2; exit 1; }
[ -f "$SRC/mimetype" ] || { echo "error: src/mimetype missing" >&2; exit 1; }
[ -f "$SRC/content.opf" ] || { echo "error: src/content.opf missing" >&2; exit 1; }

# Hash of every source file's name and contents. Sorted and byte-stable, so
# it depends on content alone — not on file order, mtimes or build host.
HASH="$(cd "$SRC" && find . -type f ! -name '.DS_Store' -print0 \
        | LC_ALL=C sort -z \
        | xargs -0 shasum -a 256 \
        | shasum -a 256 | cut -c1-8)"
BUILD="$(date -u +%Y%m%d.%H%M%S)"

# Monotonic build counter. Kept OUTSIDE build/, so wiping build output does
# not reset the version the book displays.
COUNTER="$REPO/.buildnum"
N=0
[ -f "$COUNTER" ] && N="$(tr -cd '0-9' < "$COUNTER")"
N=$(( ${N:-0} + 1 ))
printf '%s\n' "$N" > "$COUNTER"

# The reader-facing version is editorial, so it is read, never generated.
VERSION_FILE="$REPO/VERSION"
[ -f "$VERSION_FILE" ] || { echo "error: no VERSION file at repo root" >&2; exit 1; }
VERSION="$(grep -v '^[[:space:]]*#' "$VERSION_FILE" | tr -d '[:space:]' | head -c 32)"
[ -n "$VERSION" ] || { echo "error: VERSION file has no version in it" >&2; exit 1; }

YEAR="$(date +%Y)"
STAMP="${VERSION}+${N}+${HASH}"

# Stage a copy so the stamp never touches src/.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
# The trailing /. copies dotfiles (META-INF) too.
cp -R "$SRC"/. "$STAGE"/
find "$STAGE" -name '.DS_Store' -delete

# Fill the {{VERSION}} / {{YEAR}} placeholders in the staged title pages.
python3 - "$STAGE" "$VERSION" "$YEAR" "$N" <<'FILL'
import pathlib, sys
stage, version, year, build = pathlib.Path(sys.argv[1]), *sys.argv[2:5]
subs = {"{{VERSION}}": version, "{{YEAR}}": year, "{{BUILD}}": build}
hits = 0
for f in sorted(list(stage.rglob("*.htm")) + list(stage.rglob("*.xhtml"))):
    t = f.read_text(encoding="utf-8")
    if not any(k in t for k in subs):
        continue
    for k, v in subs.items():
        t = t.replace(k, v)
    f.write_text(t, encoding="utf-8")
    hits += 1
if hits == 0:
    sys.exit("error: no {{VERSION}}/{{YEAR}}/{{BUILD}} placeholder found to fill")
FILL

STAMP_TITLE="$STAMP_TITLE" DEV="$DEV" STAMP="$STAMP" VERSION="$VERSION" \
BUILD="$BUILD" HASH="$HASH" \
python3 - "$STAGE/content.opf" <<'PY'
import os, re, sys

path = sys.argv[1]
stamp = os.environ["STAMP"]            # version+build+hash, for the metadata
version = os.environ["VERSION"]        # the reader-facing version
hash8 = os.environ["HASH"]
dev = os.environ["DEV"] == "1"
stamp_title = os.environ["STAMP_TITLE"] == "1"
opf = open(path, encoding="utf-8").read()

# Targeted regex edits, not an XML round-trip: re-serialising this OPF would
# rewrite its namespace prefixes and Calibre-specific metadata wholesale.

# 1. The identifier. A release build leaves it STABLE — that is the whole
#    point of an identifier, and with dcterms:modified below it forms the
#    Release Identifier that marks this as a revision of the same book.
#    Only --dev suffixes it, to force Apple Books past its cache.
m = re.search(r'\bunique-identifier="([^"]+)"', opf)
if not m:
    sys.exit("error: package has no unique-identifier attribute")
uid = m.group(1)

ident = re.compile(
    r'(<dc:identifier\b[^>]*\bid="%s"[^>]*>)(.*?)(</dc:identifier>)' % re.escape(uid),
    re.S,
)
m2 = ident.search(opf)
if not m2:
    sys.exit(f"error: no <dc:identifier id=\"{uid}\"> to stamp")

# Strip any suffix a previous --dev build left, then re-add only for --dev.
base = re.sub(r'-b[0-9a-f]{8}$', '', m2.group(2).strip())
new_id = f"{base}-b{hash8}" if dev else base
opf = ident.sub(lambda _m: f"{_m.group(1)}{new_id}{_m.group(3)}", opf, count=1)

# 2. dcterms:modified must be ISO 8601 UTC. The value carried in src is
#    '2023-09-23T11:05:00:00Z' — malformed, an extra :00 — so it is replaced
#    rather than corrected in place. Built from BUILD (a UTC timestamp), NOT
#    from the display version, which is now 1.0.<n> and carries no date.
b = os.environ["BUILD"]          # YYYYMMDD.HHMMSS
now = "%s-%s-%sT%s:%s:%sZ" % (
    b[0:4], b[4:6], b[6:8], b[9:11], b[11:13], b[13:15],
)
modified = re.compile(r'(<meta\b[^>]*\bproperty="dcterms:modified"[^>]*>)(.*?)(</meta>)', re.S)
if modified.search(opf):
    opf = modified.sub(lambda _m: f"{_m.group(1)}{now}{_m.group(3)}", opf, count=1)
else:
    opf = opf.replace(
        "</metadata>",
        f'  <meta property="dcterms:modified">{now}</meta>\n  </metadata>', 1)

# 3. Version metadata, EPUB 2 style (name/content), which EPUB 2 readers
#    understand — <meta property=...> is an EPUB 3 construct.
opf = re.sub(r'\s*<meta name="(?:build|version)" content="[^"]*"/>', "", opf)
opf = opf.replace("</metadata>",
                  f'  <meta name="version" content="{version}"/>\n'
                  f'  <meta name="build" content="{stamp}"/>\n  </metadata>', 1)

# 4. dc:date. src carries '0101-01-01T00:00:00+00:00', which is nonsense; in
#    EPUB 2 this is the edition's date, so write the build date as W3CDTF.
day = "%s-%s-%s" % (b[0:4], b[4:6], b[6:8])
date = re.compile(r'(<dc:date\b[^>]*>)(.*?)(</dc:date>)', re.S)
if date.search(opf):
    opf = date.sub(lambda _m: f"{_m.group(1)}{day}{_m.group(3)}", opf, count=1)

# 5. Optional: put the build in the title, so a library listing tells builds
#    apart at a glance.
if stamp_title:
    opf = re.sub(r'(<dc:title>)(.*?)(</dc:title>)',
                 lambda _m: "%s%s [%s]%s" % (
                     _m.group(1), re.sub(r'\s*\[[\d.+a-f]+\]$', '', _m.group(2)),
                     stamp, _m.group(3)),
                 opf, count=1, flags=re.S)

open(path, "w", encoding="utf-8").write(opf)
PY

mkdir -p "$REPO/build"
rm -f "$OUT"

cd "$STAGE"

# The spec requires 'mimetype' to be the FIRST entry and STORED
# (uncompressed, -0). Get this wrong and iBooks/Kindle reject the file.
zip -q -X -0 "$OUT" mimetype

# Everything else, deflated. -D omits directory entries; junk files excluded.
zip -q -X -r -9 -D "$OUT" . \
  -x mimetype \
  -x '.DS_Store' -x '*/.DS_Store' \
  -x '.git*' -x '*/.git*'

printf '%s\n' "$STAMP" > "$REPO/build/version.txt"

echo "built  $OUT"
echo "size   $(du -h "$OUT" | cut -f1)"
echo "files  $(unzip -l "$OUT" | tail -1 | awk '{print $2}')"
echo "build  $STAMP"
echo "shown  $VERSION $YEAR   (title pages) · build $N (key page)"
if [ "$DEV" = "1" ]; then
  echo "mode   DEV — identifier busted to defeat the Books cache. Do not ship."
else
  echo "mode   release — identifier stable, dcterms:modified bumped."
fi

# Sanity: first entry must be an uncompressed mimetype.
first="$(unzip -l "$OUT" | sed -n '4p' | awk '{print $NF}')"
[ "$first" = "mimetype" ] || { echo "FAIL: first entry is '$first', not mimetype" >&2; exit 1; }
echo "ok     mimetype is first entry and stored"
