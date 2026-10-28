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

PLUGIN_DIR="$TMP_DIR/plugin"
DATA_DIR="$TMP_DIR/koreader"
SETTINGS_DIR="$DATA_DIR/settings"

mkdir -p "$PLUGIN_DIR/assets" "$DATA_DIR/icons" "$DATA_DIR/fonts" \
    "$SETTINGS_DIR/simpleui/sui_icons/packs/Solar Mono"
cp -R "$PROJECT_DIR/plugin/." "$PLUGIN_DIR/"
cp -R "$PROJECT_DIR/assets/icons" "$PROJECT_DIR/assets/simpleui-icons" \
    "$PROJECT_DIR/assets/fonts" "$PLUGIN_DIR/assets/"
cp "$PROJECT_DIR/patches/2-mac1984.lua" "$PLUGIN_DIR/loader.lua"

printf 'STOCK\n' > "$DATA_DIR/icons/appbar.menu.svg"
printf '%s\n' \
    'return {' \
    '    ["simpleui_ui_font_name"] = "OpenDyslexic",' \
    '    ["simpleui_sysicon_menu"] = "./settings/simpleui/sui_icons/packs/Solar Mono/menu.svg",' \
    '}' \
    > "$SETTINGS_DIR/simpleui/sui_settings.lua"

(
    cd "$PROJECT_DIR"
    lua tests/deploy_test.lua "$PLUGIN_DIR" "$DATA_DIR" "$SETTINGS_DIR"
)
