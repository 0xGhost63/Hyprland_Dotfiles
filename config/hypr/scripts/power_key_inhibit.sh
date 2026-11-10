#!/usr/bin/env bash

if pgrep -f "systemd-inhibit.*handle-power-key.*Hyprland power key" >/dev/null 2>&1; then
    exit 0
fi

exec systemd-inhibit \
    --what=handle-power-key \
    --mode=block \
    --who="Hyprland power key" \
    --why="Handle the power button through Hyprland instead of logind" \
    python3 "$HOME/.config/hypr/scripts/power_key_monitor.py"
