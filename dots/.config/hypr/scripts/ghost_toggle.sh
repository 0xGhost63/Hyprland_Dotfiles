#!/bin/bash
# Toggle Ghost Desktop Mascot

if pgrep -f "ghost_mascot.py" >/dev/null; then
    pkill -f "ghost_mascot.py"
else
    python3 "$HOME/dotfiles/config/hypr/scripts/ghost_mascot.py" &
fi
