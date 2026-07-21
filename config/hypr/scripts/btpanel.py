#!/usr/bin/env python3
# Bluetooth Panel — Sleek GTK4 Control Dialog
# Triggered from Waybar right-click on Bluetooth module

import gi
import subprocess
import threading
import re

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

GLib.set_prgname("btpanel")
GLib.set_application_name("Bluetooth Panel")

CSS = b"""
* {
    font-family: "Inter", "JetBrains Mono Nerd Font", "JetBrains Mono", sans-serif;
}

window, decoration {
    background: transparent;
}

.panel-root {
    background-color: #1a1b26;
    border: 1px solid rgba(122, 162, 247, 0.25);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.panel-header {
    background-color: #16161e;
    border-radius: 16px 16px 0 0;
    padding: 14px 16px 12px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-title {
    color: #7aa2f7;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.close-btn {
    color: #565f89;
    font-size: 14px;
    background: transparent;
    border: none;
    border-radius: 6px;
    padding: 2px 8px;
    min-width: 0;
    min-height: 0;
}

.close-btn:hover {
    color: #f7768e;
    background-color: rgba(247, 118, 142, 0.12);
}

.conn-card {
    background-color: #24283b;
    border: 1px solid rgba(122, 162, 247, 0.2);
    border-radius: 12px;
    margin: 12px 14px 8px;
    padding: 12px 14px;
}

.conn-icon {
    font-size: 18px;
    color: #73daca;
}

.conn-name {
    color: #c0caf5;
    font-size: 13px;
    font-weight: 600;
}

.badge-connected {
    background-color: rgba(115, 218, 202, 0.15);
    color: #73daca;
    border: 1px solid rgba(115, 218, 202, 0.3);
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}

.badge-offline {
    background-color: rgba(86, 95, 137, 0.15);
    color: #565f89;
    border: 1px solid rgba(86, 95, 137, 0.3);
    border-radius: 4px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}

.divider {
    background-color: rgba(255, 255, 255, 0.06);
    min-height: 1px;
    margin: 4px 14px;
}

.section-label {
    color: #565f89;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 10px 16px 6px;
}

.dev-row {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 8px;
    padding: 8px 10px;
    margin: 2px 10px;
}

.dev-row:hover {
    background-color: #24283b;
    border-color: rgba(122, 162, 247, 0.15);
}

.dev-icon {
    font-size: 14px;
    color: #7aa2f7;
}

.row-name {
    color: #a9b1d6;
    font-size: 12px;
    font-weight: 500;
}

.action-btn {
    background-color: rgba(122, 162, 247, 0.1);
    color: #7aa2f7;
    border: 1px solid rgba(122, 162, 247, 0.3);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 3px 10px;
    min-height: 0;
}

.action-btn:hover {
    background-color: #7aa2f7;
    color: #1a1b26;
}

.disconnect-btn {
    background-color: rgba(247, 118, 142, 0.1);
    color: #f7768e;
    border: 1px solid rgba(247, 118, 142, 0.3);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 3px 10px;
    min-height: 0;
}

.disconnect-btn:hover {
    background-color: #f7768e;
    color: #1a1b26;
}

.panel-footer {
    background-color: #16161e;
    border-radius: 0 0 16px 16px;
    border-top: 1px solid rgba(255, 255, 255, 0.06);
    padding: 12px 14px;
}

.btn-footer {
    background-color: rgba(122, 162, 247, 0.12);
    color: #7aa2f7;
    border: 1px solid rgba(122, 162, 247, 0.25);
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    padding: 7px 0;
}

.btn-footer:hover {
    background-color: #7aa2f7;
    color: #1a1b26;
}

.btn-secondary {
    background-color: rgba(255, 255, 255, 0.04);
    color: #a9b1d6;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    padding: 7px 0;
}

.btn-secondary:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #c0caf5;
}

scrolledwindow { background: transparent; }
scrollbar { background: transparent; min-width: 4px; }
scrollbar slider { background-color: #3b4261; border-radius: 4px; min-width: 4px; }
"""

# Icon mapping for Bluetooth device types
DEVICE_ICON = {
    "audio-headphones": "󰋋",
    "audio-headset":    "󰋎",
    "audio-card":       "󰓃",
    "input-mouse":      "󰍽",
    "input-keyboard":   "󰌌",
    "input-gaming":     "󰄋",
    "phone":            "󰏲",
    "computer":         "󰌢",
    "default":          "󰂯",
}

def btctl_run(args):
    try:
        r = subprocess.run(
            ["bluetoothctl"] + args,
            capture_output=True, text=True, timeout=5, input=""
        )
        return r.stdout.strip()
    except Exception:
        return ""

