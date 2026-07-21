#!/bin/bash
OUT="/tmp/waybar-art.png"
playerctl -p spotify metadata --format '{{mpris:artUrl}}' --follow 2>/dev/null | while read -r ART_URL; do
    [ -z "$ART_URL" ] && continue
    if [[ "$ART_URL" == file://* ]]; then
        cp "${ART_URL#file://}" "$OUT" 2>/dev/null
    elif [[ "$ART_URL" == http*://* ]]; then
        curl -s "$ART_URL" -o "$OUT" 2>/dev/null
    fi
done
