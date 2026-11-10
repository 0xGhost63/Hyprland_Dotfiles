#!/usr/bin/env python3
"""
Media Dynamic Island — floating GTK3 media controller
Triggered by keybind, controlled entirely by keyboard.
← → = prev/next track | Space/Enter = play-pause | Esc = dismiss
Auto-dismisses after 6 seconds of inactivity.
"""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango

import cairo
import subprocess
import sys
import os
import tempfile
import urllib.request

# ── Kill any existing instance ─────────────────────────────
def is_already_running():
    try:
        result = subprocess.run(
            ["pgrep", "-f", "media_island.py"],
            capture_output=True, text=True
        )
        pids = [p for p in result.stdout.strip().split("\n") if p and p != str(os.getpid())]
        if pids:
            for pid in pids:
                subprocess.run(["kill", pid])
            sys.exit(0)
    except Exception:
        pass

is_already_running()


def run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=2).stdout.strip()
    except Exception:
        return ""


def playerctl(*args):
    return run(["playerctl"] + list(args))


def load_matugen_colors():
    colors = {
        "bg": "rgba(25, 17, 18, 0.95)",
        "border": "rgba(255, 178, 191, 0.5)",
        "primary": "#ffb2bf",
        "text": "#f0dee0",
        "subtext": "rgba(240, 222, 224, 0.65)"
    }
    css_path = os.path.expanduser("~/.config/waybar/colors.css")
    if os.path.exists(css_path):
        try:
            with open(css_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if "@define-color primary " in line:
                        colors["primary"] = line.split("primary")[1].strip(" ;")
                    elif "@define-color surface_container " in line:
                        hex_bg = line.split("surface_container")[1].strip(" ;")
                        h = hex_bg.lstrip("#")
                        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16) if len(h) >= 6 else (0,0,0)
                        colors["bg"] = f"rgba({r}, {g}, {b}, 0.94)"
                    elif "@define-color on_surface " in line:
                        colors["text"] = line.split("on_surface")[1].strip(" ;")
                    elif "@define-color primary_container " in line:
                        hex_out = line.split("primary_container")[1].strip(" ;")
                        h = hex_out.lstrip("#")
                        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16) if len(h) >= 6 else (0,0,0)
                        colors["border"] = f"rgba({r}, {g}, {b}, 0.5)"
        except Exception:
            pass
    return colors


mat_colors = load_matugen_colors()

CSS = f"""
window#media-island {{
    background-color: transparent;
    background: transparent;
}}

box#island-box {{
    background-color: {mat_colors['bg']};
    border-radius: 40px;
    border: 1.5px solid {mat_colors['border']};
    padding: 10px 22px 10px 14px;
    min-height: 78px;
}}

image#album-art {{
    border-radius: 12px;
}}

label#title-label {{
    color: {mat_colors['text']};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
    font-weight: bold;
}}

label#artist-label {{
    color: {mat_colors['primary']};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
}}

label#status-label {{
    color: {mat_colors['primary']};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
    margin-top: 1px;
}}

label#hint-label {{
    color: {mat_colors['subtext']};
    font-family: "JetBrainsMono Nerd Font";
    font-size: 9px;
}}

label#separator {{
    color: {mat_colors['border']};
    font-size: 24px;
    margin: 0px 6px;
}}
""".encode("utf-8")