def bt_service_active():
    try:
        r = subprocess.run(["systemctl", "is-active", "bluetooth"], capture_output=True, text=True, timeout=3)
        return r.stdout.strip() == "active"
    except Exception:
        return False

def bt_powered():
    out = btctl_run(["show"])
    return "Powered: yes" in out

def set_bt_power(state: bool):
    subprocess.run(["bluetoothctl", "power", "on" if state else "off"], capture_output=True)

def get_devices():
    devices_out = btctl_run(["devices"])

    devices = []
    for line in devices_out.splitlines():
        m = re.match(r"Device ([0-9A-F:]{17}) (.+)", line, re.I)
        if not m:
            continue
        mac = m.group(1).upper()
        name = m.group(2).strip()

        info = btctl_run(["info", mac])
        connected = "Connected: yes" in info

        dev_type = "default"
        for l in info.splitlines():
            if "Icon:" in l:
                raw = l.split("Icon:")[1].strip()
                if raw in DEVICE_ICON:
                    dev_type = raw
                break

        bat_match = re.search(r"Battery Percentage:.*\((\d+)\)", info)
        battery = f"{bat_match.group(1)}%" if bat_match else None

        devices.append({
            "mac": mac,
            "name": name,
            "connected": connected,
            "battery": battery,
            "icon": DEVICE_ICON.get(dev_type, "󰂯"),
        })

    devices.sort(key=lambda d: (not d["connected"], d["name"]))
    return devices


