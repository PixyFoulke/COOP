
import board
import digitalio
import time
import os


button = digitalio.DigitalInOut(board.D17)

button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def reboot_pi():
    os.system("sudo reboot")


last_press = False


def get_button_action():

    global last_press

    pressed = not button.value

    # New press detected
    if pressed and not last_press:

        print("Button pressed")

        last_press = True

        return "toggle"

    # Button released
    if not pressed:

        last_press = False

    return None
