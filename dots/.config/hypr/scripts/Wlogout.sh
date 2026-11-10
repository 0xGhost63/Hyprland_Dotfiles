#!/bin/bash
# Toggle wlogout Power Menu (Super + Esc)
# Screen: 1366x768
# Centering: margin 200px all sides → button area = 966x368, 3 cols x 2 rows
if pgrep -x "wlogout" > /dev/null; then
    pkill -x "wlogout"
else
    wlogout \
        --layout ~/.config/wlogout/layout \
        --css ~/.config/wlogout/style.css \
        --protocol layer-shell \
        -b 3 -c 10 -r 10 \
        -m 200
fi
