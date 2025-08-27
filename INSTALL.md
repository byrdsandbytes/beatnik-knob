# Beatnik Knob Installation Guide for Raspberry Pi

## Prerequisites

- Raspberry Pi (3B+ or newer recommended) with Debian Bookworm Lite
- MicroSD card (16GB or larger)
- Rotary encoder module (KY-040 or compatible)
- Jumper wires
- Internet connection for the Pi

## Step-by-Step Installation

### 1. Prepare Raspberry Pi OS

1. **Download Raspberry Pi OS Lite (Bookworm)**:
   - Visit [rpi.org](https://www.raspberrypi.org/software/operating-systems/)
   - Download "Raspberry Pi OS Lite (64-bit)" with Debian Bookworm

2. **Flash to SD Card**:
   - Use Raspberry Pi Imager or balenaEtcher
   - Enable SSH and configure WiFi during imaging (recommended)

3. **Boot and Initial Setup**:
   ```bash
   # Update system
   sudo apt update && sudo apt upgrade -y
   
   # Enable GPIO interface
   sudo raspi-config
   # Navigate to: Interface Options > GPIO > Enable
   ```

### 2. Hardware Setup

**Wiring the Rotary Encoder**:

```
Rotary Encoder    Raspberry Pi
    CLK     →     GPIO 17 (Pin 11)
    DT      →     GPIO 18 (Pin 12)
    SW      →     GPIO 27 (Pin 13)
    VCC     →     3.3V    (Pin 1)
    GND     →     Ground  (Pin 6)
```

**Visual Pin Layout** (looking at Pi from above, GPIO pins at top):
```
3.3V  [1] [2]  5V
      [3] [4]  5V
      [5] [6]  GND  ← Connect encoder GND here
      [7] [8]
      [9] [10]
CLK → [11][12] ← DT
SW  → [13][14]
```

### 3. Software Installation

1. **Clone the Repository**:
   ```bash
   cd ~
   git clone https://github.com/Idrimi/beatnik-knob.git
   cd beatnik-knob
   ```

2. **Run Automated Setup**:
   ```bash
   chmod +x setup.sh
   sudo ./setup.sh
   ```
   
   The setup script will:
   - Install Python dependencies
   - Configure GPIO permissions
   - Set up system services
   - Create example configuration

3. **Manual Installation** (if automated setup fails):
   ```bash
   # Install Python packages
   pip3 install --user gpiozero websockets
   
   # Add user to gpio group
   sudo usermod -a -G gpio $USER
   
   # Logout and login for group changes to take effect
   ```

### 4. Configuration

1. **Find Your Snapcast Client ID**:
   ```bash
   # Method 1: Using curl and jq
   curl -s http://YOUR_SNAPCAST_SERVER:1780/jsonrpc \
     -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' | \
     jq '.result.server.groups[].clients[].id'
   
   # Method 2: Check Snapcast web interface
   # Open http://YOUR_SNAPCAST_SERVER:1780 in browser
   ```

2. **Edit Configuration**:
   ```bash
   cd ~/beatnik-knob/rotary
   nano snapcast-volume-rotary.py
   ```
   
   Update these lines:
   ```python
   SNAPCAST_URI = "ws://YOUR_SERVER_IP:1780/jsonrpc"
   SNAPCAST_CLIENT_ID = "YOUR_CLIENT_ID_HERE"
   ```

### 5. Testing

1. **Test Hardware**:
   ```bash
   cd ~/beatnik-knob/rotary
   python3 rotary-encoder-test.py
   ```
   
   You should see output when rotating the encoder and pressing the button.

2. **Test Volume Controller**:
   ```bash
   python3 snapcast-volume-rotary.py
   ```
   
   Expected output:
   ```
   🔌 Trying to connect to ws://your-server:1780/jsonrpc...
   ✅ WebSocket connection established!
   ✅ Initial state synced: Volume is 50%, Mute is AN
   ```

### 6. Set Up as System Service

1. **Install Service File**:
   ```bash
   sudo cp ~/beatnik-knob/beatnik-knob.service /etc/systemd/system/
   sudo systemctl daemon-reload
   ```

2. **Enable and Start Service**:
   ```bash
   sudo systemctl enable beatnik-knob.service
   sudo systemctl start beatnik-knob.service
   ```

3. **Check Service Status**:
   ```bash
   sudo systemctl status beatnik-knob.service
   journalctl -u beatnik-knob.service -f
   ```

## Troubleshooting

### Common Issues

**"Permission denied" GPIO errors**:
```bash
# Add user to gpio group and reboot
sudo usermod -a -G gpio $USER
sudo reboot
```

**"Module not found" errors**:
```bash
# Reinstall Python packages
pip3 install --user --force-reinstall gpiozero websockets
```

**Cannot connect to Snapcast server**:
```bash
# Test connectivity
ping YOUR_SNAPCAST_SERVER
telnet YOUR_SNAPCAST_SERVER 1780

# Check if server is running
curl http://YOUR_SNAPCAST_SERVER:1780/jsonrpc \
  -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}'
```

**Encoder not responding**:
- Double-check wiring connections
- Verify GPIO pin numbers in code match your wiring
- Test with multimeter if available

### Getting Help

1. **Check system logs**:
   ```bash
   journalctl -u beatnik-knob.service -n 50
   ```

2. **Run in debug mode**:
   ```bash
   cd ~/beatnik-knob/rotary
   python3 -u snapcast-volume-rotary.py
   ```

3. **Verify hardware connections**:
   ```bash
   # Check GPIO state
   gpio readall  # If gpio command is available
   ```

## Performance Tips

- Use a Class 10 or better SD card for best performance
- Consider using a USB 3.0 flash drive as root filesystem for better I/O
- Ensure stable power supply (proper power adapter, not USB power from PC)
- Keep the Pi cool with adequate ventilation or heatsinks

## Next Steps

Once everything is working:
- Customize volume step size and other settings
- Create additional hardware controls (more buttons, LEDs, etc.)
- Integrate with other home automation systems
- Set up monitoring and alerting for the service

Enjoy your physical Snapcast volume control! 🎵
