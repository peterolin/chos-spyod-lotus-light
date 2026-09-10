#!/usr/bin/env bash
# Build, then open in the Calibre viewer. Read-only preview.
#
# NOTE: this opens ebook-viewer, NOT the Calibre editor. Do not edit the
# built EPUB — build/ is disposable output and is not tracked by git.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VIEWER="/Applications/calibre.app/Contents/MacOS/ebook-viewer"

"$REPO/tools/pack.sh" --dev

[ -x "$VIEWER" ] || { echo "error: Calibre viewer not found at $VIEWER" >&2; exit 1; }
exec "$VIEWER" "$REPO/build/Ka-Nying-Chos-spyod.epub"
