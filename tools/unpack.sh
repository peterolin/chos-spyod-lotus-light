#!/usr/bin/env bash
# Import an .epub into src/, replacing its contents.
#
#   tools/unpack.sh path/to/some.epub
#
# You should rarely need this. src/ is the source of truth and is edited
# directly in VSCode. Use this only to import an EPUB produced elsewhere
# (e.g. a legacy Calibre-era file), and always from a CLEAN git tree so
# that `git diff` shows exactly what the import changed.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC="$REPO/src"
EPUB="${1:-}"

[ -n "$EPUB" ] || { echo "usage: tools/unpack.sh <file.epub>" >&2; exit 1; }
[ -f "$EPUB" ] || { echo "error: no such file: $EPUB" >&2; exit 1; }

if [ -n "$(cd "$REPO" && git status --porcelain -- src)" ]; then
  echo "error: src/ has uncommitted changes." >&2
  echo "       Commit or stash them first, or this import will destroy them." >&2
  exit 1
fi

rm -rf "$SRC"
mkdir -p "$SRC"
unzip -qo "$EPUB" -d "$SRC"

echo "imported $EPUB -> src/  ($(find "$SRC" -type f | wc -l | tr -d ' ') files)"
echo "review with: git status && git diff -- src"
