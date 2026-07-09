
import time
import board
import digitalio

OPEN_PIN = board.D5
CLOSE_PIN = board.D6

open_button = digitalio.DigitalInOut(OPEN_PIN)
close_button = digitalio.DigitalInOut(CLOSE_PIN)

open_button.direction = digitalio.Direction.INPUT
close_button.direction = digitalio.Direction.INPUT

door_is_open = False


def _press(pin):
    """
    Simulate a button press.
    """

    pin.pull = digitalio.Pull.DOWN
    time.sleep(0.2)

    pin.pull = digitalio.Pull.UP
    time.sleep(0.2)

    pin.pull = digitalio.Pull.DOWN


def open_door():
    global door_is_open

    _press(open_button)
    door_is_open = True

    print("Door opened.")


def close_door():
    global door_is_open

    _press(close_button)
    door_is_open = False

    print("Door closed.")


def toggle_door():
    if door_is_open:
        close_door()
    else:
        open_door()

    return door_is_open


def is_door_open():
    return door_is_open
