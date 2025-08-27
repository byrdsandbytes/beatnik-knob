import asyncio
import json
import websockets
import time # Import the time module
from gpiozero import RotaryEncoder, Button

# --- Konfiguration ---
SNAPCAST_URI = "ws://beatnik-server.local:1780/jsonrpc"
SNAPCAST_CLIENT_ID = "2c:cf:67:d4:b1:95"
VOLUME_STEP = 5
THROTTLE_INTERVAL_S = 0.05 # --- NEW: Send updates at most every 50ms ---

# --- GPIO Konfiguration ---
PIN_CLK = 17
PIN_DT = 18
PIN_SW = 27

# --- Globale Variablen für den Zustand ---
current_volume = 0
is_muted = False
websocket = None
last_command_time = 0 # --- NEW: Timestamp for throttling ---

# --- Initialisierung der GPIO-Komponenten ---
encoder = RotaryEncoder(PIN_CLK, PIN_DT, max_steps=0, wrap=False)
button = Button(PIN_SW, pull_up=True)

# --- Asynchrone Funktionen ---

async def send_rpc_request(method, params={}, request_id=None):
    """Prepares and sends a JSON-RPC request over the active WebSocket."""
    if websocket:
        if request_id is None:
            request_id = int(time.time())
        request = {"id": request_id, "jsonrpc": "2.0", "method": method, "params": params}
        await websocket.send(json.dumps(request))

def handle_notification(data):
    """Parses notifications from the server and updates the authoritative state."""
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
            print(f"🔇 Synced mute from server: {'STUMM' if is_muted else 'AN'}")

def handle_initial_state(data):
    """Parses the full server status to set the initial state."""
    global current_volume, is_muted
    try:
        clients = data["result"]["server"]["groups"][0]["clients"]
        client_state = next((c for c in clients if c["id"] == SNAPCAST_CLIENT_ID), None)
        if client_state:
            current_volume = client_state["config"]["volume"]["percent"]
            is_muted = client_state["config"]["volume"]["muted"]
            print(f"✅ Initial state synced: Volume is {current_volume}%, Mute is {'STUMM' if is_muted else 'AN'}")
        else:
            print(f"⚠️ Client ID {SNAPCAST_CLIENT_ID} not found on server.")
    except (KeyError, TypeError, StopIteration):
        print("⛔️ Error: Could not parse the server state structure.")

# --- GPIO Callback-Funktionen ---

def on_rotate_clockwise():
    """Increase volume, with throttling."""
    global current_volume, last_command_time
    now = time.monotonic()
    # --- CHANGE: Check if enough time has passed ---
    if (now - last_command_time) > THROTTLE_INTERVAL_S:
        current_volume = min(100, current_volume + VOLUME_STEP)
        print(f"-> Knob set to: {current_volume}%")
        volume_payload = {"percent": current_volume, "muted": is_muted}
        asyncio.run_coroutine_threadsafe(
            send_rpc_request("Client.SetVolume", {"id": SNAPCAST_CLIENT_ID, "volume": volume_payload}),
            main_loop
        )
        last_command_time = now # Update the timestamp

def on_rotate_counter_clockwise():
    """Decrease volume, with throttling."""
    global current_volume, last_command_time
    now = time.monotonic()
    # --- CHANGE: Check if enough time has passed ---
    if (now - last_command_time) > THROTTLE_INTERVAL_S:
        current_volume = max(0, current_volume - VOLUME_STEP)
        print(f"<- Knob set to: {current_volume}%")
        volume_payload = {"percent": current_volume, "muted": is_muted}
        asyncio.run_coroutine_threadsafe(
            send_rpc_request("Client.SetVolume", {"id": SNAPCAST_CLIENT_ID, "volume": volume_payload}),
            main_loop
        )
        last_command_time = now # Update the timestamp

def on_button_press():
    """Request to toggle mute."""
    new_mute_status = not is_muted
    print(f"--- Requesting mute: {'STUMM' if new_mute_status else 'AN'} ---")
    asyncio.run_coroutine_threadsafe(
        send_rpc_request("Client.SetMute", {"id": SNAPCAST_CLIENT_ID, "mute": new_mute_status}),
        main_loop
    )

# --- Hauptlogik ---
async def main():
    """The main asynchronous function that manages the connection and tasks."""
    global websocket
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
    
    main_loop = asyncio.get_event_loop()
    try:
        main_loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\nProgrammed stopped by user.")