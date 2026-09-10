#!/usr/bin/env bash
# Build build/<name>.epub from src/.
#
# src/ is the source of truth. This script is the ONLY way an .epub
# should come into existence in this repo.
#
# VERSION STAMPING — why this exists:
# Apple Books keys its library on the OPF unique identifier. Re-importing a
# file whose identifier it has seen before shows the CACHED book, so CSS and
# markup changes appear not to have happened. Every build therefore stamps
# the output with:
#
#   version     <utc timestamp>+<content hash>   always increases
#   identifier  <base uuid>-b<content hash>      changes iff src/ changed
#
# Deriving the identifier from a hash of src/ (rather than bumping it every
# run) means a real change always opens fresh, while rebuilding unchanged
# content does not litter the Books library with duplicate copies.
#
# src/ is never modified: the stamp is applied to a staged copy.
#
#   tools/pack.sh                 build, stamped
#   tools/pack.sh --stamp-title   also append the build to the visible title,
#                                 so several builds are told apart in a
#                                 library listing
set -euo pipefail

STAMP_TITLE=0
for arg in "$@"; do
  case "$arg" in
    --stamp-title) STAMP_TITLE=1 ;;
    *) echo "usage: pack.sh [--stamp-title]" >&2; exit 2 ;;
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
VERSION="${BUILD}+${HASH}"

# Stage a copy so the stamp never touches src/.
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
# The trailing /. copies dotfiles (META-INF) too.
cp -R "$SRC"/. "$STAGE"/
find "$STAGE" -name '.DS_Store' -delete

STAMP_TITLE="$STAMP_TITLE" VERSION="$VERSION" HASH="$HASH" \
python3 - "$STAGE/content.opf" <<'PY'
import os, re, sys

path = sys.argv[1]
version = os.environ["VERSION"]
hash8 = os.environ["HASH"]
stamp_title = os.environ["STAMP_TITLE"] == "1"
opf = open(path, encoding="utf-8").read()

# Targeted regex edits, not an XML round-trip: re-serialising this OPF would
# rewrite its namespace prefixes and Calibre-specific metadata wholesale.

# 1. The identifier Apple Books matches on. Which <dc:identifier> counts is
#    named by the package's unique-identifier attribute.
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

base = re.sub(r'-b[0-9a-f]{8}$', '', m2.group(2).strip())
opf = ident.sub(lambda _m: f"{_m.group(1)}{base}-b{hash8}{_m.group(3)}", opf, count=1)

# 2. dcterms:modified must be ISO 8601 UTC. The value carried in src is
#    '2023-09-23T11:05:00:00Z' — malformed, an extra :00 — so it is replaced
#    rather than corrected in place.
stamped = re.sub(r'\+\S+$', '', version)  # keep the timestamp half
now = "%s-%s-%sT%s:%s:%sZ" % (
    stamped[0:4], stamped[4:6], stamped[6:8],
    stamped[9:11], stamped[11:13], stamped[13:15],
)
modified = re.compile(r'(<meta\b[^>]*\bproperty="dcterms:modified"[^>]*>)(.*?)(</meta>)', re.S)
if modified.search(opf):
    opf = modified.sub(lambda _m: f"{_m.group(1)}{now}{_m.group(3)}", opf, count=1)
else:
    opf = opf.replace(
        "</metadata>",
        f'  <meta property="dcterms:modified">{now}</meta>\n  </metadata>', 1)

# 3. A human-readable build marker, so a built file can be identified.
opf = re.sub(r'\s*<meta name="build" content="[^"]*"/>', "", opf)
opf = opf.replace(
    "</metadata>", f'  <meta name="build" content="{version}"/>\n  </metadata>', 1)

# 4. Optional: put the build in the title, so a library listing tells builds
#    apart at a glance.
if stamp_title:
    opf = re.sub(r'(<dc:title>)(.*?)(</dc:title>)',
                 lambda _m: "%s%s [%s]%s" % (
                     _m.group(1), re.sub(r'\s*\[[\d.+a-f]+\]$', '', _m.group(2)),
                     version, _m.group(3)),
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

printf '%s\n' "$VERSION" > "$REPO/build/version.txt"

echo "built  $OUT"
echo "size   $(du -h "$OUT" | cut -f1)"
echo "files  $(unzip -l "$OUT" | tail -1 | awk '{print $2}')"
echo "build  $VERSION"

# Sanity: first entry must be an uncompressed mimetype.
first="$(unzip -l "$OUT" | sed -n '4p' | awk '{print $NF}')"
[ "$first" = "mimetype" ] || { echo "FAIL: first entry is '$first', not mimetype" >&2; exit 1; }
echo "ok     mimetype is first entry and stored"
