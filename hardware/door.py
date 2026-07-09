
import time
import board
import digitalio


door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D22)

door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT


door_open_pin.value = False
door_close_pin.value = False


def press_button(pin):
    pin.value = True
    time.sleep(0.1)
    pin.value = False


def open_door():
    print("Opening door")
    press_button(door_open_pin)


def close_door():
    print("Closing door")
    press_button(door_close_pin)
