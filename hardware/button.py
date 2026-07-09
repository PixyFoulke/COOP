
import RPi.GPIO as GPIO
import time
import os

BUTTON_PIN = 17

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

DOUBLE_CLICK_TIME = 0.5
HOLD_TIME = 5.0

last_release = 0
click_count = 0


def button_pressed():
    return GPIO.input(BUTTON_PIN) == GPIO.LOW


def reboot_pi():
    os.system("sudo reboot")


def get_button_action():
    """
    Returns:
        'toggle'  -> single click
        'alarm'   -> double click
        'restart' -> held for 5 seconds
        None      -> nothing happened
    """

    global last_release
    global click_count

    # button just pressed
    if button_pressed():

        start = time.time()

        while button_pressed():
            duration = time.time() - start

            if duration >= HOLD_TIME:
                while button_pressed():
                    time.sleep(0.05)

                return "restart"

            time.sleep(0.05)

        # debounce
        time.sleep(0.05)

        click_count += 1
        last_release = time.time()

    # determine single vs double click
    if click_count > 0:
        if time.time() - last_release > DOUBLE_CLICK_TIME:

            if click_count == 1:
                action = "toggle"
            else:
                action = "alarm"

            click_count = 0
            return action

    return None
