#!/usr/bin/env python3

import glob
import os
import select
import struct
import subprocess
import sys
import time
from pathlib import Path

EV_KEY = 1
KEY_POWER = 116
EVENT = struct.Struct("llHHi")

HOLD_SECONDS = float(os.environ.get("HOLD_SECONDS", "4"))
LOCK_CMD = os.environ.get(
    "LOCK_CMD",
    "qs -c ii ipc call lock activate || pidof hyprlock || hyprlock",
)
POWEROFF_CMD = os.environ.get(
    "POWEROFF_CMD",
    "systemctl poweroff || loginctl poweroff",
)


def run_detached(command):
    subprocess.Popen(
        ["bash", "-c", command],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )


def power_device_paths():
    override = os.environ.get("POWER_KEY_DEVICE", "")
    if override:
        return [path for path in override.split(":") if path]

    paths = []
    for path in sorted(glob.glob("/dev/input/event*")):
        name_path = Path("/sys/class/input") / Path(path).name / "device/name"
        try:
            name = name_path.read_text().strip().lower()
        except OSError:
            continue
        if "power" in name or "pwr" in name:
            paths.append(path)
    return paths


def open_devices(paths):
    devices = []
    for path in paths:
        try:
            fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
        except OSError as exc:
            print(f"power_key_monitor: cannot open {path}: {exc}", file=sys.stderr)
            continue
        devices.append((path, fd))
    return devices


def main():
    paths = power_device_paths()
    devices = open_devices(paths)
    if not devices:
        print("power_key_monitor: no power button input device found", file=sys.stderr)
        return 1

    fd_to_path = {fd: path for path, fd in devices}
    pressed_at = None
    powered_off = False

    try:
        while True:
            timeout = None
            if pressed_at is not None and not powered_off:
                timeout = max(0.0, HOLD_SECONDS - (time.monotonic() - pressed_at))

            readable, _, _ = select.select(list(fd_to_path), [], [], timeout)

            if not readable and pressed_at is not None and not powered_off:
                if time.monotonic() - pressed_at >= HOLD_SECONDS:
                    powered_off = True
                    run_detached(POWEROFF_CMD)
                continue

            for fd in readable:
                try:
                    data = os.read(fd, EVENT.size * 64)
                except BlockingIOError:
                    continue
                except OSError as exc:
                    print(
                        f"power_key_monitor: read error on {fd_to_path[fd]}: {exc}",
                        file=sys.stderr,
                    )
                    fd_to_path.pop(fd, None)
                    os.close(fd)
                    continue

                offset = 0
                while offset + EVENT.size <= len(data):
                    _, _, event_type, code, value = EVENT.unpack_from(data, offset)
                    offset += EVENT.size

                    if event_type != EV_KEY or code != KEY_POWER:
                        continue

                    if value == 1:
                        pressed_at = time.monotonic()
                        powered_off = False
                    elif value == 0 and pressed_at is not None:
                        duration = time.monotonic() - pressed_at
                        pressed_at = None
                        if not powered_off and duration < HOLD_SECONDS:
                            run_detached(LOCK_CMD)
                        powered_off = False
    except KeyboardInterrupt:
        return 0
    finally:
        for _, fd in devices:
            try:
                os.close(fd)
            except OSError:
                pass


if __name__ == "__main__":
    sys.exit(main())
