
import time
import board
import digitalio


# Door controller inputs
OPEN_PIN = board.D27
CLOSE_PIN = board.D22


open_signal = digitalio.DigitalInOut(OPEN_PIN)
close_signal = digitalio.DigitalInOut(CLOSE_PIN)


open_signal.direction = digitalio.Direction.INPUT
close_signal.direction = digitalio.Direction.INPUT


def open_door():

    print("Sending OPEN signal")

    open_signal.pull = digitalio.Pull.DOWN
    time.sleep(0.1)

    open_signal.pull = digitalio.Pull.UP
    time.sleep(1)

    open_signal.pull = digitalio.Pull.DOWN
    time.sleep(0.1)

    open_signal.pull = digitalio.Pull.UP

    print("OPEN signal complete")


def close_door():

    print("Sending CLOSE signal")

    close_signal.pull = digitalio.Pull.DOWN
    time.sleep(0.1)

    close_signal.pull = digitalio.Pull.UP
    time.sleep(1)

    close_signal.pull = digitalio.Pull.DOWN
    time.sleep(0.1)

    close_signal.pull = digitalio.Pull.UP

    print("CLOSE signal complete")


def toggle_door():

    open_door()


def is_door_open():

    return False
