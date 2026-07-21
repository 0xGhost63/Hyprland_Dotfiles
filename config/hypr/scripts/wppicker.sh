#!/bin/bash

# === CONFIG ===
WALLPAPER_DIR="$HOME/Pictures/wallpapers"
SYMLINK_PATH="$HOME/.config/hypr/current_wallpaper"

cd "$WALLPAPER_DIR" || exit 1

# === handle spaces name
IFS=$'\n'

# === ICON-PREVIEW SELECTION WITH ROFI, SORTED BY NEWEST ===
SELECTED_WALL=$(for a in $(ls -t *.jpg *.png *.gif *.jpeg 2>/dev/null); do printf '%s\0icon\x1f%s\n' "$a" "$WALLPAPER_DIR/$a"; done | rofi -dmenu -p "Wallpaper")
[ -z "$SELECTED_WALL" ] && exit 1
SELECTED_PATH="$WALLPAPER_DIR/$SELECTED_WALL"

# === CREATE SYMLINK ===
mkdir -p "$(dirname "$SYMLINK_PATH")"
ln -sf "$SELECTED_PATH" "$SYMLINK_PATH"
ln -sf "$SELECTED_PATH" "$HOME/.config/hypr/current_wallpaper.png"

# === ENSURE AWWW-DAEMON IS RUNNING ===
if command -v awww-daemon &>/dev/null && ! pgrep -x awww-daemon &>/dev/null; then
    pkill swaybg 2>/dev/null
    awww-daemon &
    sleep 0.5
fi

# === RUN MATUGEN FOR SMART COLOR GENERATION AND ANIMATED TRANSITION ===
if command -v matugen &>/dev/null; then
    matugen image --prefer saturation "$SELECTED_PATH"
elif command -v awww &>/dev/null; then
    awww img --transition-type any --transition-fps 60 "$SELECTED_PATH"
else
    pkill swaybg 2>/dev/null
    while pgrep -x swaybg > /dev/null; do sleep 0.1; done
    swaybg -m fill -i "$SELECTED_PATH" &
    disown
fi

