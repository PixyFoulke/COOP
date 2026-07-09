
import time
import board
import digitalio


door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D22)


door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT


door_open_pin.value = False
door_close_pin.value = False


door_state = "closed"

# Prevent rapid button presses
last_door_command = 0
DOOR_COOLDOWN = 5


def door_open():

    print("OPEN signal")

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False
    time.sleep(1)

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False
    time.sleep(1)

    print("OPEN complete")


def door_close():

    print("CLOSE signal")

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False
    time.sleep(1)

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False
    time.sleep(1)

    print("CLOSE complete")


def toggle_door():

    global door_state
    global last_door_command

    if door_state == "closed":

        door_open()

        print("Waiting for door movement to finish...")
        time.sleep(15)

        door_state = "open"

    else:

        door_close()

        print("Waiting for door movement to finish...")
        time.sleep(15)

        door_state = "closed"


def is_door_open():

    return door_state == "open"
