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

## Installation

You can install the necessary packages and set up permissions by running the installation script.

```bash
# Make the script executable
chmod +x install.sh

# Run the installation script
sudo ./install.sh
```

After the script completes, you will need to **reboot your Raspberry Pi** for the permission changes to take effect.

For manual installation steps, please see the `INSTALL.md` file.

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
sudo apt install --reinstall python3-gpiozero python3-websockets
```

**Connection errors**: Verify Snapcast server IP and that port 1780 is accessible

**Service logging and debugging**:
```bash
# Check service status
sudo systemctl status beatnik-knob.service

# View recent logs
journalctl -u beatnik-knob.service -n 50

# Follow logs in real-time
journalctl -u beatnik-knob.service -f

# View logs from today
journalctl -u beatnik-knob.service --since today

# View logs with timestamps
journalctl -u beatnik-knob.service -o short-iso

# Restart service and watch logs
sudo systemctl restart beatnik-knob.service && journalctl -u beatnik-knob.service -f
```
