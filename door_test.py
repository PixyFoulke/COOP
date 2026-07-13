
# door_test.py

import time
from hardware.door_controller import door_open, door_close

print("Opening door...")
door_open()

time.sleep(5)  # Keep the door open for 5 seconds

print("Closing door...")
door_close()

print("Door test complete.")
