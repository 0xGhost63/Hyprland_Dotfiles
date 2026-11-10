#!/bin/bash

if pgrep -f quicknote.py >/dev/null; then
    pkill -f quicknote.py
else
    ~/.config/hypr/scripts/quicknote.py >/dev/null 2>&1 &
fi
