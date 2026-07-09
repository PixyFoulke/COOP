
from hardware.door import door_open, door_close
import time


print("Testing OPEN")
door_open()

time.sleep(10)

print("Testing CLOSE")
door_close()

print("Finished")
