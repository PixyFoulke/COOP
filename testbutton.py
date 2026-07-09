
import time
import board
import digitalio


button = digitalio.DigitalInOut(board.D17)

button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP


print("Waiting for button...")


while True:

    if not button.value:
        print("BUTTON PRESSED")

        while not button.value:
            time.sleep(0.05)

        print("BUTTON RELEASED")

    time.sleep(0.05)
