#!/bin/bash

SAVE_DIR="$HOME/Pictures/Screenshots"
mkdir -p "$SAVE_DIR"

FILE_NAME="Screenshot_$(date +'%Y%m%d_%H%M%S').png"
FULL_PATH="$SAVE_DIR/$FILE_NAME"

# Run region selector and grab the screen area
if slurp | grim -g - "$FULL_PATH"; then
    cat "$FULL_PATH" | wl-copy
    notify-send "Screenshot Captured" "Saved to $FILE_NAME and copied to clipboard!" --icon=image
else
    notify-send "Screenshot Canceled" "No region selected." --icon=dialog-warning
fi
