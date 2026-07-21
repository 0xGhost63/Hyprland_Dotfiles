#!/usr/bin/env python3

import gi
import os
import re

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gdk, GLib, Pango

# Set application/class name so Hyprland window rules match correctly
GLib.set_prgname("quicknote")
GLib.set_application_name("Ghost's Note")

NOTE = os.path.expanduser("~/.local/share/quicknote.txt")
os.makedirs(os.path.dirname(NOTE), exist_ok=True)

class QuickNote(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="hypr.quicknote")

    def do_activate(self):
        self.win = Gtk.ApplicationWindow(application=self)
        self.win.set_title("Ghost's Note")
        # Bigger tile (default size increased to 650x450)
        self.win.set_default_size(650, 450)
        self.win.set_decorated(False)

        # Main layout container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.win.set_child(main_box)

        # Clean Header with a big bold modern title
        self.header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.header_box.set_margin_start(16)
        self.header_box.set_margin_end(16)
        self.header_box.set_margin_top(16)
        self.header_box.set_margin_bottom(8)

        title_label = Gtk.Label(label="GHOST'S NOTE")
        title_label.set_name("app-title")
        title_label.set_halign(Gtk.Align.START)
        self.header_box.append(title_label)

        # Spacer to push buttons to the right
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        self.header_box.append(spacer)

        main_box.append(self.header_box)

        # Slide-down Search Bar (hidden by default)
        self.search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.search_box.set_name("search-box")
        self.search_box.set_visible(False)
        self.search_box.set_margin_start(16)
        self.search_box.set_margin_end(16)
        self.search_box.set_margin_top(6)
        self.search_box.set_margin_bottom(6)

        self.search_entry = Gtk.Entry()
        self.search_entry.set_placeholder_text("Find in note...")
        self.search_entry.set_hexpand(True)
        self.search_entry.connect("changed", self.on_search_changed)
        
        self.search_count_label = Gtk.Label(label="")
        self.search_count_label.set_name("search-count")

        self.search_box.append(self.search_entry)
        self.search_box.append(self.search_count_label)
        main_box.append(self.search_box)

        # Scrolled window wrapper for the TextView
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        scroll.set_hexpand(True)

        self.text = Gtk.TextView()
        self.text.set_wrap_mode(Gtk.WrapMode.WORD)
        
        try:
            self.text.set_enable_undo(True)
        except AttributeError:
            try:
                self.text.set_property("enable-undo", True)
            except Exception:
                pass
        
        # Proper internal margins
        self.text.set_left_margin(16)
        self.text.set_right_margin(16)
        self.text.set_top_margin(8)
        self.text.set_bottom_margin(16)

        self.buffer = self.text.get_buffer()
        
        # Tags for highlighting and formatting
        self.search_tag = self.buffer.create_tag("search_highlight", background="#e0af68", foreground="#1a1b26")
        self.bold_tag = self.buffer.create_tag("bold", weight=Pango.Weight.BOLD)

        if os.path.exists(NOTE):
            with open(NOTE) as f:
                self.buffer.set_text(f.read())

        # Apply initial styling to loaded note
        self.apply_markdown_styling()

        self.buffer.connect("changed", self.on_buffer_changed)
        scroll.set_child(self.text)
        main_box.append(scroll)

        # Bottom status bar (Saved state + Word count)
        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        footer.set_margin_start(16)
        footer.set_margin_end(16)
        footer.set_margin_top(8)
        footer.set_margin_bottom(12)

        self.status_label = Gtk.Label(label="Saved")
        self.status_label.set_halign(Gtk.Align.START)

        self.stats_label = Gtk.Label(label="0 words | 0 chars")
        self.stats_label.set_halign(Gtk.Align.END)
        self.stats_label.set_hexpand(True)

        footer.append(self.status_label)
        footer.append(self.stats_label)
        main_box.append(footer)

        # Update initial stats
        self.update_stats()

        # Keyboard shortcuts controller
        key_controller = Gtk.EventControllerKey()
        key_controller.set_propagation_phase(Gtk.PropagationPhase.CAPTURE)
        key_controller.connect("key-pressed", self.on_key_pressed)
        self.win.add_controller(key_controller)

        # Modern glassmorphism / dark theme CSS styling matching Ghost's color scheme
        css = Gtk.CssProvider()
        css.load_from_data(b"""
        window, decoration, box {
            background-color: #1a1b26;
            border-radius: 16px;
        }
        #app-title {
            color: #7aa2f7;
            font-family: "Inter", "Segoe UI", sans-serif;
            font-size: 16px;
            font-weight: 900;
            letter-spacing: 1.5px;
        }
        scrolledwindow {
            background-color: transparent;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }
        #search-box {
            background-color: #16161e;
            border-radius: 8px;
            padding: 4px;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }
        entry {
            background-color: transparent;
            border: none;
            color: #c0caf5;
            font-size: 13px;
        }
        #search-count {
            color: #565f89;
            font-size: 11px;
            font-weight: bold;
            padding-right: 6px;
        }
        textview, text {
            background-color: transparent;
            color: #c0caf5;
            font-family: "Inter", "SF Pro Text", "Segoe UI", sans-serif;
            font-size: 15px;
            line-height: 1.6;
        }
        label {
            color: #565f89;
            font-size: 11px;
            font-weight: bold;
        }
        """)

        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            css,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

        self.win.present()

    def on_buffer_changed(self, buffer):
        if getattr(self, "_in_buffer_changed", False):
            return
        self._in_buffer_changed = True
        
        try:
            self.save(buffer)
            self.apply_markdown_styling()
            self.update_stats()
            self.status_label.set_text("Saving...")
            GLib.timeout_add(400, lambda: self.status_label.set_text("Saved") or False)
            if self.search_box.get_visible():
                self.perform_search()
        finally:
            self._in_buffer_changed = False

    def update_stats(self):
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        text = self.buffer.get_text(start, end, True)
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0
        self.stats_label.set_text(f"{word_count} words | {char_count} chars")

    def on_search_changed(self, entry):
        self.perform_search()

    def perform_search(self):
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        self.buffer.remove_tag(self.search_tag, start_iter, end_iter)

        query = self.search_entry.get_text()
        if not query:
            self.search_count_label.set_text("")
            return

        count = 0
        iter_ = self.buffer.get_start_iter()
        while True:
            res = iter_.forward_search(query, Gtk.TextSearchFlags.CASE_INSENSITIVE, None)
            if not res:
                break
            match_start, match_end = res[1], res[2]
            self.buffer.apply_tag(self.search_tag, match_start, match_end)
            iter_ = match_end
            count += 1

        if count > 0:
            self.search_count_label.set_text(f"{count} matches")
        else:
            self.search_count_label.set_text("No matches")

    def apply_markdown_styling(self):
        # Apply visual bolding to markdown **bold** blocks
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        self.buffer.remove_tag(self.bold_tag, start, end)

        text = self.buffer.get_text(start, end, True)
        for match in re.finditer(r"\*\*(.*?)\*\*", text):
            start_offset = match.start()
            end_offset = match.end()
            start_iter = self.buffer.get_iter_at_offset(start_offset)
            end_iter = self.buffer.get_iter_at_offset(end_offset)
            self.buffer.apply_tag(self.bold_tag, start_iter, end_iter)

    def toggle_bold(self):
        # Ctrl+B markdown toggler
        bounds = self.buffer.get_selection_bounds()
        if bounds:
            start_iter, end_iter = bounds
            text = self.buffer.get_text(start_iter, end_iter, True)
            if text.startswith("**") and text.endswith("**") and len(text) >= 4:
                # Strip bold formatting
                new_text = text[2:-2]
                self.buffer.delete(start_iter, end_iter)
                self.buffer.insert(start_iter, new_text)
            else:
                # Wrap selection in **
                new_text = f"**{text}**"
                self.buffer.delete(start_iter, end_iter)
                self.buffer.insert(start_iter, new_text)
        else:
            # Place empty bold markers and place cursor inside
            insert_mark = self.buffer.get_insert()
            cursor_iter = self.buffer.get_iter_at_mark(insert_mark)
            self.buffer.insert(cursor_iter, "****")
            cursor_iter = self.buffer.get_iter_at_mark(insert_mark)
            cursor_iter.backward_chars(2)
            self.buffer.place_cursor(cursor_iter)

    def toggle_checklist(self):
        insert_mark = self.buffer.get_insert()
        cursor_iter = self.buffer.get_iter_at_mark(insert_mark)

        line_start = cursor_iter.copy()
        if not line_start.starts_line():
            line_start.set_line_offset(0)

        line_end = line_start.copy()
        line_end.forward_to_line_end()

        line_text = self.buffer.get_text(line_start, line_end, True)

        if line_text.startswith("- [ ] "):
            new_start = line_start.copy()
            new_end = line_start.copy()
            new_end.forward_chars(6)
            self.buffer.delete(new_start, new_end)
            self.buffer.insert(line_start, "- [x] ")
        elif line_text.startswith("- [x] "):
            new_start = line_start.copy()
            new_end = line_start.copy()
            new_end.forward_chars(6)
            self.buffer.delete(new_start, new_end)
            self.buffer.insert(line_start, "- [ ] ")
        elif line_text.startswith("- "):
            new_start = line_start.copy()
            new_end = line_start.copy()
            new_end.forward_chars(2)
            self.buffer.delete(new_start, new_end)
            self.buffer.insert(line_start, "- [ ] ")
        else:
            self.buffer.insert(line_start, "- [ ] ")

    def insert_timestamp(self):
        now = GLib.DateTime.new_now_local()
        timestamp = now.format("[%Y-%m-%d %H:%M] ")
        self.buffer.insert_at_cursor(timestamp)

    def on_key_pressed(self, controller, keyval, keycode, state):
        print(f"DEBUG: keyval={keyval}, state={state}", flush=True)
        # Escape: close search bar if open, else close quicknote window
        if keyval == Gdk.KEY_Escape:
            if self.search_box.get_visible():
                self.search_box.set_visible(False)
                self.search_entry.set_text("")
                self.text.grab_focus()
                return True
            else:
                self.win.close()
                return True

        if state & Gdk.ModifierType.CONTROL_MASK:
            # Ctrl+B: Toggle Bold markdown
            if keyval in (Gdk.KEY_b, Gdk.KEY_B):
                self.toggle_bold()
                return True
            # Ctrl+C: Copy selected text to clipboard (using wl-copy for persistence on Wayland)
            if keyval in (Gdk.KEY_c, Gdk.KEY_C):
                bounds = self.buffer.get_selection_bounds()
                if bounds:
                    start_iter, end_iter = bounds
                    selected_text = self.buffer.get_text(start_iter, end_iter, True)
                    # Use wl-copy to persist clipboard text after closing quicknote
                    import subprocess
                    try:
                        subprocess.run(["wl-copy"], input=selected_text, text=True, check=True)
                    except Exception:
                        pass
                return True

            # Ctrl+X: Cut selected text to clipboard
            if keyval in (Gdk.KEY_x, Gdk.KEY_X):
                bounds = self.buffer.get_selection_bounds()
                if bounds:
                    start_iter, end_iter = bounds
                    selected_text = self.buffer.get_text(start_iter, end_iter, True)
                    # Use wl-copy to persist clipboard text after closing quicknote
                    import subprocess
                    try:
                        subprocess.run(["wl-copy"], input=selected_text, text=True, check=True)
                    except Exception:
                        pass
                    self.buffer.delete(start_iter, end_iter)
                return True

            # Ctrl+V: Paste text from clipboard
            if keyval in (Gdk.KEY_v, Gdk.KEY_V):
                import subprocess
                try:
                    pasted_text = subprocess.check_output(["wl-paste"], text=True)
                    if pasted_text:
                        bounds = self.buffer.get_selection_bounds()
                        if bounds:
                            start_iter, end_iter = bounds
                            self.buffer.delete(start_iter, end_iter)
                        self.buffer.insert_at_cursor(pasted_text)
                except Exception:
                    # Fallback to standard paste
                    pass
                return True

            # Ctrl+W / Ctrl+Q: Save and Quit
            if keyval in (Gdk.KEY_w, Gdk.KEY_W, Gdk.KEY_q, Gdk.KEY_Q):
                self.win.close()
                return True
            # Ctrl+N: Wipe Note
            if keyval in (Gdk.KEY_n, Gdk.KEY_N):
                self.buffer.set_text("")
                return True
            # Ctrl+D: Time/Date stamp
            if keyval in (Gdk.KEY_d, Gdk.KEY_D):
                self.insert_timestamp()
                return True
            # Ctrl+T: Toggle checklists
            if keyval in (Gdk.KEY_t, Gdk.KEY_T):
                self.toggle_checklist()
                return True
            # Ctrl+F: Search note
            if keyval in (Gdk.KEY_f, Gdk.KEY_F):
                is_visible = self.search_box.get_visible()
                self.search_box.set_visible(not is_visible)
                if not is_visible:
                    self.search_entry.grab_focus()
                else:
                    self.search_entry.set_text("")
                    self.text.grab_focus()
                return True
        return False

    def save(self, buffer):
        start = buffer.get_start_iter()
        end = buffer.get_end_iter()
        with open(NOTE, "w") as f:
            f.write(buffer.get_text(start, end, True))

app = QuickNote()
app.run(None)
