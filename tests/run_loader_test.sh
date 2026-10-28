#!/usr/bin/env bash
set -eu

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
TMP_DIR="$(mktemp -d)"
if [ "${KEEP_TEST_DIR:-0}" != "1" ]; then
    trap 'rm -rf "$TMP_DIR"' EXIT
else
    printf 'Test directory: %s\n' "$TMP_DIR"
fi

PLUGIN_DIR="$TMP_DIR/mac1984-koreader.koplugin"
mkdir -p "$PLUGIN_DIR/theme"
printf '_G.mac1984_loader_test_loaded = true\n' > "$PLUGIN_DIR/theme/apply.lua"

(
    cd "$PROJECT_DIR"
    lua tests/loader_test.lua "$PLUGIN_DIR"
)
