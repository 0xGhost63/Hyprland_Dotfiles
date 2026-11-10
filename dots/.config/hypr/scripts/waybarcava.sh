#!/usr/bin/env python3
import os
import sys
import subprocess
import signal

config_file = "/tmp/bar_cava_config"
with open(config_file, "w") as f:
    f.write("""[general]
framerate = 60
bars = 14
autosens = 1
sensitivity = 100

[smoothing]
integral = 70
monstercat = 1
waves = 0
gravity = 100

[input]
method = pulse
source = auto

[output]
method = raw
raw_target = /dev/stdout
data_format = ascii
ascii_max_range = 8
""")

subprocess.run(["pkill", "-f", f"cava -p {config_file}"], stderr=subprocess.DEVNULL)

proc = subprocess.Popen(
    ["cava", "-p", config_file],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL,
    text=True,
    bufsize=1
)

bars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]

try:
    for line in proc.stdout:
        line = line.strip().rstrip(";")
        if not line:
            continue
        parts = line.split(";")
        out = ""
        is_silent = True
        for p in parts:
            try:
                v = int(p)
                if v > 0:
                    is_silent = False
                if v < 0: v = 0
                if v >= len(bars): v = len(bars) - 1
                out += bars[v]
            except ValueError:
                pass
        if is_silent:
            sys.stdout.write("\n")
        else:
            sys.stdout.write(out + "\n")
        sys.stdout.flush()
except KeyboardInterrupt:
    proc.terminate()
