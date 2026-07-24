#!/usr/bin/env python3
# Universal Media Thumbnail Fetcher for Waybar
# Supports Spotify, Brave / Chrome / Firefox (YouTube & web media), mpv / yt-x, and all MPRIS players.
# Output is saved to /tmp/waybar-art.png ONLY when media is actively playing.

import os
import re
import time
import subprocess
import urllib.request

OUT_FILE = "/tmp/waybar-art.png"
LAST_URL = ""

def extract_youtube_thumb(text):
    if not text:
        return None
    match = re.search(r'(?:v=|\/|be\/)([a-zA-Z0-9_-]{11})', text)
    if match:
        vid = match.group(1)
        return f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
    return None

def get_active_media_art():
    # 1. Query playerctl for all MPRIS players
    try:
        proc = subprocess.run(
            ["playerctl", "-a", "metadata", "--format", "{{status}}\t{{playerName}}\t{{mpris:artUrl}}\t{{xesam:url}}"],
            capture_output=True, text=True, timeout=2
        )
        if proc.stdout.strip():
            lines = proc.stdout.strip().split("\n")
            for line in lines:
                parts = line.split("\t")
                if len(parts) >= 1:
                    status = parts[0].strip().lower()
                    player = parts[1].strip() if len(parts) > 1 else ""
                    art_url = parts[2].strip() if len(parts) > 2 else ""
                    page_url = parts[3].strip() if len(parts) > 3 else ""

                    if status == "playing":
                        # Direct artUrl (Spotify, local file, or browser thumbnail)
                        if art_url:
                            if art_url.startswith("file://"):
                                local_path = art_url.replace("file://", "")
                                if os.path.exists(local_path):
                                    return ("local", local_path)
                            elif art_url.startswith("http://") or art_url.startswith("https://"):
                                return ("remote", art_url)

                        # YouTube fallback via page_url or art_url
                        yt_thumb = extract_youtube_thumb(page_url) or extract_youtube_thumb(art_url)
                        if yt_thumb:
                            return ("remote", yt_thumb)

                        return ("none", None)
    except Exception:
        pass

    # 2. Check if mpv (used by yt-x) is running
    try:
        ps_proc = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=2)
        for line in ps_proc.stdout.split("\n"):
            if "mpv " in line and "grep" not in line:
                yt_thumb = extract_youtube_thumb(line)
                if yt_thumb:
                    return ("remote", yt_thumb)
    except Exception:
        pass

    return (None, None)

def update_art():
    global LAST_URL
    kind, url = get_active_media_art()

    if kind == "remote" and url:
        if url != LAST_URL or not os.path.exists(OUT_FILE):
            LAST_URL = url
            try:
                urllib.request.urlretrieve(url, OUT_FILE)
            except Exception:
                if os.path.exists(OUT_FILE):
                    os.remove(OUT_FILE)
    elif kind == "local" and url:
        if url != LAST_URL or not os.path.exists(OUT_FILE):
            LAST_URL = url
            try:
                subprocess.run(["cp", url, OUT_FILE], stderr=subprocess.DEVNULL)
            except Exception:
                if os.path.exists(OUT_FILE):
                    os.remove(OUT_FILE)
    else:
        # No active playing media or no thumbnail available
        if os.path.exists(OUT_FILE):
            try:
                os.remove(OUT_FILE)
            except Exception:
                pass
        LAST_URL = ""

if __name__ == "__main__":
    while True:
        update_art()
        time.sleep(1)
