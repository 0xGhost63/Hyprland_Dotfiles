#!/usr/bin/env python3
# MPRIS Album Art Fetcher Daemon for Swaync / GTK
# Downloads HTTPS album covers to /tmp/mpris_art.png locally so GTK never fails to render art

import time
import urllib.request
import subprocess
import os

OUT_FILE = "/tmp/mpris_art.png"
LAST_URL = ""

def fetch_art():
    global LAST_URL
    try:
        r = subprocess.run(["playerctl", "-p", "spotify", "metadata", "--format", "{{mpris:artUrl}}"],
                           capture_output=True, text=True, timeout=3)
        art_url = r.stdout.strip()
        if art_url and art_url != LAST_URL:
            LAST_URL = art_url
            if art_url.startswith("http://") or art_url.startswith("https://"):
                urllib.request.urlretrieve(art_url, OUT_FILE)
            elif art_url.startswith("file://"):
                src = art_url.replace("file://", "")
                if os.path.exists(src):
                    os.system(f"cp '{src}' '{OUT_FILE}'")
    except Exception:
        pass

if __name__ == "__main__":
    while True:
        fetch_art()
        time.sleep(2)
