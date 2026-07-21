#!/usr/bin/env python3
# Bluetooth Panel — Native DBus Control Dialog
# Triggered from Waybar right-click on Bluetooth module

import gi
import subprocess
import threading
import re

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

try:
    import dbus
    HAS_DBUS = True
except ImportError:
    HAS_DBUS = False

GLib.set_prgname("btpanel")
GLib.set_application_name("Bluetooth Control")

CSS = b"""
* {
    font-family: "Inter", "JetBrains Mono Nerd Font", "JetBrains Mono", sans-serif;
}

window, decoration {
    background-color: #1a1b26;
    border: 1px solid rgba(122, 162, 247, 0.35);
    border-radius: 16px;
}

.panel-root {
    background-color: transparent;
    border: none;
    padding: 16px;
}

.panel-header {
    background-color: #16161e;
    border-radius: 12px;
    padding: 10px 14px;
    margin-bottom: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
}

.panel-title {
    color: #7aa2f7;
    font-size: 14px;
    font-weight: 700;
    letter-spacing: 0.5px;
}

.conn-card {
    background-color: #24283b;
    border: 1px solid rgba(122, 162, 247, 0.25);
    border-radius: 12px;
    margin-bottom: 12px;
    padding: 12px 14px;
}

.conn-icon {
    font-size: 20px;
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
    border: 1px solid rgba(115, 218, 202, 0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}

.badge-offline {
    background-color: rgba(86, 95, 137, 0.15);
    color: #565f89;
    border: 1px solid rgba(86, 95, 137, 0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 2px 8px;
}

.divider {
    background-color: rgba(255, 255, 255, 0.08);
    min-height: 1px;
    margin: 6px 0;
}

.section-label {
    color: #565f89;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    margin: 8px 4px 6px;
}

.dev-row {
    background-color: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 4px;
}

.dev-row:hover {
    background-color: #24283b;
    border-color: rgba(122, 162, 247, 0.25);
}

.dev-icon {
    font-size: 16px;
    color: #7aa2f7;
}

.row-name {
    color: #a9b1d6;
    font-size: 12px;
    font-weight: 500;
}

.action-btn {
    background-color: rgba(122, 162, 247, 0.14);
    color: #7aa2f7;
    border: 1px solid rgba(122, 162, 247, 0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 4px 12px;
    min-height: 0;
}

.action-btn:hover {
    background-color: #7aa2f7;
    color: #1a1b26;
}

.disconnect-btn {
    background-color: rgba(247, 118, 142, 0.14);
    color: #f7768e;
    border: 1px solid rgba(247, 118, 142, 0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 600;
    padding: 4px 12px;
    min-height: 0;
}

.disconnect-btn:hover {
    background-color: #f7768e;
    color: #1a1b26;
}

.panel-footer {
    background-color: #16161e;
    border-radius: 12px;
    border: 1px solid rgba(255, 255, 255, 0.06);
    padding: 10px;
    margin-top: 12px;
}

.btn-footer {
    background-color: rgba(122, 162, 247, 0.14);
    color: #7aa2f7;
    border: 1px solid rgba(122, 162, 247, 0.3);
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
    background-color: rgba(255, 255, 255, 0.05);
    color: #a9b1d6;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    font-size: 11px;
    font-weight: 600;
    padding: 7px 0;
}

.btn-secondary:hover {
    background-color: rgba(255, 255, 255, 0.12);
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

def get_dbus_devices():
    if not HAS_DBUS:
        return [], False
    try:
        bus = dbus.SystemBus()
        manager = dbus.Interface(bus.get_object("org.bluez", "/"), "org.freedesktop.DBus.ObjectManager")
        objects = manager.GetManagedObjects()

        powered = False
        devices = []

        for path, interfaces in objects.items():
            if "org.bluez.Adapter1" in interfaces:
                if bool(interfaces["org.bluez.Adapter1"].get("Powered", False)):
                    powered = True

            if "org.bluez.Device1" in interfaces:
                dev = interfaces["org.bluez.Device1"]
                name = str(dev.get("Name", dev.get("Alias", "Unknown")))
                mac = str(dev.get("Address", ""))
                connected = bool(dev.get("Connected", False))
                paired = bool(dev.get("Paired", False))
                raw_icon = str(dev.get("Icon", "default"))

                battery = None
                if "org.bluez.Battery1" in interfaces:
                    battery = f"{int(interfaces['org.bluez.Battery1'].get('Percentage', 0))}%"

                if paired or connected:
                    devices.append({
                        "mac": mac,
                        "name": name,
                        "connected": connected,
                        "battery": battery,
                        "icon": DEVICE_ICON.get(raw_icon, "󰂯"),
                    })

        devices.sort(key=lambda d: (not d["connected"], d["name"]))
        return devices, powered
    except Exception as e:
        return [], False

def set_bt_power(state: bool):
    subprocess.run(["bluetoothctl", "power", "on" if state else "off"], capture_output=True)


class BTPanel(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="hypr.btpanel")
        self._scanning = False

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("Bluetooth Control")
        self.win.set_default_size(380, 440)
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

        devices, powered = get_dbus_devices()

        self._switch = Gtk.Switch()
        self._switch.set_valign(Gtk.Align.CENTER)
        self._switch.set_active(powered)
        self._switch.connect("state-set", self._on_switch_toggled)

        header.append(bt_icon)
        header.append(title)
        header.append(spacer)
        header.append(self._switch)
        root.append(header)

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

        # ESC key controller to close window cleanly
        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", lambda c, k, *a: self.win.close() if k == Gdk.KEY_Escape else False)
        self.win.add_controller(kc)

        self.win.present()
        self._update_ui(devices)

    def _load_data(self):
        devices, _ = get_dbus_devices()
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
            lbl.set_margin_start(8)
            lbl.set_margin_top(12)
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
