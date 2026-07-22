#!/bin/bash
# Game Mode / Ultra-Performance Toggle for Hyprland

FLAG_FILE="$HOME/.cache/gamemode_active"

if [ -f "$FLAG_FILE" ]; then
    # Game Mode is ON -> Restore normal mode
    rm -f "$FLAG_FILE"
    hyprctl reload
    notify-send -u low "Game Mode" "Performance mode disabled. Aesthetics restored."
else
    # Game Mode is OFF -> Enable Ultra-Performance mode
    touch "$FLAG_FILE"
    hyprctl --batch "\
        keyword animations:enabled 0;\
        keyword decoration:shadow:enabled 0;\
        keyword decoration:blur:enabled 0;\
        keyword general:gaps_in 0;\
        keyword general:gaps_out 0;\
        keyword general:border_size 1;\
        keyword decoration:rounding 0"
    notify-send -u low "Game Mode" "Ultra-Performance mode enabled! Blur, gaps, and animations disabled."
fi
