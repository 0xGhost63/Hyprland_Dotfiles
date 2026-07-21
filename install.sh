#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status
set -euo pipefail

# ANSI color codes for clean terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# Define source and target paths
BASE_DIR="$HOME/dotfiles"
CONFIG_TARGET="$HOME/.config"

echo -e "${MAGENTA}==================================================${NC}"
echo -e "${MAGENTA}         Hyprland Rice Installer Script           ${NC}"
echo -e "${MAGENTA}==================================================${NC}"

# 1. Environment verification
if [ ! -d "$BASE_DIR/config/hypr" ] || [ ! -d "$BASE_DIR/config/waybar" ]; then
    log_error "This installer must be run from $HOME/dotfiles containing the configuration folders."
    exit 1
fi

# 2. Dependency verification
log_info "Verifying core dependencies..."
for binary in hyprland waybar git eww kitty rofi matugen awww swaync dolphin; do
    if command -v "$binary" &> /dev/null; then
        log_success "Found dependency: $binary"
    else
        log_warning "Core dependency '$binary' is missing. You will need to install it later."
    fi
done

# 3. Create target configuration directory if missing
if [ ! -d "$CONFIG_TARGET" ]; then
    log_info "Creating missing directory: $CONFIG_TARGET"
    mkdir -p "$CONFIG_TARGET"
fi

# 4. Safely process configurations using symbolic links
for app in hypr waybar eww kitty rofi swaync matugen wlogout; do
    SRC="$BASE_DIR/config/$app"
    DST="$CONFIG_TARGET/$app"

    log_info "Processing configuration component: $app"

    # Verify source directory exists
    if [ ! -d "$SRC" ]; then
        log_error "Source folder $SRC does not exist in the repository. Skipping..."
        continue
    fi

    # Handle existing target destination safely
    if [ -L "$DST" ]; then
        log_info "Replacing existing symbolic link at $DST"
        rm "$DST"
    elif [ -d "$DST" ]; then
        BACKUP_PATH="${DST}_backup_$(date +%Y%m%d_%H%M%S)"
        log_warning "Existing folder found at $DST. Backing up to $BACKUP_PATH"
        mv "$DST" "$BACKUP_PATH"
    fi

    # Create the symbolic link
    ln -s "$SRC" "$DST"
    log_success "Linked $SRC -> $DST"
done

# 5. Fix permissions on internal repository scripts automatically
log_info "Ensuring internal configuration scripts are executable..."
find "$BASE_DIR" -maxdepth 1 -type f -name "*.sh" -exec chmod +x {} + 2>/dev/null || true
find "$BASE_DIR/scripts" -type f -name "*.sh" -exec chmod +x {} + 2>/dev/null || true
find "$BASE_DIR/config" -type f -path "*/scripts/*" -exec chmod +x {} + 2>/dev/null || true
find "$BASE_DIR/config" -type f \( -name "*.sh" -o -name "launch_*" -o -name "change_*" -o -name "sys_info" -o -name "*.py" \) -exec chmod +x {} + 2>/dev/null || true

