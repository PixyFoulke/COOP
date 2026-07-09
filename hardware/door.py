
import time
import board
import digitalio


# Door controller pins
# OPEN = GPIO 27
# CLOSE = GPIO 22

door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D22)


door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT


# Default state
door_open_pin.value = False
door_close_pin.value = False


door_state = False


def open_door():

    global door_state

    print("Opening door...")

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False
    time.sleep(1)

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False
    time.sleep(1)

    door_state = True

    print("Door opened.")


def close_door():

    global door_state

    print("Closing door...")

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False
    time.sleep(1)

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False
    time.sleep(1)

    door_state = False

    print("Door closed.")


def toggle_door():

    global door_state

    if door_state:
        close_door()
    else:
        open_door()

    return door_state


def is_door_open():

    return door_state
