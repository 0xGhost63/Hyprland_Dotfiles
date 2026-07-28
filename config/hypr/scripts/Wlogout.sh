#!/bin/bash
# Toggle wlogout Power Menu (Super + Esc)
# Screen: 1366x768 — margins calculated to center the 3x2 button grid
if pgrep -x "wlogout" > /dev/null; then
    pkill -x "wlogout"
else
    wlogout \
        --layout ~/.config/wlogout/layout \
        --css ~/.config/wlogout/style.css \
        --protocol layer-shell \
        -b 3 -c 20 -r 20 \
        -L 283 -R 283 -T 224 -B 224
fi
