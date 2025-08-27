from gpiozero import RotaryEncoder, Button
import time

# --- Konfiguration ---
# Definiere die GPIO-Pins, an die der Encoder angeschlossen ist.
# Ändere diese Werte, falls du andere Pins verwendest.
PIN_CLK = 17
PIN_DT = 18
PIN_SW = 27

# --- Initialisierung ---
# Erstelle ein RotaryEncoder-Objekt.
# max_steps und min_steps begrenzen den Zähler, 0 bedeutet unbegrenzt.
encoder = RotaryEncoder(PIN_CLK, PIN_DT, max_steps=0)

# Erstelle ein Button-Objekt für den Taster.
button = Button(PIN_SW, pull_up=True) # pull_up=True, falls kein externer Pull-up-Widerstand verwendet wird.

# --- Funktionen (Callbacks) ---
# Diese Funktionen werden aufgerufen, wenn ein Ereignis eintritt.

def on_rotate_clockwise():
    """Wird aufgerufen, wenn im Uhrzeigersinn gedreht wird."""
    print("-> Rechts gedreht")
    print(f"   Position: {encoder.steps}")

def on_rotate_counter_clockwise():
    """Wird aufgerufen, wenn gegen den Uhrzeigersinn gedreht wird."""
    print("<- Links gedreht")
    print(f"   Position: {encoder.steps}")

def on_button_press():
    """Wird aufgerufen, wenn der Taster gedrückt wird."""
    print("\n--- Knopf gedrückt! ---")
    # Setzt den Zähler auf 0 zurück, wenn der Knopf gedrückt wird.
    encoder.steps = 0
    print(f"Position zurückgesetzt auf: {encoder.steps}\n")

# --- Zuweisung der Funktionen ---
# Verknüpfe die Funktionen mit den Ereignissen des Encoders und des Tasters.
encoder.when_rotated_clockwise = on_rotate_clockwise
encoder.when_rotated_counter_clockwise = on_rotate_counter_clockwise
button.when_pressed = on_button_press

# --- Hauptschleife ---
print("Rotary Encoder Test gestartet. Drücke STRG+C zum Beenden.")
print("Drehe den Knopf oder drücke ihn...")

try:
    # Das Skript läuft in einer Endlosschleife und wartet auf Ereignisse.
    # time.sleep() reduziert die CPU-Last.
    while True:
        time.sleep(0.1)

except KeyboardInterrupt:
    # Programm sauber beenden, wenn STRG+C gedrückt wird.
    print("\nProgramm wird beendet.")