hl.bind("CTRL+SUPER+ALT+Slash", hl.dsp.exec_cmd("xdg-open ~/.config/hypr/custom/keybinds.lua"), {description = "Config: Edit user keybinds"} )

-- Ghost Notes (Super+N)
hl.bind("SUPER + N", hl.dsp.exec_cmd("~/.config/hypr/scripts/notes.sh"), {description = "Utilities: Ghost Quick Notes"})

-- Cat Mascot Toggle (Super+Alt+G)
hl.bind("SUPER + ALT + G", hl.dsp.exec_cmd("~/.config/hypr/scripts/ghost_toggle.sh"), {description = "Utilities: Toggle Ghost Cat Mascot"})

-- Wallpaper Picker (Super+W)
hl.bind("SUPER + W", hl.dsp.global("quickshell:wallpaperSelectorToggle"), {description = "Shell: Wallpaper Picker"})

-- Dashboard (Super+M)
hl.bind("SUPER + M", hl.dsp.exec_cmd("~/.config/eww/dashboard/launch_dashboard"), {description = "App: Eww Dashboard"})

-- Media Dynamic Island (Super+O)
hl.bind("SUPER + O", hl.dsp.exec_cmd("python3 ~/.config/hypr/scripts/media_island.py"), {description = "Shell: Media Island"})

-- App Launcher (Super+D)
hl.bind("SUPER + D", hl.dsp.exec_cmd("qs -c $qsConfig ipc call search apps"), {description = "App: App Menu"})

-- Floating Terminal (Super+Shift+Return)
hl.bind("SUPER + SHIFT + Return", hl.dsp.exec_cmd("[float; size 800 550] kitty"), {description = "App: Floating Terminal"})

-- Kill Active Process (Super+Shift+Q)
hl.bind("SUPER + SHIFT + Q", hl.dsp.exec_cmd("~/.config/hypr/scripts/KillActiveProcess.sh"), {description = "Window: Kill Active Process"})

-- Restart Waybar (Super+R)
hl.bind("SUPER + R", hl.dsp.exec_cmd("~/.config/hypr/scripts/wbrestart.sh"), {description = "Shell: Restart Waybar"})

-- Toggle Floating (Super+Space)
hl.bind("SUPER + Space", hl.dsp.window.float({ action = "toggle" }), {description = "Window: Toggle Floating"})

-- Fullscreen (Super+Shift+F)
hl.bind("SUPER + SHIFT + F", hl.dsp.window.fullscreen({ mode = "fullscreen", action = "toggle" }), {description = "Window: Fullscreen"})

-- Yazi File Manager (Super+Shift+E)
hl.bind("SUPER + SHIFT + E", hl.dsp.exec_cmd("kitty yazi"), {description = "App: Yazi File Manager"})

-- Lock In Mode (Super+Shift+G)
hl.bind("SUPER + SHIFT + G", hl.dsp.exec_cmd("~/.config/hypr/scripts/lockin_mode.sh"), {description = "Utilities: Lock In Mode"})

-- Screen Shaders Menu (Super+Shift+H) -- moved from Super+Shift+N to avoid the right-sidebar binding
hl.bind("SUPER + SHIFT + H", hl.dsp.exec_cmd("~/.config/hypr/scripts/hyprshade_menu.sh"), {description = "Screen: Shaders Menu"})

-- Startup Script (Ctrl+Super+Alt+S) -- moved from Super+S to avoid the scratchpad binding
hl.bind("CTRL + SUPER + ALT + S", hl.dsp.exec_cmd("~/dotfiles/scripts/startup.sh"), {description = "Config: Startup Script"})


