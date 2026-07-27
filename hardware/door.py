
import time
import board
import digitalio


door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D22)

door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT

door_open_pin.value = False
door_close_pin.value = False


def door_open():

    print("OPEN signal")

    door_open_pin.value = True
    time.sleep(8)
    door_open_pin.value = False

    print("OPEN complete")


def door_close():

    print("CLOSE signal")

    door_close_pin.value = True
    time.sleep(8)
    door_close_pin.value = False

    print("CLOSE complete")
