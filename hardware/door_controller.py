# Jax
import time
import board
import digitalio

dooropen = digitalio.DigitalInOut(board.D27)
doorclose = digitalio.DigitalInOut(board.D17)

dooropen.direction = digitalio.Direction.INPUT
doorclose.direction = digitalio.Direction.INPUT

def dooropen():
    dooropen.pull = digitalio.Pull.DOWN
    time.sleep(0.1)
    dooropen.pull = digitalio.Pull.UP
    time.sleep(1)
    dooropen.pull = digitalio.Pull.DOWN
    time.sleep(0.1)
    dooropen.pull = digitalio.Pull.UP

def doorclose():
    doorclose.pull = digitalio.Pull.DOWN
    time.sleep(0.1)
    doorclose.pull = digitalio.Pull.UP
    time.sleep(1)
    doorclose.pull = digitalio.Pull.DOWN
    time.sleep(0.1)
    doorclose.pull = digitalio.Pull.UP

# TEST
dooropen()
time.sleep(2)
doorclose()
time.sleep(2)