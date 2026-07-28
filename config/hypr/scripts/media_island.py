#!/usr/bin/env python3
"""
Media Dynamic Island — floating GTK3 media controller
Triggered by keybind, controlled entirely by keyboard.
← → = prev/next track | Space/Enter = play-pause | Esc = dismiss
Auto-dismisses after 6 seconds of inactivity.
"""

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf, Pango

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


CSS = b"""
window#media-island {
    background: transparent;
}

box#island-box {
    background: rgba(14, 10, 20, 0.88);
    border-radius: 28px;
    border: 1px solid rgba(122, 162, 247, 0.35);
    padding: 10px 18px 10px 14px;
}

image#album-art {
    border-radius: 12px;
}

label#title-label {
    color: #e2e2f0;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 14px;
    font-weight: bold;
}

label#artist-label {
    color: #7aa2f7;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 12px;
}

label#status-label {
    color: #00e5ff;
    font-family: "JetBrainsMono Nerd Font";
    font-size: 11px;
    margin-top: 2px;
}

label#hint-label {
    color: rgba(180, 180, 220, 0.55);
    font-family: "JetBrainsMono Nerd Font";
    font-size: 10px;
}

label#separator {
    color: rgba(122, 162, 247, 0.4);
    font-size: 20px;
    margin: 0px 6px;
}
"""


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

        # Transparent background
        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual:
            self.set_visual(visual)

        # ── CSS styling ────────────────────────────────────
        provider = Gtk.CssProvider()
        provider.load_from_data(CSS)
        Gtk.StyleContext.add_provider_for_screen(
            screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        # ── Main outer box ─────────────────────────────────
        outer = Gtk.Box()
        outer.set_margin_top(6)
        outer.set_margin_bottom(6)
        outer.set_margin_start(6)
        outer.set_margin_end(6)

        island_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        island_box.set_name("island-box")
        outer.pack_start(island_box, True, True, 0)
        self.add(outer)

        # ── Album art ─────────────────────────────────────
        self.art_image = Gtk.Image()
        self.art_image.set_name("album-art")
        self.art_image.set_size_request(56, 56)
        self.art_image.set_valign(Gtk.Align.CENTER)
        island_box.pack_start(self.art_image, False, False, 0)

        # ── Separator ─────────────────────────────────────
        sep = Gtk.Label(label="│")
        sep.set_name("separator")
        sep.set_valign(Gtk.Align.CENTER)
        island_box.pack_start(sep, False, False, 0)

        # ── Text section ──────────────────────────────────
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        vbox.set_valign(Gtk.Align.CENTER)

        self.title_label = Gtk.Label()
        self.title_label.set_name("title-label")
        self.title_label.set_halign(Gtk.Align.START)
        self.title_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.title_label.set_max_width_chars(28)
        vbox.pack_start(self.title_label, False, False, 0)

        self.artist_label = Gtk.Label()
        self.artist_label.set_name("artist-label")
        self.artist_label.set_halign(Gtk.Align.START)
        self.artist_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.artist_label.set_max_width_chars(26)
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

        # ── Position: top-center below waybar ─────────────
        self.set_default_size(460, 90)
        self.realize()
        monitor = screen.get_monitor_geometry(0)
        win_w = 460
        x = monitor.x + (monitor.width - win_w) // 2
        y = monitor.y + 40   # just below waybar
        self.move(x, y)

        # ── Initial populate ───────────────────────────────
        self.update_info()

        # ── Key binding ────────────────────────────────────
        self.connect("key-press-event", self.on_key_press)

        # ── Auto-dismiss timer (6 seconds) ─────────────────
        self._dismiss_id = GLib.timeout_add_seconds(6, self.dismiss)

        self.show_all()

    def reset_timer(self):
        if self._dismiss_id:
            GLib.source_remove(self._dismiss_id)
        self._dismiss_id = GLib.timeout_add_seconds(6, self.dismiss)

    def update_info(self):
        title  = playerctl("metadata", "title")  or "No media"
        artist = playerctl("metadata", "artist") or ""
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
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 56, 56, True)
                self.art_image.set_from_pixbuf(pb)
                return
            elif url.startswith("http"):
                tmp = tempfile.NamedTemporaryFile(suffix=".jpg", delete=False)
                urllib.request.urlretrieve(url, tmp.name)
                pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(tmp.name, 56, 56, True)
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
