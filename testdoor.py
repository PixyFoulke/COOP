
import time

from hardware.door import door_open, door_close


print("Starting door test")

print("Opening door...")
door_open()

time.sleep(5)

print("Closing door...")
door_close()

time.sleep(5)

print("Door test complete")
