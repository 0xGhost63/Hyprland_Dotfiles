hl.bind("CTRL+SUPER+ALT+Slash", hl.dsp.exec_cmd("xdg-open ~/.config/hypr/custom/keybinds.lua"), {description = "Edit user keybinds"} )

-- Ghost Notes (Super+N)
hl.bind("SUPER + N", hl.dsp.exec_cmd("~/.config/hypr/scripts/notes.sh"), {description = "Ghost Quick Notes"})

-- Cat Mascot Toggle (Super+Alt+G)
hl.bind("SUPER + ALT + G", hl.dsp.exec_cmd("~/.config/hypr/scripts/ghost_toggle.sh"), {description = "Toggle Ghost Cat Mascot"})

-- Wallpaper Picker (Super+W)
hl.bind("SUPER + W", hl.dsp.exec_cmd("~/.config/hypr/scripts/wppicker.sh"), {description = "Wallpaper Picker"})

-- Dashboard (Super+M)
hl.bind("SUPER + M", hl.dsp.exec_cmd("~/.config/eww/dashboard/launch_dashboard"), {description = "Eww Dashboard"})

-- Media Dynamic Island (Super+O)
hl.bind("SUPER + O", hl.dsp.exec_cmd("python3 ~/.config/hypr/scripts/media_island.py"), {description = "Media Island"})

-- Terminal and App Launcher
hl.bind("SUPER + Return", hl.dsp.exec_cmd("kitty"), {description = "Terminal"})
hl.bind("SUPER + SHIFT + Return", hl.dsp.exec_cmd("[float; size 800 550] kitty"), {description = "Floating Terminal"})
hl.bind("SUPER + Q", hl.dsp.exec_cmd("pkill rofi || hyprctl dispatch killactive"), {description = "Close Window"})
hl.bind("SUPER + D", hl.dsp.exec_cmd("rofi -show drun || fuzzel"), {description = "App Menu"})
hl.bind("SUPER + SHIFT + S", hl.dsp.exec_cmd("~/.config/hypr/scripts/screenshot.sh"), {description = "Screenshot"})
hl.bind("SUPER + SHIFT + Q", hl.dsp.exec_cmd("~/.config/hypr/scripts/KillActiveProcess.sh"), {description = "Kill Active Process"})
hl.bind("SUPER + R", hl.dsp.exec_cmd("~/.config/hypr/scripts/wbrestart.sh"), {description = "Restart Waybar"})
hl.bind("SUPER + L", hl.dsp.exec_cmd("~/.config/hypr/scripts/hyprlock.sh"), {description = "Lock Screen"})

-- Additional User Bindings
hl.bind("SUPER + C", hl.dsp.exec_cmd("hyprpicker -a"), {description = "Color Picker"})
hl.bind("SUPER + B", hl.dsp.exec_cmd("xdg-open 'https://'"), {description = "Default Browser"})
hl.bind("SUPER + E", hl.dsp.exec_cmd("dolphin"), {description = "File Manager"})
hl.bind("SUPER + Space", hl.dsp.window.float({ action = "toggle" }), {description = "Toggle Floating"})
hl.bind("SUPER + SHIFT + F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }), {description = "Fullscreen"})
hl.bind("SUPER + SHIFT + E", hl.dsp.exec_cmd("kitty yazi"), {description = "Yazi File Manager"})
hl.bind("SUPER + Period", hl.dsp.exec_cmd("~/.config/hypr/scripts/emoji.sh"), {description = "Emoji Picker"})
hl.bind("SUPER + SHIFT + G", hl.dsp.exec_cmd("~/.config/hypr/scripts/lockin_mode.sh"), {description = "Lock In Mode"})
hl.bind("SUPER + SHIFT + N", hl.dsp.exec_cmd("~/.config/hypr/scripts/hyprshade_menu.sh"), {description = "Shaders Menu"})
hl.bind("SUPER + S", hl.dsp.exec_cmd("~/dotfiles/scripts/startup.sh"), {description = "Startup Script"})
