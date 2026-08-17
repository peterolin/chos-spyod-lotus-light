#!/usr/bin/env bash
# Build build/<name>.epub from src/.
#
# src/ is the source of truth. This script is the ONLY way an .epub
# should come into existence in this repo.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/src"
OUT="$REPO/build/Ka-Nying-Chos-spyod.epub"

[ -d "$SRC" ] || { echo "error: no src/ — run tools/unpack.sh first" >&2; exit 1; }
[ -f "$SRC/mimetype" ] || { echo "error: src/mimetype missing" >&2; exit 1; }

mkdir -p "$REPO/build"
rm -f "$OUT"

cd "$SRC"

# The spec requires 'mimetype' to be the FIRST entry and STORED
# (uncompressed, -0). Get this wrong and iBooks/Kindle reject the file.
zip -q -X -0 "$OUT" mimetype

# Everything else, deflated. -D omits directory entries; junk files excluded.
zip -q -X -r -9 -D "$OUT" . \
  -x mimetype \
  -x '.DS_Store' -x '*/.DS_Store' \
  -x '.git*' -x '*/.git*'

echo "built  $OUT"
echo "size   $(du -h "$OUT" | cut -f1)"
echo "files  $(unzip -l "$OUT" | tail -1 | awk '{print $2}')"

# Sanity: first entry must be an uncompressed mimetype.
first="$(unzip -l "$OUT" | sed -n '4p' | awk '{print $NF}')"
[ "$first" = "mimetype" ] || { echo "FAIL: first entry is '$first', not mimetype" >&2; exit 1; }
echo "ok     mimetype is first entry and stored"
