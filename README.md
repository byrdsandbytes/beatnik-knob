# Beatnik Knob - Snapcast Volume Controller

A hardware volume controller for Snapcast using a rotary encoder on Raspberry Pi. Control your Snapcast client volume with a physical rotary knob and button for mute/unmute functionality.

## Features

- 🎛️ **Physical Volume Control**: Rotate the encoder to adjust volume in real-time
- 🔇 **Mute Toggle**: Press the button to mute/unmute audio
- 🔄 **Real-time Sync**: Automatically syncs with server-side volume changes
- 🚀 **Auto-reconnect**: Handles network disconnections gracefully
- ⚡ **Throttled Updates**: Optimized for smooth operation without overwhelming the server

## Hardware Requirements

- Raspberry Pi (tested on Pi 3B+ and Pi 4)
- Rotary encoder with push button (KY-040 or similar)
- Jumper wires
- Breadboard (optional)

## Wiring Diagram

Connect the rotary encoder to your Raspberry Pi as follows:

| Rotary Encoder Pin | Raspberry Pi GPIO | Pin Number |
|-------------------|-------------------|------------|
| CLK               | GPIO 17           | Pin 11     |
| DT                | GPIO 18           | Pin 12     |
| SW (Button)       | GPIO 27           | Pin 13     |
| VCC               | 3.3V              | Pin 1      |
| GND               | Ground            | Pin 6      |

## Software Requirements

- Raspberry Pi OS (Debian Bookworm Lite)
- Python 3.11+
- Snapcast server running on your network
- GPIO access (requires running as root or adding user to gpio group)

## Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Idrimi/beatnik-knob.git
   cd beatnik-knob
   ```

2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   sudo ./setup.sh
   ```

3. **Configure your Snapcast server details**:
   ```bash
   nano rotary/snapcast-volume-rotary.py
   ```
   Update these variables:
   - `SNAPCAST_URI`: Your Snapcast server WebSocket URI
   - `SNAPCAST_CLIENT_ID`: Your Raspberry Pi's Snapcast client ID

4. **Run the controller**:
   ```bash
   cd rotary
   python3 snapcast-volume-rotary.py
   ```

## Configuration

### Finding Your Client ID

To find your Snapcast client ID, run:
```bash
curl -s http://your-snapcast-server:1780/jsonrpc -d '{"id":1,"jsonrpc":"2.0","method":"Server.GetStatus"}' | jq '.result.server.groups[].clients[].id'
```

Or check the Snapcast web interface at `http://your-snapcast-server:1780`.

### Customizable Settings

Edit `rotary/snapcast-volume-rotary.py` to customize:

- `VOLUME_STEP`: Volume change per encoder step (default: 5%)
- `THROTTLE_INTERVAL_S`: Minimum time between commands (default: 0.05s)
- GPIO pin assignments (CLK, DT, SW)

## Running as a Service

To run the volume controller automatically on boot:

1. **Create the service file**:
   ```bash
   sudo nano /etc/systemd/system/beatnik-knob.service
   ```

2. **Add the service configuration**:
   ```ini
   [Unit]
   Description=Beatnik Knob Snapcast Volume Controller
   After=network.target snapclient.service
   Wants=snapclient.service

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/beatnik-knob/rotary
   ExecStart=/usr/bin/python3 /home/pi/beatnik-knob/rotary/snapcast-volume-rotary.py
   Restart=always
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable and start the service**:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable beatnik-knob.service
   sudo systemctl start beatnik-knob.service
   ```

4. **Check service status**:
   ```bash
   sudo systemctl status beatnik-knob.service
   ```

## Troubleshooting

### Common Issues

**Permission Denied (GPIO)**:
```bash
sudo usermod -a -G gpio pi
# Logout and login again
```

**Cannot Connect to Snapcast Server**:
- Verify server IP/hostname in `SNAPCAST_URI`
- Check if port 1780 is accessible: `telnet your-server 1780`
- Ensure Snapcast server is running

**Module Import Errors**:
```bash
pip3 install --user gpiozero websockets
```

**Encoder Not Responding**:
- Check wiring connections
- Verify GPIO pin numbers match your configuration
- Test with `rotary/rotary-encoder-test.py`

### Debug Mode

For verbose output, modify the script to include debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Hardware

Use the included test script to verify your hardware setup:
```bash
cd rotary
python3 rotary-encoder-test.py
```

## Development

### Project Structure

```
beatnik-knob/
├── README.md
├── setup.sh
└── rotary/
    ├── snapcast-volume-rotary.py    # Main controller script
    └── rotary-encoder-test.py       # Hardware testing script
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test on actual hardware
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Snapcast](https://github.com/badaix/snapcast) - Multi-room audio player
- [gpiozero](https://gpiozero.readthedocs.io/) - Simple GPIO library for Raspberry Pi
- [websockets](https://websockets.readthedocs.io/) - WebSocket implementation for Python

---

**Note**: This project requires a running Snapcast server and client setup. For Snapcast installation instructions, visit the [official Snapcast documentation](https://github.com/badaix/snapcast).