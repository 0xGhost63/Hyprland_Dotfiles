#!/usr/bin/env python3
import os
import re
import sys
import subprocess

ICON_DIR = "/usr/share/icons/Papirus-Dark/24x24/panel"

def run_rofi(prompt, input_str):
    cmd = ["rofi", "-dmenu", "-i", "-show-icons", "-p", prompt]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=False)
    out, _ = p.communicate(input=input_str.encode("utf-8"))
    return out.decode("utf-8").strip()

def main():
    res_bt = subprocess.run(["bluetoothctl", "show"], capture_output=True, text=True)
    bt_on = any(k in res_bt.stdout for k in ["Powered: yes", "PowerState: on"])

    lines = []
    if bt_on:
        lines.append(f"Turn Bluetooth Off\x00icon\x1f{ICON_DIR}/bluetooth-disabled.svg")
    else:
        lines.append(f"Turn Bluetooth On\x00icon\x1f{ICON_DIR}/bluetooth-active.svg")

    lines.append(f"Scan Devices\x00icon\x1f{ICON_DIR}/network-wireless-0.svg")

    if bt_on:
        res_dev = subprocess.run(["bluetoothctl", "devices"], capture_output=True, text=True)
        for line in res_dev.stdout.strip().split("\n"):
            parts = line.split(" ", 2)
            if len(parts) >= 3:
                mac = parts[1]
                name = parts[2]
                info_res = subprocess.run(["bluetoothctl", "info", mac], capture_output=True, text=True)
                is_conn = "Connected: yes" in info_res.stdout
                icon_name = "bluetooth-connected.svg" if is_conn else "bluetooth-active.svg"
                prefix = "[Connected] " if is_conn else ""
                label = f"{prefix}{name} ({mac})"
                lines.append(f"{label}\x00icon\x1f{os.path.join(ICON_DIR, icon_name)}")

    input_str = "\n".join(lines) + "\n"
    chosen = run_rofi("Bluetooth", input_str)

    if not chosen:
        return

    if "Turn Bluetooth Off" in chosen:
        subprocess.run(["bluetoothctl", "power", "off"])
        subprocess.run(["rfkill", "block", "bluetooth"], stderr=subprocess.DEVNULL)
        subprocess.run(["notify-send", "-u", "low", "Bluetooth", "Bluetooth Powered Off"])
    elif "Turn Bluetooth On" in chosen:
        subprocess.run(["rfkill", "unblock", "bluetooth"], stderr=subprocess.DEVNULL)
        subprocess.run(["bluetoothctl", "power", "on"])
        subprocess.run(["notify-send", "-u", "low", "Bluetooth", "Bluetooth Powered On"])
        main()
    elif "Scan Devices" in chosen:
        subprocess.run(["notify-send", "-u", "low", "Bluetooth", "Scanning for devices..."])
        subprocess.run(["bluetoothctl", "--timeout", "5", "scan", "on"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        main()
    else:
        mac_match = re.search(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}", chosen)
        if mac_match:
            mac = mac_match.group(0)
            name = chosen
            if name.startswith("[Connected] "):
                name = name.replace("[Connected] ", "")
            name = re.sub(r"\s+\(([0-9A-Fa-f:]+)\)$", "", name)

            if "[Connected]" in chosen:
                action = run_rofi(name, "Disconnect\nUnpair / Remove\n")
                if action == "Disconnect":
                    subprocess.run(["bluetoothctl", "disconnect", mac])
                    subprocess.run(["notify-send", "-u", "low", "Bluetooth", f"Disconnected from {name}"])
                elif "Unpair" in action:
                    subprocess.run(["bluetoothctl", "remove", mac])
                    subprocess.run(["notify-send", "-u", "low", "Bluetooth", f"Removed {name}"])
            else:
                action = run_rofi(name, "Connect\nPair & Connect\nRemove\n")
                if action == "Connect":
                    subprocess.run(["notify-send", "-u", "low", "Bluetooth", f"Connecting to {name}..."])
                    subprocess.run(["bluetoothctl", "connect", mac])
                elif "Pair" in action:
                    subprocess.run(["notify-send", "-u", "low", "Bluetooth", f"Pairing with {name}..."])
                    subprocess.run(["bluetoothctl", "pair", mac])
                    subprocess.run(["bluetoothctl", "connect", mac])
                elif action == "Remove":
                    subprocess.run(["bluetoothctl", "remove", mac])
                    subprocess.run(["notify-send", "-u", "low", "Bluetooth", f"Removed {name}"])

if __name__ == "__main__":
    main()
