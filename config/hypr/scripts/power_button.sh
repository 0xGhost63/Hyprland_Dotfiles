#!/usr/bin/env bash
set -u

STATE_FILE="${XDG_RUNTIME_DIR:-/tmp}/hypr-power-button.state"
HOLD_SECONDS="${HOLD_SECONDS:-4}"
LOCK_CMD="${LOCK_CMD:-qs -c ii ipc call lock activate || pidof hyprlock || hyprlock}"
POWEROFF_CMD="${POWEROFF_CMD:-systemctl poweroff || loginctl poweroff}"

case "${1:-}" in
    press)
        token="$(date +%s%N)"
        printf '%s\n' "$token" > "$STATE_FILE"
        (
            sleep "$HOLD_SECONDS"
            if [ "$(cat "$STATE_FILE" 2>/dev/null)" = "$token" ]; then
                rm -f "$STATE_FILE"
                eval "$POWEROFF_CMD"
            fi
        ) &
        ;;
    release)
        token="$(cat "$STATE_FILE" 2>/dev/null || true)"
        if [ -n "$token" ]; then
            rm -f "$STATE_FILE"
            eval "$LOCK_CMD"
        fi
        ;;
esac