class MediaIsland(Gtk.Window):
    def __init__(self):
        super().__init__()

        # ── Window setup ───────────────────────────────────
        self.set_title("media_island")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_app_paintable(True)
        self.set_name("media-island")

        # 100% Transparent background setup with Cairo
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.connect("draw", self.on_draw)

        # ── CSS styling ────────────────────────────────────
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── Main container (no outer margins) ──────────────
        island_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        island_box.set_name("island-box")
        self.add(island_box)

        # ── Album art (Larger: 76x76) ──────────────────────
        self.art_image = Gtk.Image()
        self.art_image.set_name("album-art")
        self.art_image.set_size_request(76, 76)
        self.art_image.set_valign(Gtk.Align.CENTER)
        island_box.pack_start(self.art_image, False, False, 0)

        # ── Separator ─────────────────────────────────────
        sep = Gtk.Label(label="│")
        sep.set_name("separator")
        sep.set_valign(Gtk.Align.CENTER)
        island_box.pack_start(sep, False, False, 0)

        # ── Text section ──────────────────────────────────
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        vbox.set_valign(Gtk.Align.CENTER)

        self.title_label = Gtk.Label()
        self.title_label.set_name("title-label")
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.title_label.set_max_width_chars(30)
        vbox.pack_start(self.title_label, False, False, 0)

        self.artist_label = Gtk.Label()
        self.artist_label.set_name("artist-label")
        self.artist_label.set_halign(Gtk.Align.START)
        self.artist_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.artist_label.set_max_width_chars(28)
        vbox.pack_start(self.artist_label, False, False, 0)

        self.status_label = Gtk.Label()
        self.status_label.set_name("status-label")
        self.status_label.set_halign(Gtk.Align.START)
        vbox.pack_start(self.status_label, False, False, 0)

        hint = Gtk.Label(label="← prev   spc pause   → next   esc close")
        hint.set_name("hint-label")
        hint.set_halign(Gtk.Align.START)
        vbox.pack_start(hint, False, False, 0)

        island_box.pack_start(vbox, True, True, 0)

        # ── Position: top-center directly below topbar ──────
        win_w, win_h = 510, 88
        self.set_default_size(win_w, win_h)
        self.realize()
        monitor = screen.get_monitor_geometry(0)
        x = monitor.x + (monitor.width - win_w) // 2
        y = monitor.y + 38   # 38px from top (just below Waybar)
        self.move(x, y)

        # ── Initial populate ───────────────────────────────
        self.update_info()

        # ── Key binding ────────────────────────────────────
        self.connect("key-press-event", self.on_key_press)

        # ── Auto-dismiss timer (6 seconds) ─────────────────
        self._dismiss_id = GLib.timeout_add_seconds(6, self.dismiss)

        self.show_all()

    def on_draw(self, widget, cr):
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()
        cr.set_operator(cairo.OPERATOR_OVER)
        return False

    def reset_timer(self):
        if self._dismiss_id:
            GLib.source_remove(self._dismiss_id)
        self._dismiss_id = GLib.timeout_add_seconds(6, self.dismiss)

    def update_info(self):
        title  = playerctl("metadata", "title")  or "No media playing"
        artist = playerctl("metadata", "artist") or "Media Player"
        status = playerctl("status")             or "Stopped"

        self.title_label.set_text(title)
        self.artist_label.set_text(artist)

        if status == "Playing":
            self.status_label.set_text("▶  Playing")
        elif status == "Paused":
            self.status_label.set_text("⏸  Paused")
        else:
            self.status_label.set_text("⏹  Stopped")

        # Album art
        art_url = playerctl("metadata", "mpris:artUrl")
        self._load_art(art_url)

    def _load_art(self, url):
        try:
            if url.startswith("file://"):
                path = url[7:]
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 76, 76, True)
                self.art_image.set_from_pixbuf(pb)
                return
            elif url.startswith("http"):
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                urllib.request.urlretrieve(url, tmp.name)
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmp.name, 76, 76, True)
                self.art_image.set_from_pixbuf(pb)
                return
        except Exception:
            pass
        # Fallback: music note icon
        self.art_image.set_from_icon_name("audio-x-generic", Gtk.IconSize.DIALOG)

    def on_key_press(self, widget, event):
        self.reset_timer()
        key = event.keyval

        if key == Gdk.KEY_Left:
            playerctl("previous")
            GLib.timeout_add(350, self.update_info)

        elif key == Gdk.KEY_Right:
            playerctl("next")
            GLib.timeout_add(350, self.update_info)

        elif key in (Gdk.KEY_space, Gdk.KEY_Return):
            playerctl("play-pause")
            GLib.timeout_add(200, self.update_info)

        elif key == Gdk.KEY_Escape:
            self.dismiss()

        return True   # consume all keys

    def dismiss(self):
        Gtk.main_quit()
        return False   # remove timeout source


if __name__ == "__main__":
    MediaIsland()
    Gtk.main()
