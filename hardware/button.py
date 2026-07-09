
import board
import digitalio
import time
import os


button = digitalio.DigitalInOut(board.D17)

button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def reboot_pi():

    os.system("sudo reboot")


def get_button_action():

    # wait for button press
    if not button.value:

        print("Button detected")

        # debounce
        time.sleep(0.1)

        # wait until button is released
        while not button.value:
            time.sleep(0.05)

        print("Button released")

        return "toggle"

    return None
