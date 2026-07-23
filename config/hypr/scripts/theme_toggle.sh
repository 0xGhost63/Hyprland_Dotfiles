#!/bin/bash
# System-wide Dark / Light Mode Switcher

MODE="$1"

if [ "$MODE" = "light" ]; then
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-light' 2>/dev/null
    gsettings set org.gnome.desktop.interface gtk-theme 'Adwaita' 2>/dev/null
    gsettings set org.gnome.desktop.interface icon-theme 'Papirus' 2>/dev/null

    if [ -f "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf" ]; then
        sed -i 's/Net\/ThemeName.*/Net\/ThemeName "Adwaita"/' "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf"
        sed -i 's/Net\/IconThemeName.*/Net\/IconThemeName "Papirus"/' "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf"
        pkill -HUP xsettingsd 2>/dev/null
    fi

    for file in ~/.config/gtk-3.0/settings.ini ~/.config/gtk-4.0/settings.ini; do
        if [ -f "$file" ]; then
            sed -i 's/gtk-theme-name=.*/gtk-theme-name=Adwaita/' "$file"
            sed -i 's/gtk-icon-theme-name=.*/gtk-icon-theme-name=Papirus/' "$file"
            sed -i 's/gtk-application-prefer-dark-theme=.*/gtk-application-prefer-dark-theme=0/' "$file"
        fi
    done

    sed -i 's/ColorScheme=.*/ColorScheme=BreezeLight/' ~/.config/kdeglobals 2>/dev/null
    sed -i 's/ColorScheme=.*/ColorScheme=BreezeLight/' ~/.config/dolphinrc 2>/dev/null
    hyprctl reload 2>/dev/null
    notify-send -u low "System Theme" "Switched to Light Mode"

else
    gsettings set org.gnome.desktop.interface color-scheme 'prefer-dark' 2>/dev/null
    gsettings set org.gnome.desktop.interface gtk-theme 'Sweet-Dark' 2>/dev/null
    gsettings set org.gnome.desktop.interface icon-theme 'Papirus-Dark' 2>/dev/null

    if [ -f "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf" ]; then
        sed -i 's/Net\/ThemeName.*/Net\/ThemeName "Sweet-Dark"/' "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf"
        sed -i 's/Net\/IconThemeName.*/Net\/IconThemeName "Papirus-Dark"/' "$HOME/dotfiles/config/xsettingsd/xsettingsd.conf"
        pkill -HUP xsettingsd 2>/dev/null
    fi

    for file in ~/.config/gtk-3.0/settings.ini ~/.config/gtk-4.0/settings.ini; do
        if [ -f "$file" ]; then
            sed -i 's/gtk-theme-name=.*/gtk-theme-name=Sweet-Dark/' "$file"
            sed -i 's/gtk-icon-theme-name=.*/gtk-icon-theme-name=Papirus-Dark/' "$file"
            sed -i 's/gtk-application-prefer-dark-theme=.*/gtk-application-prefer-dark-theme=1/' "$file"
        fi
    done

    sed -i 's/ColorScheme=.*/ColorScheme=BreezeDark/' ~/.config/kdeglobals 2>/dev/null
    sed -i 's/ColorScheme=.*/ColorScheme=BreezeDark/' ~/.config/dolphinrc 2>/dev/null
    hyprctl reload 2>/dev/null
    notify-send -u low "System Theme" "Switched to Dark Mode"
fi
