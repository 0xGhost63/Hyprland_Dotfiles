#!/usr/bin/env python3
# Bluetooth Panel — Ghost's ricing
# Floating GTK4 panel triggered from Waybar

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
    font-family: "JetBrains Mono", "Iosevka", monospace;
}
window, decoration {
    background: transparent;
}
.panel-root {
    background-color: #15161E;
    border: 1px solid #f8a0b0;
    border-radius: 12px;
}
.panel-header {
    background-color: #0d0e17;
    border-radius: 12px 12px 0 0;
    padding: 12px 14px 10px;
    border-bottom: 1px solid rgba(248,160,176,0.15);
}
.panel-title {
    color: #bb9af7;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
}
.toggle-on {
    color: #bb9af7;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}
.toggle-off {
    color: #565f89;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
}
.close-btn {
    color: #565f89;
    font-size: 12px;
    background: transparent;
    border: none;
    border-radius: 4px;
    padding: 2px 6px;
    min-width: 0;
    min-height: 0;
}
.close-btn:hover {
    color: #f7768e;
    background-color: rgba(247,118,142,0.1);
}
.conn-card {
    background-color: #1a1b26;
    border: 1px solid rgba(248,160,176,0.15);
    border-radius: 8px;
    margin: 10px 10px 8px;
    padding: 10px 12px;
}
.conn-type-badge {
    background-color: rgba(187,154,247,0.12);
    color: #bb9af7;
    border: 1px solid rgba(187,154,247,0.25);
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    padding: 1px 6px;
    letter-spacing: 1px;
}
.conn-name {
    color: #c0caf5;
    font-size: 13px;
    font-weight: 600;
}
.badge-audio {
    background-color: rgba(187,154,247,0.12);
    color: #bb9af7;
    border: 1px solid rgba(187,154,247,0.3);
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    padding: 1px 6px;
    letter-spacing: 0.8px;
}
.badge-none {
    background-color: rgba(247,118,142,0.1);
    color: #f7768e;
    border: 1px solid rgba(247,118,142,0.25);
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    padding: 1px 6px;
    letter-spacing: 0.8px;
}
.divider {
    background-color: rgba(248,160,176,0.1);
    min-height: 1px;
    margin: 0 10px;
}
.section-label {
    color: #565f89;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 2px;
    margin: 8px 14px 4px;
}
.net-row {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 7px;
    padding: 6px 8px;
    margin: 1px 8px;
    min-height: 0;
}
.net-row:hover {
    background-color: #1a1b26;
    border-color: rgba(248,160,176,0.1);
}
.net-row-active {
    background-color: #1a1b26;
    border: 1px solid rgba(187,154,247,0.2);
    border-radius: 7px;
    padding: 6px 8px;
    margin: 1px 8px;
    min-height: 0;
}
.dev-type-badge {
    background-color: rgba(100,100,140,0.15);
    color: #565f89;
    border: 1px solid rgba(100,100,140,0.2);
    border-radius: 3px;
    font-size: 8px;
    font-weight: 700;
    padding: 0 5px;
    letter-spacing: 0.5px;
    min-width: 0;
}
.row-name {
    color: #a9b1d6;
    font-size: 12px;
}
.row-name-active {
    color: #c0caf5;
    font-size: 12px;
    font-weight: 600;
}
.badge-paired {
    background-color: rgba(187,154,247,0.1);
    color: #bb9af7;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    padding: 1px 5px;
    letter-spacing: 0.6px;
}
.connect-btn {
    background: transparent;
    color: #a9b1d6;
    border: 1px solid #414868;
    border-radius: 4px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.5px;
    padding: 1px 7px;
    min-height: 0;
    min-width: 0;
}
.connect-btn:hover {
    border-color: #bb9af7;
    color: #bb9af7;
    background-color: rgba(187,154,247,0.08);
}
.panel-footer {
    background-color: #0d0e17;
    border-radius: 0 0 12px 12px;
    border-top: 1px solid rgba(248,160,176,0.12);
    padding: 9px 10px 11px;
}
.btn-scan {
    background: transparent;
    color: #bb9af7;
    border: 1px solid rgba(187,154,247,0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 6px 0;
    min-height: 0;
}
.btn-scan:hover {
    background-color: rgba(187,154,247,0.08);
    border-color: #bb9af7;
}
.btn-settings {
    background: transparent;
    color: #565f89;
    border: 1px solid #414868;
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 6px 0;
    min-height: 0;
}
.btn-settings:hover {
    background-color: #1a1b26;
    border-color: rgba(248,160,176,0.3);
    color: #a9b1d6;
}
scrolledwindow { background: transparent; }
scrolledwindow undershoot, overshoot { background: none; }
scrollbar { background: transparent; min-width: 3px; }
scrollbar slider { background-color: #414868; border-radius: 2px; min-width: 3px; }
"""

# Device type → short label (no Nerd Font)
DEVICE_TYPE_LABEL = {
    "audio-headphones": "AUDIO",
    "audio-headset":    "AUDIO",
    "audio-card":       "AUDIO",
    "input-mouse":      "MOUSE",
    "input-keyboard":   "KBD",
    "input-gaming":     "CTRL",
    "phone":            "PHONE",
    "computer":         "PC",
    "default":          "BT",
}

def btctl_run(args):
    try:
        r = subprocess.run(
            ["bluetoothctl"] + args,
            capture_output=True, text=True, timeout=6, input=""
        )
        return r.stdout.strip()
    except Exception:
        return ""

def bt_powered():
    out = btctl_run(["show"])
    return "Powered: yes" in out

def set_bt(state: bool):
    subprocess.run(["bluetoothctl", "power", "on" if state else "off"],
                   capture_output=True)

def get_devices():
    paired_out   = btctl_run(["paired-devices"])
    conn_out     = btctl_run(["info"])

    connected_mac = None
    for line in conn_out.splitlines():
        m = re.match(r"Device ([0-9A-F:]{17})", line, re.I)
        if m:
            connected_mac = m.group(1).upper()
            break

    devices = []
    for line in paired_out.splitlines():
        m = re.match(r"Device ([0-9A-F:]{17}) (.+)", line, re.I)
        if not m:
            continue
        mac  = m.group(1).upper()
        name = m.group(2).strip()

        info = btctl_run(["info", mac])
        dev_type = "default"
        for l in info.splitlines():
            if "Icon:" in l:
                raw = l.split("Icon:")[1].strip()
                if raw in DEVICE_TYPE_LABEL:
                    dev_type = raw
                break

        devices.append({
            "mac":       mac,
            "name":      name,
            "connected": mac == connected_mac,
            "type_lbl":  DEVICE_TYPE_LABEL.get(dev_type, "BT"),
        })

    devices.sort(key=lambda d: (not d["connected"], d["name"]))
    return devices


class BTPanel(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="hypr.btpanel")
        self._scanning = False

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("Bluetooth Panel")
        self.win.set_default_size(320, 1)
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
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        header.add_css_class("panel-header")

        title = Gtk.Label(label="BLUETOOTH")
        title.add_css_class("panel-title")

        spacer = Gtk.Box()
        spacer.set_hexpand(True)

        self._enabled = bt_powered()
        self._toggle_lbl = Gtk.Label(label="ON" if self._enabled else "OFF")
        self._toggle_lbl.add_css_class("toggle-on" if self._enabled else "toggle-off")

        toggle_btn = Gtk.Button(label="PWR")
        toggle_btn.add_css_class("close-btn")
        toggle_btn.connect("clicked", self._on_toggle)

        close = Gtk.Button(label="X")
        close.add_css_class("close-btn")
        close.connect("clicked", lambda _: self.win.close())

        for w in [title, spacer, self._toggle_lbl, toggle_btn, close]:
            header.append(w)
        root.append(header)

        # ── Connected card ────────────────────────────────
        conn_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        conn_card.add_css_class("conn-card")

        left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        left.set_valign(Gtk.Align.CENTER)
        self._conn_type = Gtk.Label(label="BT")
        self._conn_type.add_css_class("conn-type-badge")
        left.append(self._conn_type)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        info_box.set_hexpand(True)

        self._conn_name = Gtk.Label(label="Scanning…")
        self._conn_name.add_css_class("conn-name")
        self._conn_name.set_halign(Gtk.Align.START)

        sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._conn_badge = Gtk.Label(label="CONNECTED")
        self._conn_badge.add_css_class("badge-audio")
        sub.append(self._conn_badge)

        info_box.append(self._conn_name)
        info_box.append(sub)

        conn_card.append(left)
        conn_card.append(info_box)
        root.append(conn_card)

        # ── Divider ───────────────────────────────────────
        div = Gtk.Separator()
        div.add_css_class("divider")
        root.append(div)

        sec = Gtk.Label(label="PAIRED DEVICES")
        sec.add_css_class("section-label")
        sec.set_halign(Gtk.Align.START)
        root.append(sec)

        # ── Device list ───────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(180)
        scroll.set_max_content_height(260)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._list_box)
        root.append(scroll)

        # ── Footer ────────────────────────────────────────
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.add_css_class("panel-footer")

        self._btn_scan = Gtk.Button(label="SCAN")
        self._btn_scan.add_css_class("btn-scan")
        self._btn_scan.set_hexpand(True)
        self._btn_scan.connect("clicked", self._on_scan)

        btn_set = Gtk.Button(label="SETTINGS")
        btn_set.add_css_class("btn-settings")
        btn_set.set_hexpand(True)
        btn_set.connect("clicked", lambda _: (subprocess.Popen(["blueman-manager"]), self.win.close()))

        footer.append(self._btn_scan)
        footer.append(btn_set)
        root.append(footer)

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", lambda c, k, *a: self.win.close() if k == Gdk.KEY_Escape else False)
        self.win.add_controller(kc)

        self.win.present()
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        devices = get_devices()
        GLib.idle_add(self._update_ui, devices)

    def _update_ui(self, devices):
        connected = next((d for d in devices if d["connected"]), None)

        if connected:
            self._conn_name.set_text(connected["name"])
            self._conn_type.set_text(connected["type_lbl"])
            self._conn_badge.set_text("CONNECTED")
            self._conn_badge.remove_css_class("badge-none")
            self._conn_badge.add_css_class("badge-audio")
        else:
            self._conn_name.set_text("No device connected")
            self._conn_type.set_text("BT")
            self._conn_badge.set_text("OFFLINE")
            self._conn_badge.remove_css_class("badge-audio")
            self._conn_badge.add_css_class("badge-none")

        while self._list_box.get_first_child():
            self._list_box.remove(self._list_box.get_first_child())

        unpaired = [d for d in devices if not d["connected"]]
        if not unpaired:
            lbl = Gtk.Label(label="No other paired devices")
            lbl.add_css_class("badge-none")
            lbl.set_margin_start(14)
            lbl.set_margin_top(12)
            lbl.set_halign(Gtk.Align.START)
            self._list_box.append(lbl)
        else:
            for dev in unpaired:
                self._add_device_row(dev)
        return False

    def _add_device_row(self, dev):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        row_box.add_css_class("net-row")

        type_lbl = Gtk.Label(label=dev["type_lbl"])
        type_lbl.add_css_class("dev-type-badge")

        name_lbl = Gtk.Label(label=dev["name"])
        name_lbl.add_css_class("row-name")
        name_lbl.set_hexpand(True)
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)

        right = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        status = Gtk.Label(label="PAIRED")
        status.add_css_class("badge-paired")

        conn_btn = Gtk.Button(label="CONNECT")
        conn_btn.add_css_class("connect-btn")
        conn_btn.connect("clicked", lambda b, m=dev["mac"]: self._on_connect_dev(m))

        right.append(status)
        right.append(conn_btn)

        row_box.append(type_lbl)
        row_box.append(name_lbl)
        row_box.append(right)
        self._list_box.append(row_box)

    def _on_connect_dev(self, mac):
        subprocess.Popen(["bluetoothctl", "connect", mac])
        GLib.timeout_add(2000, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)

    def _on_scan(self, _):
        if self._scanning:
            return
        self._scanning = True
        self._btn_scan.set_label("SCANNING...")
        self._btn_scan.set_sensitive(False)

        def scan():
            subprocess.run(["bluetoothctl", "scan", "on"],
                           capture_output=True, timeout=10)

        def after():
            self._scanning = False
            self._btn_scan.set_label("SCAN")
            self._btn_scan.set_sensitive(True)
            threading.Thread(target=self._load_data, daemon=True).start()
            return False

        threading.Thread(
            target=lambda: (scan(), GLib.idle_add(after)),
            daemon=True
        ).start()

    def _on_toggle(self, _):
        self._enabled = not self._enabled
        set_bt(self._enabled)
        self._toggle_lbl.set_text("ON" if self._enabled else "OFF")
        self._toggle_lbl.remove_css_class("toggle-on" if not self._enabled else "toggle-off")
        self._toggle_lbl.add_css_class("toggle-on" if self._enabled else "toggle-off")
        GLib.timeout_add(800, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)


app = BTPanel()
app.run(None)
