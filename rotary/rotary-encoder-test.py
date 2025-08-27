#!/usr/bin/env python3
"""
Rotary Encoder Hardware Test Script
This script tests the rotary encoder hardware without connecting to Snapcast.
Use this to verify your wiring and GPIO configuration.
"""

from gpiozero import RotaryEncoder, Button
import time

# --- Configuration ---
# Define the GPIO pins where the encoder is connected.
# Change these values if you use different pins.
PIN_CLK = 17  # Rotary encoder CLK pin
PIN_DT = 18   # Rotary encoder DT pin
PIN_SW = 27   # Rotary encoder button pin

print("🧪 Rotary Encoder Hardware Test")
print("=" * 40)
print(f"CLK Pin: GPIO {PIN_CLK}")
print(f"DT Pin:  GPIO {PIN_DT}")
print(f"SW Pin:  GPIO {PIN_SW}")
print("=" * 40)
print("Instructions:")
print("- Rotate encoder clockwise and counter-clockwise")
print("- Press the encoder button to reset position")
print("- Press Ctrl+C to exit")
print("=" * 40)

try:
    # --- Initialization ---
    # Create a RotaryEncoder object.
    # max_steps and min_steps limit the counter, 0 means unlimited.
    encoder = RotaryEncoder(PIN_CLK, PIN_DT, max_steps=0)

    # Create a Button object for the switch.
    button = Button(PIN_SW, pull_up=True)  # pull_up=True if no external pull-up resistor is used.

    # --- Functions (Callbacks) ---
    # These functions are called when an event occurs.

    def on_rotate_clockwise():
        """Called when rotated clockwise."""
        print("🔄 Clockwise rotation")
        print(f"   Position: {encoder.steps}")

    def on_rotate_counter_clockwise():
        """Called when rotated counter-clockwise."""
        print("🔄 Counter-clockwise rotation")
        print(f"   Position: {encoder.steps}")

    def on_button_press():
        """Called when the button is pressed."""
        print("\n🔘 Button pressed! Position reset to 0")
        # Reset the counter to 0 when the button is pressed.
        encoder.steps = 0
        print(f"   New position: {encoder.steps}\n")

    # --- Function Assignment ---
    # Link the functions with the encoder and button events.
    encoder.when_rotated_clockwise = on_rotate_clockwise
    encoder.when_rotated_counter_clockwise = on_rotate_counter_clockwise
    button.when_pressed = on_button_press

    print("✅ Hardware initialized successfully!")
    print("Waiting for input... (Ctrl+C to exit)")
    print()

    # --- Main Loop ---
    # The script runs in an endless loop and waits for events.
    # time.sleep() reduces CPU load.
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    # Exit the program cleanly when Ctrl+C is pressed.
    print("\n👋 Test stopped by user")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nTroubleshooting tips:")
    print("1. Check wiring connections")
    print("2. Verify GPIO pin numbers match your setup")
    print("3. Ensure user is in 'gpio' group: sudo usermod -a -G gpio $USER")
    print("4. Try running with sudo (not recommended for production)")
    print("5. Reboot if you just changed group membership")
    
finally:
    print("🧹 Cleaning up GPIO...")
    try:
        encoder.close()
        button.close()
    except:
        pass
    print("✅ Cleanup complete")