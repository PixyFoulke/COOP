
import time
import board
import digitalio


# Door controller connections
# OPEN wire -> GPIO 27
# CLOSE wire -> GPIO 22
# Door controller ground -> Raspberry Pi GND

OPEN_PIN = board.D27
CLOSE_PIN = board.D22


open_button = digitalio.DigitalInOut(OPEN_PIN)
close_button = digitalio.DigitalInOut(CLOSE_PIN)


# Start as outputs
open_button.direction = digitalio.Direction.OUTPUT
close_button.direction = digitalio.Direction.OUTPUT


# Idle state (not pressing buttons)
open_button.value = True
close_button.value = True


door_is_open = False


def press_button(pin):
    """
    Simulates pressing the coop door button.
    """

    pin.value = False      # press
    time.sleep(0.25)

    pin.value = True       # release
    time.sleep(0.25)


def open_door():
    global door_is_open

    print("Opening door...")

    press_button(open_button)

    door_is_open = True


def close_door():
    global door_is_open

    print("Closing door...")

    press_button(close_button)

    door_is_open = False


def toggle_door():
    global door_is_open

    if door_is_open:
        close_door()
    else:
        open_door()

    return door_is_open


def is_door_open():
    return door_is_open
