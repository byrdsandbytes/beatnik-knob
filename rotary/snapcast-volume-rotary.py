import asyncio
import json
import websockets
import time
from gpiozero import RotaryEncoder, Button

# --- Configuration ---
SNAPCAST_URI = "ws://beatnik-server.local:1780/jsonrpc"
SNAPCAST_CLIENT_ID = "2c:cf:67:d4:b1:95"
VOLUME_STEP = 5
DEBOUNCE_DELAY_S = 0.2  # Send update 200ms after the last rotation

# --- GPIO Configuration ---
PIN_CLK = 17
PIN_DT = 18
PIN_SW = 27

# --- Global State ---
current_volume = 0
is_muted = False
websocket = None
debouncer = None  # Debouncer instance will be created in main

# --- GPIO Components ---
encoder = RotaryEncoder(PIN_CLK, PIN_DT, max_steps=0, wrap=False)
button = Button(PIN_SW, pull_up=True)

# --- Optimized Debouncer Class ---
class Debouncer:
    """A robust debouncer that sends the final volume after a pause in rotation."""
    def __init__(self, loop, delay, callback):
        self._loop = loop
        self._delay = delay
        self._callback = callback
        self._task = None

    def trigger(self):
        """Triggers the debouncer. Resets the timer if already running."""
        if self._task:
            self._task.cancel()
        self._task = self._loop.create_task(self._fire())

    async def _fire(self):
        """Waits for the delay and then executes the callback."""
        try:
            await asyncio.sleep(self._delay)
            await self._callback()
        except asyncio.CancelledError:
            pass  # Ignore cancellation, as it's part of the debounce logic

# --- Asynchronous Functions ---

async def send_rpc_request(method, params={}, request_id=None):
    """Prepares and sends a JSON-RPC request."""
    if not websocket or not websocket.open:
        print("⚠️ WebSocket is not connected. Cannot send request.")
        return
    if request_id is None:
        request_id = int(time.time())
    request = {"id": request_id, "jsonrpc": "2.0", "method": method, "params": params}
    await websocket.send(json.dumps(request))

async def send_volume_update():
    """Sends the current volume to the server."""
    print(f"⚡️ Sending final volume: {current_volume}%")
    volume_payload = {"percent": current_volume, "muted": is_muted}
    await send_rpc_request("Client.SetVolume", {"id": SNAPCAST_CLIENT_ID, "volume": volume_payload})

def handle_notification(data):
    """Parses notifications from the server and updates the state."""
    global current_volume, is_muted
    method, params = data.get("method"), data.get("params", {})
    if params.get("id") != SNAPCAST_CLIENT_ID: return

    if method == "Client.OnVolumeChanged":
        new_volume = params.get("volume", {}).get("percent")
        if new_volume is not None and current_volume != new_volume:
            current_volume = new_volume
            print(f"🔊 Synced volume from server: {current_volume}%")
    elif method == "Client.OnMute":
        new_mute_status = params.get("mute")
        if new_mute_status is not None and is_muted != new_mute_status:
            is_muted = new_mute_status
            print(f"🔇 Synced mute from server: {'Muted' if is_muted else 'Unmuted'}")

def handle_initial_state(data):
    """Parses the server status to set the initial state."""
    global current_volume, is_muted
    try:
        clients = data["result"]["server"]["groups"][0]["clients"]
        client_state = next((c for c in clients if c["id"] == SNAPCAST_CLIENT_ID), None)
        if client_state:
            current_volume = client_state["config"]["volume"]["percent"]
            is_muted = client_state["config"]["volume"]["muted"]
            print(f"✅ Initial state synced: Volume is {current_volume}%, Mute is {'Muted' if is_muted else 'Unmuted'}")
        else:
            print(f"⚠️ Client ID {SNAPCAST_CLIENT_ID} not found on server.")
    except (KeyError, TypeError, StopIteration):
        print("⛔️ Error: Could not parse the server state structure.")

# --- GPIO Callback Functions ---

def on_rotate_clockwise():
    """Increase volume locally and trigger the debouncer."""
    global current_volume
    current_volume = min(100, current_volume + VOLUME_STEP)
    print(f"-> Volume set to: {current_volume}%")
    if debouncer:
        debouncer.trigger()

def on_rotate_counter_clockwise():
    """Decrease volume locally and trigger the debouncer."""
    global current_volume
    current_volume = max(0, current_volume - VOLUME_STEP)
    print(f"<- Volume set to: {current_volume}%")
    if debouncer:
        debouncer.trigger()

def on_button_press():
    """Request to toggle mute (not debounced)."""
    new_mute_status = not is_muted
    print(f"--- Requesting mute: {'Mute' if new_mute_status else 'Unmute'} ---")
    # Use asyncio.create_task if loop is running, otherwise run_coroutine_threadsafe
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_rpc_request("Client.SetMute", {"id": SNAPCAST_CLIENT_ID, "mute": new_mute_status}))
    except RuntimeError:
        # Fallback if called when the loop is not running (less likely with this structure)
        asyncio.run(send_rpc_request("Client.SetMute", {"id": SNAPCAST_CLIENT_ID, "mute": new_mute_status}))

# --- Main Logic ---
async def main():
    """The main asynchronous function that manages the connection and tasks."""
    global websocket, debouncer
    
    loop = asyncio.get_running_loop()
    debouncer = Debouncer(loop, DEBOUNCE_DELAY_S, send_volume_update)

    while True:
        print(f"🔌 Trying to connect to {SNAPCAST_URI}...")
        try:
            async with websockets.connect(SNAPCAST_URI) as ws:
                websocket = ws
                print("✅ WebSocket connection established!")
                await send_rpc_request("Server.GetStatus", request_id=1)
                
                async for message in websocket:
                    data = json.loads(message)
                    if "method" in data:
                        handle_notification(data)
                    elif "result" in data and data.get("id") == 1:
                        handle_initial_state(data)
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            print(f"⛔️ Connection lost: {e}. Reconnecting in 5 seconds...")
            websocket = None
            await asyncio.sleep(5)

if __name__ == "__main__":
    print("Snapcast WebSocket Controller starting...")
    encoder.when_rotated_clockwise = on_rotate_clockwise
    encoder.when_rotated_counter_clockwise = on_rotate_counter_clockwise
    button.when_pressed = on_button_press
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")