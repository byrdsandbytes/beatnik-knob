# Beatnik Knob - Beatnik & Snapcast Client Volume Controller

A hardware volume controller for Snapcast using a rotary encoder on Raspberry Pi.

## Hardware Wiring

Connect your rotary encoder to the Raspberry Pi:

| Rotary Encoder | Raspberry Pi GPIO | Pin |
|----------------|-------------------|-----|
| CLK            | GPIO 17           | 11  |
| DT             | GPIO 18           | 12  |
| SW (Button)    | GPIO 27           | 13  |
| VCC            | 3.3V              | 1   |
| GND            | Ground            | 6   |

## Installation Steps

### 1. System Setup
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip git curl jq nano
```

### 2. Install Python Dependencies
```bash
# Install Python packages
pip3 install --user gpiozero websockets

# Add user to gpio group
sudo usermod -a -G gpio $USER

# Logout and login again for group changes to take effect
```

### 3. Clone and Setup Project
```bash
# Clone the repository
git clone https://github.com/Idrimi/beatnik-knob.git
cd beatnik-knob

# Make scripts executable
chmod +x rotary/*.py
```

### 4. Configure Snapcast Connection
```bash
# Edit the main script
nano rotary/snapcast-volume-rotary.py
```

Update these variables:
- `SNAPCAST_URI = "ws://YOUR_SERVER_IP:1780/jsonrpc"`
- `SNAPCAST_CLIENT_ID = "YOUR_CLIENT_ID"`

Find your client ID:
```bash
curl -s http://YOUR_SERVER_IP:1780/jsonrpc \
  -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' | \
  jq '.result.server.groups[].clients[].id'
```

### 5. Test Hardware
```bash
# Test rotary encoder wiring
cd rotary
python3 rotary-encoder-test.py
```

### 6. Run Volume Controller
```bash
# Start the controller
python3 snapcast-volume-rotary.py
```

## Optional: Run as System Service

Create service file:
```bash
sudo nano /etc/systemd/system/beatnik-knob.service
```

Add this content:
```ini
[Unit]
Description=Beatnik Knob Volume Controller
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/beatnik-knob/rotary
ExecStart=/usr/bin/python3 snapcast-volume-rotary.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable beatnik-knob.service
sudo systemctl start beatnik-knob.service
```

## Troubleshooting

**Permission errors**: Make sure you logged out and back in after adding user to gpio group

**Import errors**: 
```bash
pip3 install --user --force-reinstall gpiozero websockets
```

**Connection errors**: Verify Snapcast server IP and that port 1780 is accessible
