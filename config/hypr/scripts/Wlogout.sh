#!/bin/bash
# Toggle wlogout Power Menu (Super + Esc)
if pgrep -x "wlogout" > /dev/null; then
    pkill -x "wlogout"
else
    wlogout \
        --layout ~/.config/wlogout/layout \
        --css ~/.config/wlogout/style.css \
        --protocol layer-shell
fi
