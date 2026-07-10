
import board
import digitalio
import time
import os


button = digitalio.DigitalInOut(board.D5)

button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


def reboot_pi():

    os.system("sudo reboot")


def get_button_action():

    # button pressed
    if not button.value:

        print("Button detected")

        # debounce
        time.sleep(0.05)

        start_time = time.time()

        # wait while button is held
        while not button.value:

            held_time = time.time() - start_time

            # held for 5 seconds
            if held_time >= 5:
                print("Button held for 5 seconds")

                # wait until release so it only triggers once
                while not button.value:
                    time.sleep(0.05)

                return "restart"

            time.sleep(0.05)

        print("Button released")

        return "toggle"

    return None
