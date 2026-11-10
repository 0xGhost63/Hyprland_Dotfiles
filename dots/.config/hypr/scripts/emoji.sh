#!/bin/bash
# Emoji & Symbol Picker using Rofi

if command -v rofi-emoji &>/dev/null || rofi -h 2>&1 | grep -i "emoji" &>/dev/null; then
    rofi -modi emoji -show emoji -emoji-mode copy
else
    EMOJIS="😀 Happy
😃 Grinning
😂 Laughing
😍 Heart Eyes
😎 Cool
🔥 Fire
✨ Sparkles
🚀 Rocket
👻 Ghost
💀 Skull
🎉 Party
👍 Thumbs Up
❤️ Red Heart
💙 Blue Heart
💜 Purple Heart
(つ✧ω✧)つ Hug
(ノ^∇^)ノ Joy
¯\_(ツ)_/¯ Shrug
(⊙_⊙) Surprised
(ง'̀-'́)ง Fight
(┬┬﹏┬┬) Crying"

    selected=$(echo "$EMOJIS" | rofi -dmenu -p "😀 Emojis" -i | awk '{print $1}')
    if [ -n "$selected" ]; then
        echo -n "$selected" | wl-copy
    fi
fi
