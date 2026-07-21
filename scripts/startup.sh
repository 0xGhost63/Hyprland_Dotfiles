#!/bin/bash

# ==========================================
# GHOST'S STARTUP APPS LAUNCH SCRIPT
# ==========================================

# 1. Brave Browser on Workspace 1
hyprctl dispatch workspace 1
hyprctl dispatch exec "brave"

# 2. Spotify Music on Workspace 2
hyprctl dispatch workspace 2
hyprctl dispatch exec "spotify-launcher"

# 3. WhatsApp Client on Workspace 6
hyprctl dispatch workspace 6
hyprctl dispatch exec "elecwhat"

echo "Startup applications initialized!"
