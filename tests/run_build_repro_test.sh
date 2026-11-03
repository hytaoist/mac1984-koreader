#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cd "$PROJECT_DIR"
./build.sh >/dev/null
VERSION="$(lua -e 'io.write(assert(dofile("plugin/_meta.lua")).version)')"
STANDALONE_ARCHIVE="dist/mac1984-koreader-v$VERSION.zip"
cp dist/SHA256SUMS "$TMP_DIR/first.sums"
cp dist/*.zip "$TMP_DIR/"

if ! unzip -Z1 "$STANDALONE_ARCHIVE" \
    | grep -q '^mac1984-koreader/DEVELOPMENT.md$'; then
    printf 'Standalone archive validation failed: missing DEVELOPMENT.md\n' >&2
    exit 1
fi

./build.sh >/dev/null
cmp -s "$TMP_DIR/first.sums" dist/SHA256SUMS
for archive in dist/*.zip; do
    cmp -s "$TMP_DIR/$(basename "$archive")" "$archive"
done

printf 'build reproducibility test OK\n'
