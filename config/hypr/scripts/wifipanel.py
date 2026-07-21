#!/usr/bin/env python3
# WiFi Panel — Ghost's ricing
# Floating GTK4 panel triggered from Waybar

import gi
import subprocess
import threading

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

GLib.set_prgname("wifipanel")
GLib.set_application_name("WiFi Panel")

# ─── Tokyo Night palette ─────────────────────────────
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
    color: #7dcfff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2.5px;
}
.toggle-on {
    color: #7dcfff;
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
    background-color: rgba(125,207,255,0.12);
    color: #7dcfff;
    border: 1px solid rgba(125,207,255,0.25);
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
.badge-connected {
    background-color: rgba(158,206,106,0.12);
    color: #9ece6a;
    border: 1px solid rgba(158,206,106,0.3);
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
.signal-text {
    color: #7dcfff;
    font-size: 11px;
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
    border: 1px solid rgba(125,207,255,0.2);
    border-radius: 7px;
    padding: 6px 8px;
    margin: 1px 8px;
    min-height: 0;
}
.row-ssid-badge {
    background-color: rgba(125,207,255,0.08);
    color: #565f89;
    border: 1px solid rgba(125,207,255,0.12);
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
.lock-label {
    color: #565f89;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.5px;
}
.sig-label {
    color: #414868;
    font-size: 11px;
    letter-spacing: -1px;
}
.sig-label-good {
    color: #7dcfff;
    font-size: 11px;
    letter-spacing: -1px;
}
.panel-footer {
    background-color: #0d0e17;
    border-radius: 0 0 12px 12px;
    border-top: 1px solid rgba(248,160,176,0.12);
    padding: 9px 10px 11px;
}
.btn-disconnect {
    background: transparent;
    color: #f7768e;
    border: 1px solid rgba(247,118,142,0.35);
    border-radius: 6px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    padding: 6px 0;
    min-height: 0;
}
.btn-disconnect:hover {
    background-color: rgba(247,118,142,0.1);
    border-color: #f7768e;
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

def nmcli(*args):
    try:
        r = subprocess.run(
            ["nmcli", "--terse", "--fields", args[0], *args[1:]],
            capture_output=True, text=True, timeout=8
        )
        return r.stdout.strip()
    except Exception:
        return ""

def get_current_ssid():
    out = nmcli("active-connection,device,type,name", "connection", "show", "--active")
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) >= 3 and parts[2] == "802-11-wireless":
            return parts[3] if len(parts) > 3 else parts[0]
    return None

def get_signal_pct(ssid):
    out = nmcli("ssid,signal", "device", "wifi", "list")
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) >= 2 and parts[0] == ssid:
            try:
                return int(parts[1])
            except ValueError:
                return 0
    return 0

def get_networks():
    out = nmcli("ssid,signal,security", "device", "wifi", "list")
    seen = set()
    nets = []
    for line in out.splitlines():
        parts = line.split(":")
        if len(parts) < 2 or not parts[0].strip():
            continue
        ssid = parts[0].strip()
        if ssid in seen:
            continue
        seen.add(ssid)
        try:
            sig = int(parts[1])
        except (ValueError, IndexError):
            sig = 0
        secured = len(parts) > 2 and parts[2].strip() not in ("", "--")
        nets.append({"ssid": ssid, "signal": sig, "secured": secured})
    nets.sort(key=lambda x: x["signal"], reverse=True)
    return nets[:8]

def signal_bars(pct):
    """Unicode block bar — works without Nerd Font"""
    if pct >= 75: return "▂▄▆█"
    elif pct >= 50: return "▂▄▆░"
    elif pct >= 25: return "▂▄░░"
    else:           return "▂░░░"

def wifi_enabled():
    out = subprocess.run(["nmcli", "radio", "wifi"], capture_output=True, text=True).stdout.strip()
    return out == "enabled"

def set_wifi(state: bool):
    subprocess.run(["nmcli", "radio", "wifi", "on" if state else "off"])


class WiFiPanel(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="hypr.wifipanel")

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("WiFi Panel")
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

        title = Gtk.Label(label="NETWORK")
        title.add_css_class("panel-title")

        spacer = Gtk.Box()
        spacer.set_hexpand(True)

        self._enabled = wifi_enabled()
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
        type_badge = Gtk.Label(label="Wi-Fi")
        type_badge.add_css_class("conn-type-badge")
        left.append(type_badge)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        info_box.set_hexpand(True)

        self._conn_name = Gtk.Label(label="Scanning…")
        self._conn_name.add_css_class("conn-name")
        self._conn_name.set_halign(Gtk.Align.START)

        sub = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self._conn_badge = Gtk.Label(label="CONNECTED")
        self._conn_badge.add_css_class("badge-connected")
        self._signal_lbl = Gtk.Label(label="")
        self._signal_lbl.add_css_class("signal-text")
        sub.append(self._conn_badge)
        sub.append(self._signal_lbl)

        info_box.append(self._conn_name)
        info_box.append(sub)

        conn_card.append(left)
        conn_card.append(info_box)
        root.append(conn_card)

        # ── Divider ───────────────────────────────────────
        div = Gtk.Separator()
        div.add_css_class("divider")
        root.append(div)

        sec = Gtk.Label(label="AVAILABLE")
        sec.add_css_class("section-label")
        sec.set_halign(Gtk.Align.START)
        root.append(sec)

        # ── Network list ──────────────────────────────────
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_min_content_height(200)
        scroll.set_max_content_height(270)
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self._list_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        scroll.set_child(self._list_box)
        root.append(scroll)

        # ── Footer ────────────────────────────────────────
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.add_css_class("panel-footer")

        self._btn_disc = Gtk.Button(label="DISCONNECT")
        self._btn_disc.add_css_class("btn-disconnect")
        self._btn_disc.set_hexpand(True)
        self._btn_disc.connect("clicked", self._on_disconnect)

        btn_set = Gtk.Button(label="SETTINGS")
        btn_set.add_css_class("btn-settings")
        btn_set.set_hexpand(True)
        btn_set.connect("clicked", lambda _: (subprocess.Popen(["nm-connection-editor"]), self.win.close()))

        footer.append(self._btn_disc)
        footer.append(btn_set)
        root.append(footer)

        kc = Gtk.EventControllerKey()
        kc.connect("key-pressed", lambda c, k, *a: self.win.close() if k == Gdk.KEY_Escape else False)
        self.win.add_controller(kc)

        self.win.present()
        threading.Thread(target=self._load_data, daemon=True).start()

    def _load_data(self):
        current = get_current_ssid()
        signal  = get_signal_pct(current) if current else 0
        nets    = get_networks()
        GLib.idle_add(self._update_ui, current, signal, nets)

    def _update_ui(self, current, signal, nets):
        if current:
            self._conn_name.set_text(current)
            self._conn_badge.set_text("CONNECTED")
            self._conn_badge.remove_css_class("badge-none")
            self._conn_badge.add_css_class("badge-connected")
            self._signal_lbl.set_text(signal_bars(signal))
        else:
            self._conn_name.set_text("Not connected")
            self._conn_badge.set_text("OFFLINE")
            self._conn_badge.remove_css_class("badge-connected")
            self._conn_badge.add_css_class("badge-none")
            self._signal_lbl.set_text("")

        while self._list_box.get_first_child():
            self._list_box.remove(self._list_box.get_first_child())

        for net in nets:
            self._add_net_row(net, net["ssid"] == current)
        return False

    def _add_net_row(self, net, is_active):
        btn = Gtk.Button()
        btn.add_css_class("net-row-active" if is_active else "net-row")

        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)

        # Security badge instead of icon
        sec_lbl = Gtk.Label(label="WPA" if net["secured"] else "OPEN")
        sec_lbl.add_css_class("row-ssid-badge")

        name_lbl = Gtk.Label(label=net["ssid"])
        name_lbl.add_css_class("row-name-active" if is_active else "row-name")
        name_lbl.set_hexpand(True)
        name_lbl.set_halign(Gtk.Align.START)
        name_lbl.set_ellipsize(Pango.EllipsizeMode.END)

        cls = "sig-label-good" if net["signal"] >= 60 else "sig-label"
        sig_lbl = Gtk.Label(label=signal_bars(net["signal"]))
        sig_lbl.add_css_class(cls)

        row.append(sec_lbl)
        row.append(name_lbl)
        row.append(sig_lbl)
        btn.set_child(row)
        btn.connect("clicked", lambda b, s=net["ssid"]: self._on_connect(s))
        self._list_box.append(btn)

    def _on_connect(self, ssid):
        subprocess.Popen(["nmcli", "connection", "up", ssid])
        GLib.timeout_add(1500, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)

    def _on_disconnect(self, _):
        subprocess.Popen(["nmcli", "device", "disconnect", "wlan0"])
        GLib.timeout_add(1200, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)

    def _on_toggle(self, _):
        self._enabled = not self._enabled
        set_wifi(self._enabled)
        self._toggle_lbl.set_text("ON" if self._enabled else "OFF")
        self._toggle_lbl.remove_css_class("toggle-on" if not self._enabled else "toggle-off")
        self._toggle_lbl.add_css_class("toggle-on" if self._enabled else "toggle-off")
        GLib.timeout_add(800, lambda: threading.Thread(target=self._load_data, daemon=True).start() or False)


app = WiFiPanel()
app.run(None)
