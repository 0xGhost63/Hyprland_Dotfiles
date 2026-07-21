# Hyprland Desktop Configuration

Welcome to my personal Hyprland setup. This repository contains the complete configuration files, scripts, assets, and themes I use to build a clean, unified, and highly responsive Linux desktop environment. 

The configuration focuses on blending Tokyo Night-inspired aesthetics with optimized, low-latency system utilities. Every component is designed to behave predictably, respond instantly to input, and maintain visual cohesion across tiling and floating states.

---

## Key Features

### 1. SDDM Login Screen (Astronaut Theme)
The system login screen uses a customized, Qt5-compliant branch of the Keyitdev Astronaut Theme. It has been modified specifically for stability and alignment on systems running older SDDM greeters:
*   **Qt5 Compatibility:** Built entirely with Qt5 Graphical Effects (`QtGraphicalEffects 1.0`) and Quick Controls to prevent version mismatches or fallback screen errors common in modern Qt6 themes.
*   **Asset Correction:** Fixed reference paths to locate system and user icon files natively, resolving missing graphics.
*   **Text Centering & Formatting:** Modified the username and password text fields (`Input.qml` and `UserList.qml`) to enforce vertical alignment (`verticalAlignment: TextInput.AlignVCenter`) and remove restrictive style padding. This resolves issues where usernames and password masks were cut off at the top.
*   **Clean Session Selector:** Integrated session option selector at the bottom of the card, allowing you to choose between Hyprland, Plasma, GNOME, or XFCE on the fly.

### 2. High-Performance Eww Control Center
The control center is built using Elkowar's Wacky Widgets (Eww) and contains several modules:
*   **System Controls:** Volume and brightness sliders built using GTK scale widgets. These widgets execute lightweight system binaries (`pamixer` and `brightnessctl`) directly instead of calling shell script wrappers, reducing input lag.
*   **Scroll wheel support:** Hovering over the audio or backlight scale and scrolling will immediately adjust the values in 15% steps.
*   **Quick Links:** High-resolution, background-free SVG launch icons for popular productivity tools (Gmail, Claude, GitHub, YouTube, Instagram) laid out in a clean grid.
*   **Monitoring Modules:** Real-time visual tracking of CPU load, memory utilization, local weather reports, system uptime, and battery state.
*   **Media Controller:** Clean media player card integrated with Spotify metadata query scripts.

### 3. Waybar Integration
A minimal, premium status bar positioned at the top of the monitor layout:
*   **Workspace Indicators:** Dynamically updates workspace states to highlight active, occupied, and empty virtual workspaces.
*   **System Gauges:** Real-time text and icon representations of network connectivity status, battery drainage, audio outputs, and clock/calendar modules.

### 4. Custom GTK4 Control Panels
Replaced legacy system trays with modern, floating GTK4-based dialog windows for essential connectivity:
*   **Bluetooth Panel (`btpanel.py`):** A custom Python/GTK4 panel that scans, connects, and configures Bluetooth hardware in a clean dialog.
*   **WiFi Panel:** A matching panel built to manage wireless network endpoints.
*   **Tokyo Night Style:** Customized stylesheet matching the Tokyo Night system colors, dark borders, and smooth margins.

### 5. Kitty Terminal Customizations
The terminal configuration is optimized for fast keyboard navigation:
*   **Text Navigation:** Restored standard shell word-by-word cursor movement using `Ctrl + Left` and `Ctrl + Right` keys.
*   **Split Controls:** Reallocated local Kitty window splitting and layouts to `Ctrl + Alt + Arrow` keys to prevent keybinding conflicts.
*   **Scroll Sensitivity:** Multiplied touchpad and wheel scroll speeds (`wheel_scroll_multiplier 5.0`) to make reading long logs and source files faster.
*   **Secure History Clearing:** The `clear` command is aliased to purge active terminal buffers and scrollbacks, preventing scrollback history extraction when clearing the screen.

### 6. Quicknote Scratchpad
A lightweight note-taking utility that runs as a floating scratchpad:
*   **Window Rules:** Tied to keybinds to appear as a centered overlay.
*   **GTK4 Clipboard Fix:** Fixed GTK4 selection bounds behavior in the python backend (`quicknote.py`), resolving crashes when coping or pasting selections.

---

## Directory Structure

Here is a breakdown of the repository files and directories:

