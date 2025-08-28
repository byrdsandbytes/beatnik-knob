#!/bin/bash

# Installation script for Beatnik Knob on Raspberry Pi

set -e # Exit immediately if a command exits with a non-zero status.

# --- Colors for output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_header() {
    echo -e "\n${BLUE}--- $1 ---${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# --- Check for root privileges ---
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root. Please use 'sudo ./install.sh'"
   exit 1
fi

# Get the actual user who is running sudo
ACTUAL_USER=${SUDO_USER:-$(whoami)}
print_status "Running as root. Commands will be configured for user: $ACTUAL_USER"

# --- Step 1: System Setup ---
print_header "Step 1: Updating and Installing System Packages"
apt update && apt upgrade -y
apt install -y python3 python3-pip git curl jq nano python3-gpiozero python3-websockets
print_status "System packages installed successfully."

# --- Step 2: Configure Permissions ---
print_header "Step 2: Configuring GPIO Permissions"
usermod -a -G gpio "$ACTUAL_USER"
print_status "User '$ACTUAL_USER' has been added to the 'gpio' group."
print_warning "A reboot is required for group changes to take effect."

# --- Step 3: Make scripts executable ---
print_header "Step 3: Setting File Permissions"
# Assuming the script is run from the cloned repository directory
SCRIPT_DIR=$(pwd)
if [ -f "$SCRIPT_DIR/rotary/snapcast-volume-rotary.py" ]; then
    chmod +x "$SCRIPT_DIR/rotary/"*.py
    print_status "Made Python scripts executable."
else
    print_error "Could not find the 'rotary' directory. Please run this script from the root of the 'beatnik-knob' repository."
    exit 1
fi

# --- Final Instructions ---
echo -e "\n${GREEN}✅ Installation Complete!${NC}"
print_header "Next Steps"
echo "1. Please reboot your Raspberry Pi to apply the new group permissions:"
echo "   ${YELLOW}sudo reboot${NC}"
echo ""
echo "2. After rebooting, configure the script with your Snapcast details:"
echo "   ${YELLOW}nano rotary/snapcast-volume-rotary.py${NC}"
echo ""
echo "3. Test your hardware:"
echo "   ${YELLOW}cd rotary && python3 rotary-encoder-test.py${NC}"
echo ""
echo "4. Run the main controller:"
echo "   ${YELLOW}python3 snapcast-volume-rotary.py${NC}"
echo ""
echo "For more details on running as a service and troubleshooting, see the README.md file."
