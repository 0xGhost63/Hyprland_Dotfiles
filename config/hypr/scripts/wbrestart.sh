#!/bin/bash

killall -9 swaync
killall -9 waybar

nohup swaync >/dev/null 2>&1 &
nohup waybar >/dev/null 2>&1 &
