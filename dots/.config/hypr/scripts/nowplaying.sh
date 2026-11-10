#!/bin/bash
ACCENT='\033[38;2;137;180;250m'
RESET='\033[0m'
DIM='\033[2m'
BOLD='\033[1m'

tput civis
trap "tput cnorm; clear; exit" INT TERM

while true; do
    cols=$(tput cols)
    width=$(( cols > 46 ? 42 : cols - 4 ))
    [ "$width" -lt 20 ] && width=20

    artist=$(playerctl -p spotify metadata --format '{{ artist }}' 2>/dev/null)
    title=$(playerctl -p spotify metadata --format '{{ title }}' 2>/dev/null)
    status=$(playerctl -p spotify status 2>/dev/null)

    now=$(date +'%H:%M:%S')
    day=$(date +'%A, %d %B')

    frame=""
    frame+="${ACCENT}┌$(printf '─%.0s' $(seq 1 $width))┐${RESET}\n"
    frame+=$(printf "${ACCENT}│${RESET}  ${BOLD}%-*s${RESET}${ACCENT}│${RESET}\n" $((width-2)) "$now")
    frame+="\n"
    frame+=$(printf "${ACCENT}│${RESET}  ${DIM}%-*s${RESET}${ACCENT}│${RESET}\n" $((width-2)) "$day")
    frame+="\n"
    frame+="${ACCENT}├$(printf '─%.0s' $(seq 1 $width))┤${RESET}\n"

    if [ -n "$title" ]; then
        frame+=$(printf "${ACCENT}│${RESET}  ${DIM}%-*s${RESET}${ACCENT}│${RESET}\n" $((width-2)) "${status:-Playing}")
        frame+="\n"
        frame+=$(printf "${ACCENT}│${RESET}  %-*.*s${ACCENT}│${RESET}\n" $((width-2)) $((width-2)) "$title")
        frame+="\n"
        frame+=$(printf "${ACCENT}│${RESET}  ${DIM}%-*.*s${RESET}${ACCENT}│${RESET}\n" $((width-2)) $((width-2)) "$artist")
        frame+="\n"
    else
        frame+=$(printf "${ACCENT}│${RESET}  ${DIM}%-*s${RESET}${ACCENT}│${RESET}\n" $((width-2)) "No active playback")
        frame+="\n"
    fi

    frame+="${ACCENT}└$(printf '─%.0s' $(seq 1 $width))┘${RESET}"

    tput cup 0 0
    printf "%b" "$frame"
    tput ed

    sleep 1
done
