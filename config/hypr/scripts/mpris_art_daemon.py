#!/usr/bin/env python3
# Universal Media Thumbnail Daemon for Waybar
# Supports Spotify, Brave / Chrome / Firefox (YouTube & web media), mpv / yt-x, and all MPRIS players.
# Output is saved to /tmp/waybar-art.png for both Playing and Paused media.

import os
import re
import time
import subprocess
import urllib.request
import urllib.parse

OUT_FILE = "/tmp/waybar-art.png"
CACHE_DIR = "/tmp/waybar_art_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

LAST_KEY = ""

def extract_youtube_id(text):
    if not text:
        return None
    match = re.search(r'(?:v=|\/|be\/)([a-zA-Z0-9_-]{11})', text)
    if match:
        return match.group(1)
    return None

def fetch_youtube_thumb_by_title(title):
    clean_title = re.sub(r'\s*-\s*YouTube\s*$', '', title, flags=re.IGNORECASE)
    clean_title = re.sub(r'^\(\d+\)\s*', '', clean_title) # strip (13)
    if not clean_title or len(clean_title) < 2:
        return None

    cache_key = re.sub(r'[^a-zA-Z0-9]', '_', clean_title)[:40]
    cached_path = os.path.join(CACHE_DIR, f"{cache_key}.jpg")
    if os.path.exists(cached_path):
        return cached_path

    try:
        search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(clean_title)
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=3).read().decode("utf-8")
        vids = re.findall(r'"videoId":"([a-zA-Z0-9_-]{11})"', html)
        if vids:
            thumb_url = f"https://img.youtube.com/vi/{vids[0]}/hqdefault.jpg"
            urllib.request.urlretrieve(thumb_url, cached_path)
            return cached_path
    except Exception:
        pass
    return None

def get_active_media_info():
    try:
        proc = subprocess.run(
            ["playerctl", "-a", "metadata", "--format", "{{status}}\t{{playerName}}\t{{mpris:artUrl}}\t{{xesam:url}}\t{{xesam:title}}"],
            capture_output=True, text=True, timeout=2
        )
        if proc.stdout.strip():
            lines = proc.stdout.strip().split("\n")

            # First try to find a Playing player, fallback to Paused
            selected_line = None
            for line in lines:
                if line.lower().startswith("playing"):
                    selected_line = line
                    break
            if not selected_line:
                for line in lines:
                    if line.lower().startswith("paused"):
                        selected_line = line
                        break

            if selected_line:
                parts = selected_line.split("\t")
                status = parts[0].strip().lower() if len(parts) > 0 else ""
                player = parts[1].strip() if len(parts) > 1 else ""
                art_url = parts[2].strip() if len(parts) > 2 else ""
                page_url = parts[3].strip() if len(parts) > 3 else ""
                title = parts[4].strip() if len(parts) > 4 else ""

                # 1. Direct artUrl (Spotify, local files, web thumbnails)
                if art_url:
                    if art_url.startswith("file://"):
                        local_path = art_url.replace("file://", "")
                        if os.path.exists(local_path):
                            return (f"{player}:{title}", "local", local_path)
                    elif art_url.startswith("http://") or art_url.startswith("https://"):
                        return (f"{player}:{art_url}", "remote", art_url)

                # 2. YouTube Video ID in page_url or art_url
                vid = extract_youtube_id(page_url) or extract_youtube_id(art_url)
                if vid:
                    yt_url = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
                    return (f"{player}:{vid}", "remote", yt_url)

                # 3. YouTube search fallback by title (for Brave / Chrome when url/artUrl is empty)
                if "youtube" in title.lower() or "remix" in title.lower() or "(" in title or title:
                    thumb_file = fetch_youtube_thumb_by_title(title)
                    if thumb_file:
                        return (f"{player}:{title}", "local", thumb_file)

    except Exception:
        pass

    # 4. Check if mpv (used by yt-x) is running
    try:
        ps_proc = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=2)
        for line in ps_proc.stdout.split("\n"):
            if "mpv " in line and "grep" not in line:
                vid = extract_youtube_id(line)
                if vid:
                    yt_url = f"https://img.youtube.com/vi/{vid}/hqdefault.jpg"
                    return (f"mpv:{vid}", "remote", yt_url)
    except Exception:
        pass

    return (None, None, None)

def update_art():
    global LAST_KEY
    key, kind, url_or_path = get_active_media_info()

    if key and url_or_path:
        if key != LAST_KEY or not os.path.exists(OUT_FILE):
            LAST_KEY = key
            try:
                if kind == "remote":
                    urllib.request.urlretrieve(url_or_path, OUT_FILE)
                elif kind == "local":
                    subprocess.run(["cp", url_or_path, OUT_FILE], stderr=subprocess.DEVNULL)
            except Exception:
                pass
    else:
        if os.path.exists(OUT_FILE):
            try:
                os.remove(OUT_FILE)
            except Exception:
                pass
        LAST_KEY = ""

if __name__ == "__main__":
    while True:
        update_art()
        time.sleep(1)
