#!/bin/bash

# Beatnik Knob Setup Script for Raspberry Pi (Debian Bookworm Lite)
# This script installs all necessary dependencies and configures the system

set -e  # Exit on any error

echo "🎛️ Beatnik Knob Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}$1${NC}"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

# Get the actual user (not root when using sudo)
ACTUAL_USER=${SUDO_USER:-$USER}
USER_HOME=$(eval echo ~$ACTUAL_USER)

print_header "📋 System Information"
echo "User: $ACTUAL_USER"
echo "Home: $USER_HOME"
echo "OS: $(lsb_release -d | cut -f2)"
echo "Kernel: $(uname -r)"
echo ""

# Update system packages
print_header "📦 Updating System Packages"
apt update
apt upgrade -y

# Install required system packages
print_header "🔧 Installing System Dependencies"
apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    curl \
    jq \
    nano \
    systemd

# Install Python packages
print_header "🐍 Installing Python Dependencies"
pip3 install --break-system-packages \
    gpiozero \
    websockets \
    asyncio

# Alternative installation method if the above fails
if [ $? -ne 0 ]; then
    print_warning "System-wide pip installation failed, trying user installation..."
    sudo -u $ACTUAL_USER pip3 install --user \
        gpiozero \
        websockets \
        asyncio
fi

# Enable GPIO and other necessary interfaces
print_header "⚙️ Configuring GPIO and Interfaces"

# Add user to gpio group
usermod -a -G gpio $ACTUAL_USER
print_status "Added $ACTUAL_USER to gpio group"

# Enable GPIO interface (if not already enabled)
if ! grep -q "^dtparam=spi=on" /boot/config.txt; then
    echo "dtparam=spi=on" >> /boot/config.txt
    print_status "Enabled SPI interface"
fi

if ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt; then
    echo "dtparam=i2c_arm=on" >> /boot/config.txt
    print_status "Enabled I2C interface"
fi

# Ensure GPIO access
if ! grep -q "^dtparam=gpio=" /boot/config.txt; then
    echo "dtparam=gpio=on" >> /boot/config.txt
    print_status "Enabled GPIO interface"
fi

# Install Snapcast client (optional but recommended)
print_header "🎵 Installing Snapcast Client (Optional)"
read -p "Do you want to install Snapcast client? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Add Snapcast repository
    curl -s https://packagecloud.io/install/repositories/badaix/snapcast/script.deb.sh | bash
    apt update
    apt install -y snapclient
    
    # Enable snapclient service
    systemctl enable snapclient
    print_status "Snapcast client installed and enabled"
    
    print_warning "Please configure Snapcast client in /etc/snapclient.conf"
    print_warning "Set your Snapcast server host in the configuration file"
else
    print_status "Skipping Snapcast client installation"
fi

# Set up project permissions
print_header "🔑 Setting Up Project Permissions"
if [ -d "$USER_HOME/beatnik-knob" ]; then
    chown -R $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/beatnik-knob"
    chmod +x "$USER_HOME/beatnik-knob/rotary/"*.py
    print_status "Set correct permissions for project files"
fi

# Create udev rule for GPIO access (alternative to running as root)
print_header "🔧 Creating GPIO udev Rule"
cat > /etc/udev/rules.d/99-gpio.rules << EOF
SUBSYSTEM=="gpio*", PROGRAM="/bin/sh -c 'chown -R root:gpio /sys/class/gpio && chmod -R 775 /sys/class/gpio; chown -R root:gpio /sys/devices/virtual/gpio && chmod -R 775 /sys/devices/virtual/gpio'"
EOF

# Reload udev rules
udevadm control --reload-rules
udevadm trigger
print_status "Created GPIO udev rule for non-root access"

# Test Python imports
print_header "🧪 Testing Python Dependencies"
sudo -u $ACTUAL_USER python3 -c "
try:
    import gpiozero
    import websockets
    import asyncio
    import json
    import time
    print('✅ All Python dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

# Create example configuration
print_header "📝 Creating Example Configuration"
if [ ! -f "$USER_HOME/beatnik-knob/rotary/config.example.py" ]; then
    cat > "$USER_HOME/beatnik-knob/rotary/config.example.py" << EOF
# Example configuration for snapcast-volume-rotary.py
# Copy this file and modify the values below in your main script

# --- Snapcast Configuration ---
SNAPCAST_URI = "ws://beatnik-server.local:1780/jsonrpc"  # Update with your server
SNAPCAST_CLIENT_ID = "2c:cf:67:d4:b1:95"  # Update with your client ID

# --- Volume Settings ---
VOLUME_STEP = 5  # Volume change per encoder step (%)
THROTTLE_INTERVAL_S = 0.05  # Minimum time between commands (seconds)

# --- GPIO Pin Configuration ---
PIN_CLK = 17  # Rotary encoder CLK pin
PIN_DT = 18   # Rotary encoder DT pin  
PIN_SW = 27   # Rotary encoder button pin

# To find your client ID, run:
# curl -s http://your-snapcast-server:1780/jsonrpc -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' | jq '.result.server.groups[].clients[].id'
EOF
    chown $ACTUAL_USER:$ACTUAL_USER "$USER_HOME/beatnik-knob/rotary/config.example.py"
    print_status "Created example configuration file"
fi

# Summary and next steps
print_header "🎉 Installation Complete!"
echo ""
print_status "Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. 🔧 Connect your rotary encoder according to the wiring diagram in README.md"
echo "2. ⚙️  Configure your Snapcast server details in rotary/snapcast-volume-rotary.py:"
echo "   - Update SNAPCAST_URI with your server address"
echo "   - Update SNAPCAST_CLIENT_ID with your client ID"
echo "3. 🧪 Test your hardware with: python3 rotary/rotary-encoder-test.py"
echo "4. 🚀 Run the volume controller: python3 rotary/snapcast-volume-rotary.py"
echo "5. 🔄 (Optional) Set up as a systemd service using instructions in README.md"
echo ""
print_warning "⚠️  You may need to reboot for GPIO permissions to take effect"
print_warning "⚠️  Make sure to logout and login again to refresh group membership"
echo ""
echo "📖 For detailed instructions, see README.md"
echo "🐛 For troubleshooting, check the Troubleshooting section in README.md"
echo ""
print_header "Happy listening! 🎵"
