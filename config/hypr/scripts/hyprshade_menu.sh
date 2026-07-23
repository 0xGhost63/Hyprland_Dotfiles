#!/bin/bash
# Hyprland Display & Theme Menu (Night Light, Dark/Light Mode)

OPTIONS="Night Light (Warm 3500K)
Sunset Mode (Medium 4500K)
Clear Night Light (Normal)
Dark Mode (System)
Light Mode (System)"

selected=$(echo "$OPTIONS" | rofi -dmenu -p "Display & Theme" -i)

case "$selected" in
    "Night Light (Warm 3500K)")
        pkill hyprsunset 2>/dev/null
        pkill -9 hyprsunset 2>/dev/null
        hyprsunset -t 3500 >/dev/null 2>&1 &
        hyprctl reload
        notify-send -u low "Night Light" "Applied Warm 3500K Filter"
        ;;
    "Sunset Mode (Medium 4500K)")
        pkill hyprsunset 2>/dev/null
        pkill -9 hyprsunset 2>/dev/null
        hyprsunset -t 4500 >/dev/null 2>&1 &
        hyprctl reload
        notify-send -u low "Night Light" "Applied Medium 4500K Filter"
        ;;
    "Clear Night Light (Normal)")
        pkill hyprsunset 2>/dev/null
        pkill -9 hyprsunset 2>/dev/null
        hyprctl keyword decoration:screen_shader "" 2>/dev/null
        hyprctl reload
        notify-send -u low "Night Light" "Restored Normal Display"
        ;;
    "Dark Mode (System)")
        bash "$HOME/dotfiles/config/hypr/scripts/theme_toggle.sh" dark
        hyprctl reload
        ;;
    "Light Mode (System)")
        bash "$HOME/dotfiles/config/hypr/scripts/theme_toggle.sh" light
        hyprctl reload
        ;;
esac
