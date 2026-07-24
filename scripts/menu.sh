#!/usr/bin/env bash

SCRIPTS_DIR="$HOME/.config/scripts"

options=(
    "  Power Menu"
    "  Screenshot"
    "  Volume"
    "  WiFi"
    "  Bluetooth"
    "  Calendar"
    "  Music"
    "  Battery"
)

rofi_cmd() {
    rofi -p "Menu" -dmenu -theme-str 'listview { lines: 8; }' \
        -theme-str 'textbox-prompt-colon { str: ""; }' \
        -theme "${ROFI_THEMES:-$HOME/.config/rofi}/launcher.rasi"
}

chosen=$(printf "%s\n" "${options[@]}" | rofi_cmd)

case "$chosen" in
    "  Power Menu")   bash "$HOME/.config/rofi/powermenu/type-1/powermenu.sh" ;;
    "  Screenshot")   bash "$HOME/.config/scripts/screenshot.sh" ;;
    "  Volume")       bash "$SCRIPTS_DIR/volume.sh" ;;
    "  WiFi")         bash "$SCRIPTS_DIR/wifi.sh" ;;
    "  Bluetooth")    bash "$SCRIPTS_DIR/bluetooth.sh" ;;
    "  Calendar")     bash "$SCRIPTS_DIR/calendar.sh" ;;
    "  Music")        bash "$SCRIPTS_DIR/musictl.sh" ;;
    "  Battery")      bash "$SCRIPTS_DIR/battery.sh" ;;
esac
