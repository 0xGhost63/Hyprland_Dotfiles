#!/bin/bash

# ==========================================
# GHOST'S STARTUP APPS LAUNCH SCRIPT
# ==========================================
# Modify the workspace numbers or launch commands below
# to customize your startup workflow.

# 1. Brave Browser
BRAVE_WS=1
BRAVE_CMD="brave"

# 2. Spotify Music
SPOTIFY_WS=2
SPOTIFY_CMD="spotify"

# 3. WhatsApp Client
WHATSAPP_WS=6
WHATSAPP_CMD="elecwhat"

# ==========================================
# LAUNCH EXECUTION
# ==========================================

echo "Launching Brave on Workspace ${BRAVE_WS}..."
hyprctl dispatch exec "${BRAVE_CMD}"

echo "Launching Spotify on Workspace ${SPOTIFY_WS}..."
hyprctl dispatch exec "${SPOTIFY_CMD}"

echo "Launching WhatsApp on Workspace ${WHATSAPP_WS}..."
hyprctl dispatch exec "${WHATSAPP_CMD}"

echo "Startup applications initialized!"
