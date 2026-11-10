-- Custom autostart commands
hl.on("hyprland.start", function ()
    -- Launch Widgets (Workspace 3)
    hl.exec_cmd("~/dotfiles/scripts/launch_widgets.sh")

    -- MPRIS Art Daemon
    hl.exec_cmd("python3 ~/.config/hypr/scripts/mpris_art_daemon.py")

    -- Wallpaper Daemon & Restore (Animated Transition)
    hl.exec_cmd("awww-daemon")
    hl.exec_cmd("awww restore")

    -- Handle the power button in Hyprland instead of logind
    hl.exec_cmd("$HOME/.config/hypr/scripts/power_key_inhibit.sh")
end)
