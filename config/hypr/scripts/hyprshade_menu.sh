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
        if command -v hyprsunset &>/dev/null; then
            pkill hyprsunset 2>/dev/null
            hyprsunset -t 3500 &
            notify-send -u low "Night Light" "Applied Warm 3500K Filter"
        else
            notify-send "Night Light" "hyprsunset is not installed. Run: sudo pacman -S hyprsunset"
        fi
        ;;
    "Sunset Mode (Medium 4500K)")
        if command -v hyprsunset &>/dev/null; then
            pkill hyprsunset 2>/dev/null
            hyprsunset -t 4500 &
            notify-send -u low "Night Light" "Applied Medium 4500K Filter"
        else
            notify-send "Night Light" "hyprsunset is not installed. Run: sudo pacman -S hyprsunset"
        fi
        ;;
    "Clear Night Light (Normal)")
        pkill hyprsunset 2>/dev/null
        hyprctl keyword decoration:screen_shader "" 2>/dev/null
        notify-send -u low "Night Light" "Restored Normal Display"
        ;;
    "Dark Mode (System)")
        gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null
        gsettings set org.gnome.desktop.interface gtk-theme 'Sweet-Dark' 2>/dev/null
        sed -i 's/ColorScheme=.*/ColorScheme=BreezeDark/' ~/.config/kdeglobals 2>/dev/null
        sed -i 's/ColorScheme=.*/ColorScheme=BreezeDark/' ~/.config/dolphinrc 2>/dev/null
        notify-send -u low "System Theme" "Switched to Dark Mode"
        ;;
    "Light Mode (System)")
        gsettings set org.gnome.desktop.interface color-scheme 'prefer-light' 2>/dev/null
        gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita' 2>/dev/null
        sed -i 's/ColorScheme=.*/ColorScheme=BreezeLight/' ~/.config/kdeglobals 2>/dev/null
        sed -i 's/ColorScheme=.*/ColorScheme=BreezeLight/' ~/.config/dolphinrc 2>/dev/null
        notify-send -u low "System Theme" "Switched to Light Mode"
        ;;
esac
