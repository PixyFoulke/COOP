
import time
import board
import digitalio


# GPIO PINS
door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D17)


door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT


# IDLE STATE
door_open_pin.value = False
door_close_pin.value = False


# TRACK STATE
door_state = "closed"


# PREVENT RAPID COMMANDS
last_door_command = 0
DOOR_COOLDOWN = 5


def door_open():

    print("OPEN signal")

    door_open_pin.value = True

    time.sleep(4)

    door_open_pin.value = False

    print("OPEN complete")


def door_close():

    print("CLOSE signal")

    door_close_pin.value = True

    time.sleep(4)

    door_close_pin.value = False

    print("CLOSE complete")


def toggle_door():

    if door_state == "closed":

        door_open()

    else:

        door_close()


def is_door_open():

    return door_state == "open"
