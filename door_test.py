
import time
import board
import digitalio


door_open_pin = digitalio.DigitalInOut(board.D27)
door_close_pin = digitalio.DigitalInOut(board.D17)

door_open_pin.direction = digitalio.Direction.OUTPUT
door_close_pin.direction = digitalio.Direction.OUTPUT

# Unpressed state
door_open_pin.value = True
door_close_pin.value = True


def press_button(pin):
    # Simulate pressing the physical button
    pin.value = False
    time.sleep(1)

    # Release the button
    pin.value = True
    time.sleep(1)


def door_open():
    print("Opening door...")
    press_button(door_open_pin)


def door_close():
    print("Closing door...")
    press_button(door_close_pin)


try:
    print("Starting door test")

    time.sleep(2)

    door_open()

    time.sleep(5)

    door_close()

    print("Door test complete")

finally:
    door_open_pin.value = True
    door_close_pin.value = True

    door_open_pin.deinit()
    door_close_pin.deinit()