*   **`config/hypr/`**
    *   `hyprland.conf`: The main configuration file handling compositor variables, window gaps, mouse rules, and hardware configurations.
    *   `configs/`: Partitioned configuration files split by function, including keybindings, window rules (`windowrules.conf`), and theme settings (`looknfeel.conf`).
    *   `scripts/`: Internal scripting library containing helper utilities, clipboard managers, and background helpers (such as `quicknote.py` and `btpanel.py`).
*   **`config/waybar/`**
    *   `config`: Layout declarations and module structures for the status bar.
    *   `style.css`: Visual styling and CSS properties for all status bar icons and elements.
*   **`config/eww/dashboard/`**
    *   `eww.yuck`: Structural layout configuration for the control widgets.
    *   `eww.scss`: Variables and style definitions for the widgets.
*   **`config/kitty/`**
    *   `kitty.conf`: Primary terminal configurations, shortcuts, scroll speeds, and Tokyo Night color palette maps.
*   **`config/Login theme/`**
    *   Custom Qt5 Astronaut theme containing source QML scripts, fonts, asset directories, and config parameters.
*   **`scripts/`**
    *   `launch_widgets.sh`: Widget management launch script.
    *   `startup.sh`: Background process startup script.
    *   `wppicker.sh`: Wallpaper picking script.
*   **`install.sh`**
    *   The unified, fault-tolerant bash installation script.

---

## System Requirements

To run this desktop rice environment on Arch Linux / EndeavourOS, install the following packages:

### Arch Linux / EndeavourOS Package Requirements
Install the required packages using `pacman` and `yay`:
```bash
sudo pacman -S --needed \
  hyprland \
  waybar \
  eww \
  kitty \
  rofi \
  matugen \
  awww \
  swaync \
  dolphin \
  brightnessctl \
  pamixer \
  wireplumber \
  fastfetch \
  cava \
  tty-clock \
  sddm \
  xcb-util-cursor \
  qt5-graphicaleffects \
  qt5-quickcontrols \
  qt5-quickcontrols2 \
  libnotify \
  playerctl
```

---

## Installation Process

To safely install the configuration files on your system:

1. Clone this repository directly into your home folder. Do not rename the target directory, as internal scripts resolve using the `~/dotfiles` path:
    ```bash
    git clone https://github.com/0xGhost63/Hyprland_Dotfiles.git ~/dotfiles
    ```

2. Navigate to the repository:
    ```bash
    cd ~/dotfiles
    ```

3. Make the installer executable:
    ```bash
    chmod +x install.sh
    ```

4. Execute the installer script:
    ```bash
    ./install.sh
    ```

### What the Installer Script Does:
* **Dependency Check:** Scans the active path to verify core utilities (`hyprland`, `waybar`, `eww`, `kitty`, `rofi`, `matugen`, `awww`, `swaync`, `dolphin`) are installed.
* **Safe Backups:** Checks for existing configuration folders under `~/.config/` and creates backups appended with timestamps to guarantee no user settings are lost.
* **Symbolic Links:** Symlinks configuration directories (`hypr`, `waybar`, `eww`, `kitty`, `rofi`, `swaync`, `matugen`, `wlogout`) from the repository to your system directories.
* **Permission Tuning:** Automatically scans all internal scripts inside `config/` and `scripts/` and applies executable permissions (`chmod +x`).
* **SDDM Deployment:** Deploys the Qt5 Astronaut theme to `/usr/share/sddm/themes/Login theme`, installs fonts, and configures `/etc/sddm.conf.d`.

---

## Keybindings Reference

| Shortcut | Action |
|---|---|
| `Super + Return` | Terminal (`kitty`) |
| `Ctrl + E` / `Super + E` | File Manager (`dolphin`) |
| `Super + W` | Wallpaper Selector (`rofi` + `matugen` 60fps animation) |
| `Super + D` | Application Launcher (`rofi`) |
| `Super + M` | Eww Control Dashboard |
| `Super + Escape` | Power Logout Menu (`wlogout`) |
| `Super + S` | Desktop Widgets (`tty-clock`, `cava`, `unimatrix`) |
| `Super + Q` | Close Active Window |
| `Super + R` | Restart Waybar & Swaync |

---

## Testing and Customization

### Testing the SDDM Theme
You can verify the theme and font configurations without logging out by running:
```bash
sddm-greeter --test-mode --theme "/usr/share/sddm/themes/Login theme/"
```