class BTPanel(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="hypr.btpanel")
        self._scanning = False

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("Bluetooth Control")
        self.win.set_default_size(340, 1)
        self.win.set_decorated(False)
        self.win.set_resizable(False)

        css = Gtk.CssProvider()
        css.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(), css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        root.add_css_class("panel-root")
        self.win.set_child(root)

        # ── Header ────────────────────────────────────────
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        header.add_css_class("panel-header")

        bt_icon = Gtk.Label(label="󰂯")
        bt_icon.add_css_class("panel-title")

        title = Gtk.Label(label="Bluetooth")
        title.add_css_class("panel-title")

        spacer = Gtk.Box()
        spacer.set_hexpand(True)

        self._switch = Gtk.Switch()
        self._switch.set_valign(Gtk.Align.CENTER)
        self._switch.set_active(bt_powered())
        self._switch.connect("state-set", self._on_switch_toggled)

        close_btn = Gtk.Button(label="✕")
        close_btn.add_css_class("close-btn")
        close_btn.connect("clicked", lambda _: self.win.close())

        for w in [bt_icon, title, spacer, self._switch, close_btn]:
            header.append(w)
        root.append(header)

        # Check Service Status
        if not bt_service_active():
            self._show_service_error(root)
            self.win.present()
            return

        # ── Active Connection Card ────────────────────────
        conn_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        conn_card.add_css_class("conn-card")

        self._conn_icon = Gtk.Label(label="󰂯")
        self._conn_icon.add_css_class("conn-icon")
        self._conn_icon.set_valign(Gtk.Align.CENTER)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        info_box.set_hexpand(True)

        self._conn_name = Gtk.Label(label="Scanning devices…")
        self._conn_name.add_css_class("conn-name")
        self._conn_name.set_halign(Gtk.Align.START)

        self._conn_badge = Gtk.Label(label="Checking…")
        self._conn_badge.add_css_class("badge-offline")
        self._conn_badge.set_halign(Gtk.Align.START)

        info_box.append(self._conn_name)
        info_box.append(self._conn_badge)

        conn_card.append(self._conn_icon)
        conn_card.append(info_box)
        root.append(conn_card)

        # ── Divider & Section Label ───────────────────────
        div = Gtk.Separator()
        div.add_css_class("divider")
        root.append(div)

        sec = Gtk.Label(label="PAIRED DEVICES")
        sec.add_css_class("section-label")
        sec.set_halign(Gtk.Align.START)
        root.append(sec)

        # ── Device List ───────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(180)
        scroll.set_max_content_height(260)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        scroll.set_child(self._list_box)
        root.append(scroll)

        # ── Footer ────────────────────────────────────────
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.add_css_class("panel-footer")

        self._btn_scan = Gtk.Button(label="Scan Devices")
        self._btn_scan.add_css_class("btn-footer")
        self._btn_scan.set_hexpand(True)
        self._btn_scan.connect("clicked", self._on_scan)

        btn_set = Gtk.Button(label="Manager")
        btn_set.add_css_class("btn-secondary")
        btn_set.set_hexpand(True)
        btn_set.connect("clicked", lambda _: (subprocess.Popen(["blueman-manager"]), self.win.close()))

        footer.append(self._btn_scan)
        footer.append(btn_set)
        root.append(footer)

        # Keyboard shortcut ESC to close
        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", lambda c, k, *a: self.win.close() if k == Gdk.KEY_Escape else False)
        self.win.add_controller(kc)

        self.win.present()
        threading.Thread(target=self._load_data, daemon=True).start()

    def _show_service_error(self, root):
        card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        card.add_css_class("conn-card")

        lbl = Gtk.Label(label="Bluetooth Service Inactive")
        lbl.add_css_class("conn-name")
        lbl.set_halign(Gtk.Align.START)

        desc = Gtk.Label(label="Systemd bluetooth.service is stopped. Enable it to connect devices.")
        desc.add_css_class("row-name")
        desc.set_wrap(True)
        desc.set_halign(Gtk.Align.START)

        btn = Gtk.Button(label="Start Service")
        btn.add_css_class("action-btn")
        btn.set_halign(Gtk.Align.START)
        btn.connect("clicked", self._on_start_service)

        card.append(lbl)
        card.append(desc)
        card.append(btn)
        root.append(card)

    def _on_start_service(self, _):
        subprocess.Popen(["pkexec", "systemctl", "enable", "--now", "bluetooth"])
        self.win.close()

    def _load_data(self):
        devices = get_devices()
        GLib.idle_add(self._update_ui, devices)

    def _update_ui(self, devices):
        connected = next((d for d in devices if d["connected"]), None)

        if connected:
            self._conn_name.set_text(connected["name"])
            self._conn_icon.set_text(connected["icon"])
            bat_str = f"Connected ({connected['battery']})" if connected.get("battery") else "Connected"
            self._conn_badge.set_text(bat_str)
            self._conn_badge.remove_css_class("badge-offline")
            self._conn_badge.add_css_class("badge-connected")
        else:
            self._conn_name.set_text("No Device Connected")
            self._conn_icon.set_text("󰂯")
            self._conn_badge.set_text("Disconnected")
            self._conn_badge.remove_css_class("badge-connected")
            self._conn_badge.add_css_class("badge-offline")

        while self._list_box.get_first_child():
            self._list_box.remove(self._list_box.get_first_child())

        if not devices:
            lbl = Gtk.Label(label="No paired devices found")
            lbl.add_css_class("row-name")
            lbl.set_margin_start(16)
            lbl.set_margin_top(16)
            lbl.set_halign(Gtk.Align.START)
            self._list_box.append(lbl)
        else:
            for dev in devices:
                self._add_device_row(dev)
        return False

    def _add_device_row(self, dev):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        row_box.add_css_class("dev-row")

        icon_lbl = Gtk.Label(label=dev["icon"])
        icon_lbl.add_css_class("dev-icon")

        name_str = f"{dev['name']} ({dev['battery']})" if dev.get("battery") else dev["name"]
        name_lbl = Gtk.Label(label=name_str)
        name_lbl.add_css_class("row-name")
        name_lbl.set_hexpand(True)
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)

        if dev["connected"]:
            action_btn = Gtk.Button(label="Disconnect")
            action_btn.add_css_class("disconnect-btn")
            action_btn.connect("clicked", lambda b, m=dev["mac"]: self._on_disconnect_dev(m))
        else:
            action_btn = Gtk.Button(label="Connect")
            action_btn.add_css_class("action-btn")
            action_btn.connect("clicked", lambda b, m=dev["mac"]: self._on_connect_dev(m))

        row_box.append(icon_lbl)
        row_box.append(name_lbl)
        row_box.append(action_btn)
        self._list_box.append(row_box)

    def _on_connect_dev(self, mac):
        subprocess.Popen(["bluetoothctl", "connect", mac])
        GLib.timeout_add(1500, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)

    def _on_disconnect_dev(self, mac):
        subprocess.Popen(["bluetoothctl", "disconnect", mac])
        GLib.timeout_add(1500, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)

    def _on_scan(self, _):
        if self._scanning:
            return
        self._scanning = True
        self._btn_scan.set_label("Scanning…")
        self._btn_scan.set_sensitive(False)

        def scan():
            subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, timeout=8)

        def after():
            self._scanning = False
            self._btn_scan.set_label("Scan Devices")
            self._btn_scan.set_sensitive(True)
            threading.Thread(target=self._load_data, daemon=True).start()
            return False

        threading.Thread(target=lambda: (scan(), GLib.idle_add(after)), daemon=True).start()

    def _on_switch_toggled(self, switch, state):
        set_bt_power(state)
        GLib.timeout_add(800, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)
        return False


if __name__ == "__main__":
    app = BTPanel()
    app.run(None)
