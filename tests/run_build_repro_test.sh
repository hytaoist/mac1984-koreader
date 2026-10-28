#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "$TMP_DIR"' EXIT

cd "$PROJECT_DIR"
./build.sh >/dev/null
cp dist/SHA256SUMS "$TMP_DIR/first.sums"
cp dist/*.zip "$TMP_DIR/"

./build.sh >/dev/null
cmp -s "$TMP_DIR/first.sums" dist/SHA256SUMS
for archive in dist/*.zip; do
    cmp -s "$TMP_DIR/$(basename "$archive")" "$archive"
done

printf 'build reproducibility test OK\n'
