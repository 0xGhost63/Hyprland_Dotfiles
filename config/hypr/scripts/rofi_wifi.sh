#!/usr/bin/env python3
import os
import re
import sys
import subprocess

ICON_DIR = "/usr/share/icons/Papirus-Dark/24x24/panel"

def run_rofi(prompt, input_str, password=False):
    cmd = ["rofi", "-dmenu", "-i", "-p", prompt]
    if not password:
        cmd.append("-show-icons")
    else:
        cmd.append("-password")

    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=False)
    out, _ = p.communicate(input=input_str.encode("utf-8"))
    return out.decode("utf-8").strip()

def main():
    # Check Wi-Fi state
    res_state = subprocess.run(["nmcli", "-fields", "WIFI", "g"], capture_output=True, text=True)
    wifi_enabled = "enabled" in res_state.stdout.lower()

    lines = []
    if wifi_enabled:
        lines.append(f"Turn Wi-Fi Off\x00icon\x1f{ICON_DIR}/network-wireless-offline.svg")
    else:
        lines.append(f"Turn Wi-Fi On\x00icon\x1f{ICON_DIR}/network-wireless-signal-excellent.svg")

    lines.append(f"Rescan Networks\x00icon\x1f{ICON_DIR}/network-wireless-0.svg")

    if wifi_enabled:
        res_list = subprocess.run(["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list"], capture_output=True, text=True)
        seen = set()
        for line in res_list.stdout.strip().split("\n"):
            parts = line.split(":")
            if len(parts) >= 3 and parts[1].strip():
                in_use = parts[0].strip() == "*"
                ssid = parts[1].strip()
                try:
                    sig = int(parts[2].strip())
                except ValueError:
                    sig = 0
                is_sec = len(parts) > 3 and bool(parts[3].strip())

                if ssid in seen:
                    continue
                seen.add(ssid)

                prefix = "network-wireless-secure-signal-" if is_sec else "network-wireless-signal-"
                if sig >= 75:
                    icon_name = prefix + "excellent.svg"
                elif sig >= 50:
                    icon_name = prefix + "good.svg"
                elif sig >= 25:
                    icon_name = prefix + "low.svg"
                else:
                    icon_name = prefix + "none.svg"

                icon_path = os.path.join(ICON_DIR, icon_name)
                status_prefix = "[Connected] " if in_use else ""
                label = f"{status_prefix}{ssid} ({sig}%)"
                lines.append(f"{label}\x00icon\x1f{icon_path}")

    input_str = "\n".join(lines) + "\n"
    chosen = run_rofi("Wi-Fi", input_str)

    if not chosen:
        return

    if "Turn Wi-Fi Off" in chosen:
        subprocess.run(["nmcli", "radio", "wifi", "off"])
    elif "Turn Wi-Fi On" in chosen:
        subprocess.run(["nmcli", "radio", "wifi", "on"])
    elif "Rescan Networks" in chosen:
        subprocess.run(["nmcli", "dev", "wifi", "rescan"])
        main()
    else:
        # Extract SSID
        ssid = chosen
        if ssid.startswith("[Connected] "):
            ssid = ssid.replace("[Connected] ", "")
        ssid = re.sub(r'\s+\(\d+%\)$', '', ssid)

        if "[Connected]" in chosen:
            action = run_rofi(ssid, "Disconnect\nForget\n")
            if action == "Disconnect":
                dev_res = subprocess.run(["nmcli", "-t", "-f", "DEVICE,TYPE", "dev"], capture_output=True, text=True)
                for dev_line in dev_res.stdout.split("\n"):
                    if "wifi" in dev_line:
                        dev_name = dev_line.split(":")[0]
                        subprocess.run(["nmcli", "dev", "disconnect", dev_name])
                        break
            elif action == "Forget":
                subprocess.run(["nmcli", "connection", "delete", "id", ssid])
        else:
            sec_res = subprocess.run(["nmcli", "-t", "-f", "SSID,SECURITY", "dev", "wifi", "list"], capture_output=True, text=True)
            is_secured = False
            for sline in sec_res.stdout.split("\n"):
                sparts = sline.split(":")
                if len(sparts) >= 2 and sparts[0] == ssid and sparts[1].strip():
                    is_secured = True
                    break

            if is_secured:
                password = run_rofi(f"Password for {ssid}", "", password=True)
                if password:
                    subprocess.run(["nmcli", "dev", "wifi", "connect", ssid, "password", password])
            else:
                subprocess.run(["nmcli", "dev", "wifi", "connect", ssid])

if __name__ == "__main__":
    main()
