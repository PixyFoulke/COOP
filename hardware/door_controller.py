import time
import board
import digitalio

door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D17)

door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT

def door_open():
    door_open_pin.value = True
    time.sleep(1)
    door_open_pin.value = False
    time.sleep(1)
    door_open_pin.value = True
    time.sleep(1)
    door_open_pin.value = False
    time.sleep(1)

def door_close():
    door_close_pin.value = True
    time.sleep(1)
    door_close_pin.value = False
    time.sleep(1)
    door_close_pin.value = True
    time.sleep(1)
    door_close_pin.value = False
    time.sleep(1)

# TEST
door_open()
time.sleep(2)