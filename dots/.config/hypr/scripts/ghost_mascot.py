#!/usr/bin/env python3
import sys
import os
import math
import cairo
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

VIBE_CAT_GIF = os.path.expanduser("~/dotfiles/config/fastfetch/vibe_cat.gif")

class VibeCatMascot(Gtk.Window):
    def __init__(self):
        super().__init__(title="ghost_mascot")
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_decorated(False)
        self.set_keep_above(True)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_accept_focus(False)

        # 100% Click-Through Window Region
        region = cairo.Region()
        self.input_shape_combine_region(region)

        screen = self.get_screen()
        visual = screen.get_rgba_visual()
        if visual and screen.is_composited():
            self.set_visual(visual)

        self.set_app_paintable(True)
        self.connect("draw", self.on_draw)

        if os.path.exists(VIBE_CAT_GIF):
            self.anim = GdkPixbuf.PixbufAnimation.new_from_file(VIBE_CAT_GIF)
            self.iter = self.anim.get_iter(None)
        else:
            self.anim = None
            self.iter = None

        self.set_default_size(220, 220)

        # Frame animation loop (40ms ~ 25 FPS)
        GLib.timeout_add(40, self.update_frame)

    def update_frame(self):
        if self.iter:
            self.iter.advance(None)
            self.queue_draw()
        return True

    def on_draw(self, widget, cr):
        # 100% Transparent Background Clear
        cr.set_operator(cairo.OPERATOR_SOURCE)
        cr.set_source_rgba(0, 0, 0, 0)
        cr.paint()

        cr.set_operator(cairo.OPERATOR_OVER)

        if self.iter:
            pixbuf = self.iter.get_pixbuf()
            if pixbuf:
                scaled = pixbuf.scale_simple(220, 220, GdkPixbuf.InterpType.BILINEAR)
                if scaled:
                    cr.save()
                    # Circular clipping mask
                    cr.arc(110, 110, 105, 0, 2 * math.pi)
                    cr.clip()

                    Gdk.cairo_set_source_pixbuf(cr, scaled, 0, 0)
                    cr.paint_with_alpha(1.0) # 100% Opaque Rendering
                    cr.restore()
        return False

def main():
    app = VibeCatMascot()
    app.show_all()
    app.set_keep_above(True)
    app.present()
    Gtk.main()

if __name__ == "__main__":
    main()
