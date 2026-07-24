#!/bin/bash
# Toggle Spaced wlogout Power Menu
if pgrep -x "wlogout" > /dev/null; then
    pkill -x "wlogout"
else
    wlogout -b 3 -c 30 -r 30 -L 150 -R 150 -T 120 -B 120 --protocol layer-shell
fi