# 6. Install and configure SDDM theme
if command -v sddm &> /dev/null || [ -d /usr/share/sddm ]; then
    echo ""
    log_info "SDDM display manager detected. Setting up Login theme..."
    
    # Prompt user for sudo privileges up front
    log_info "Requesting sudo permissions to install dependencies and configure the theme..."
    if sudo -v; then
        # Keep-alive sudo credentials during execution
        while kill -0 "$$" 2>/dev/null; do sudo -v; sleep 60; done &
        SUDO_KEEPALIVE_PID=$!
        
        # Trap to clean up keep-alive background job on exit
        trap 'kill $SUDO_KEEPALIVE_PID 2>/dev/null || true' EXIT

        # Arch/EndeavourOS: verify pacman-based deps instead of apt
        log_info "Verifying Qt5/SDDM dependencies via pacman..."
        MISSING=()
        for pkg in sddm xcb-util-cursor qt5-graphicaleffects qt5-quickcontrols qt5-quickcontrols2; do
            if ! pacman -Qi "$pkg" &> /dev/null; then
                MISSING+=("$pkg")
            fi
        done
        if [ ${#MISSING[@]} -eq 0 ]; then
            log_success "All SDDM/Qt5 dependencies already installed."
        else
            log_info "Installing missing dependencies: ${MISSING[*]}"
            sudo pacman -S --needed --noconfirm "${MISSING[@]}"
        fi

        # Deploy theme to system directory
        if [ -d "$BASE_DIR/config/Login theme" ]; then
            log_info "Deploying theme to /usr/share/sddm/themes/Login theme..."
            sudo mkdir -p /usr/share/sddm/themes
            sudo rm -rf "/usr/share/sddm/themes/Login theme"
            sudo cp -r "$BASE_DIR/config/Login theme" "/usr/share/sddm/themes/Login theme"
            
            # Fix ownership/permissions of copied files
            sudo chown -R root:root "/usr/share/sddm/themes/Login theme"
            sudo chmod -R 755 "/usr/share/sddm/themes/Login theme"
            log_success "Theme successfully copied."
        else
            log_error "Login theme folder was not found at $BASE_DIR/config/Login theme."
        fi

        # Copy custom theme fonts
        if [ -d "$BASE_DIR/config/Login theme/Fonts" ]; then
            log_info "Installing theme fonts to system directories..."
            sudo mkdir -p /usr/share/fonts/truetype/sddm-astronaut
            sudo rm -f /usr/share/fonts/truetype/sddm-astronaut/*
            sudo cp -r "$BASE_DIR/config/Login theme/Fonts/"* /usr/share/fonts/truetype/sddm-astronaut/
            sudo chown -R root:root /usr/share/fonts/truetype/sddm-astronaut
            sudo chmod 644 /usr/share/fonts/truetype/sddm-astronaut/*
            sudo fc-cache -f
            log_success "Fonts installed and system font cache updated."
        fi

        # Safely configure SDDM settings
        log_info "Updating SDDM theme configuration..."
        SDDM_CONF_DIR="/etc/sddm.conf.d"
        KDE_SETTINGS_CONF="$SDDM_CONF_DIR/kde_settings.conf"
        FALLBACK_CONF="$SDDM_CONF_DIR/sddm.conf"
        
        sudo mkdir -p "$SDDM_CONF_DIR"

        if [ -f "$KDE_SETTINGS_CONF" ]; then
            log_info "Backing up existing SDDM configuration at $KDE_SETTINGS_CONF"
            sudo cp "$KDE_SETTINGS_CONF" "${KDE_SETTINGS_CONF}.backup_$(date +%Y%m%d_%H%M%S)"
            
            log_info "Updating theme setting to Login theme inside $KDE_SETTINGS_CONF"
            if grep -q "Current=" "$KDE_SETTINGS_CONF"; then
                sudo sed -i 's/Current=.*/Current=Login theme/g' "$KDE_SETTINGS_CONF"
            else
                # Add [Theme] block if missing or just append theme line
                if grep -q "\[Theme\]" "$KDE_SETTINGS_CONF"; then
                    sudo sed -i '/\[Theme\]/a Current=Login theme' "$KDE_SETTINGS_CONF"
                else
                    echo -e "\n[Theme]\nCurrent=Login theme" | sudo tee -a "$KDE_SETTINGS_CONF" > /dev/null
                fi
            fi
        else
            log_info "Creating default configuration at $FALLBACK_CONF"
            if [ -f "$FALLBACK_CONF" ]; then
                sudo cp "$FALLBACK_CONF" "${FALLBACK_CONF}.backup_$(date +%Y%m%d_%H%M%S)"
            fi
            echo -e "[Theme]\nCurrent=Login theme" | sudo tee "$FALLBACK_CONF" > /dev/null
        fi
        log_success "SDDM configuration updated successfully."
    else
        log_error "Sudo authorization failed. Skipping theme deployment steps."
    fi
else
    log_info "SDDM is not installed or /usr/share/sddm folder is missing. Skipping theme installation."
fi

echo ""
echo -e "${GREEN}==================================================${NC}"
echo -e "${GREEN}      Environment Installation Completed!        ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo "You can test the SDDM theme by running:"
echo "sddm-greeter --test-mode --theme \"/usr/share/sddm/themes/Login theme/\""
