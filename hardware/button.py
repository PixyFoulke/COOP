
import board
import digitalio
import time
import os

button = digitalio.DigitalInOut(board.D17)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

DOUBLE_CLICK_TIME = 0.5
HOLD_TIME = 5.0

last_release = 0
click_count = 0


def button_pressed():
    return not button.value


def reboot_pi():
    os.system("sudo reboot")


def get_button_action():
    global last_release
    global click_count

    if button_pressed():

        start = time.time()

        while button_pressed():

            if time.time() - start >= HOLD_TIME:

                while button_pressed():
                    time.sleep(0.05)

                click_count = 0
                return "restart"

            time.sleep(0.05)

        # debounce
        time.sleep(0.05)

        click_count += 1
        last_release = time.time()

    if click_count > 0:
        if time.time() - last_release > DOUBLE_CLICK_TIME:

            if click_count == 1:
                action = "toggle"
            else:
                action = "alarm"

            click_count = 0
            return action

    return None
