
import time
import board
import digitalio


# GPIO PINS
door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D22)


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

    global last_door_command
    global door_state

    # cooldown protection
    if time.time() - last_door_command < DOOR_COOLDOWN:

        print("Door command ignored (cooldown)")
        return

    last_door_command = time.time()

    print("OPEN signal")

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False
    time.sleep(1)

    door_open_pin.value = True
    time.sleep(1)

    door_open_pin.value = False

    print("OPEN complete")

    door_state = "open"


def door_close():

    global last_door_command
    global door_state

    # cooldown protection
    if time.time() - last_door_command < DOOR_COOLDOWN:

        print("Door command ignored (cooldown)")
        return

    last_door_command = time.time()

    print("CLOSE signal")

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False
    time.sleep(1)

    door_close_pin.value = True
    time.sleep(1)

    door_close_pin.value = False

    print("CLOSE complete")

    door_state = "closed"


def toggle_door():

    if door_state == "closed":

        door_open()

    else:

        door_close()


def is_door_open():

    return door_state == "open"
