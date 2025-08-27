# Installation Guide - Beatnik Knob on Raspberry Pi

## Prerequisites

- Raspberry Pi with Debian Bookworm Lite
- Rotary encoder (KY-040 or similar)
- Internet connection

## Step-by-Step Installation

### 1. Prepare Your Raspberry Pi

Flash Raspberry Pi OS Lite to SD card and boot your Pi.

### 2. Connect Hardware

Wire the rotary encoder to your Raspberry Pi:

```
Rotary Encoder → Raspberry Pi
CLK     → GPIO 17 (Pin 11)
DT      → GPIO 18 (Pin 12)  
SW      → GPIO 27 (Pin 13)
VCC     → 3.3V    (Pin 1)
GND     → Ground  (Pin 6)
```

### 3. Update System

```bash
sudo apt update
sudo apt upgrade -y
```

### 4. Install Dependencies

```bash
# Install system packages
sudo apt install -y python3 python3-pip git curl jq nano

# Install Python libraries
pip3 install --user gpiozero websockets
```

### 5. Configure Permissions

```bash
# Add user to gpio group
sudo usermod -a -G gpio $USER

# Logout and login (or reboot) for changes to take effect
sudo reboot
```

### 6. Get the Code

```bash
# Clone repository
git clone https://github.com/Idrimi/beatnik-knob.git
cd beatnik-knob

# Make scripts executable  
chmod +x rotary/*.py
```

### 7. Find Your Snapcast Client ID

```bash
# Replace YOUR_SERVER_IP with your Snapcast server IP
curl -s http://YOUR_SERVER_IP:1780/jsonrpc \
  -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' | \
  jq '.result.server.groups[].clients[].id'
```

### 8. Configure the Script

```bash
nano rotary/snapcast-volume-rotary.py
```

Edit these lines:
```python
SNAPCAST_URI = "ws://YOUR_SERVER_IP:1780/jsonrpc"
SNAPCAST_CLIENT_ID = "YOUR_CLIENT_ID_FROM_STEP_7"
```

### 9. Test Hardware

```bash
cd rotary
python3 rotary-encoder-test.py
```

You should see output when rotating and pressing the encoder.

### 10. Run the Volume Controller

```bash
python3 snapcast-volume-rotary.py
```

If successful, you'll see:
```
🔌 Trying to connect to ws://your-server:1780/jsonrpc...
✅ WebSocket connection established!
✅ Initial state synced: Volume is 50%, Mute is AN
```

## Make it Run Automatically (Optional)

### Create System Service

```bash
sudo nano /etc/systemd/system/beatnik-knob.service
```

Add this content (adjust paths if needed):
```ini
[Unit]
Description=Beatnik Knob Volume Controller
After=network.target

[Service]
Type=simple
User=pi
Group=gpio
WorkingDirectory=/home/pi/beatnik-knob/rotary
ExecStart=/usr/bin/python3 snapcast-volume-rotary.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Enable and Start Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable beatnik-knob.service

# Start service now
sudo systemctl start beatnik-knob.service

# Check status
sudo systemctl status beatnik-knob.service
```

## Troubleshooting

### Permission Denied Errors
Make sure you rebooted after adding user to gpio group:
```bash
groups  # Should show 'gpio' in the list
```

### Python Import Errors
Reinstall packages:
```bash
pip3 install --user --force-reinstall gpiozero websockets
```

### Cannot Connect to Server
Test connectivity:
```bash
ping YOUR_SERVER_IP
telnet YOUR_SERVER_IP 1780
```

### Hardware Not Responding
- Double-check wiring
- Verify GPIO pins match your configuration
- Test individual components

### Service Issues
Check logs:
```bash
journalctl -u beatnik-knob.service -f
```

You're all set! Your rotary encoder should now control Snapcast volume. 🎵
