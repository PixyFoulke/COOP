# - Jax/Rune Stitt
# #ADS7830 (SDA GPIO 2) (SCL GPIO 3)
# ADS7830 Documentation: https://shorturl.at/n1RN0
#2x Photoresistor (5539) (ADS7830 A0 thru 10k ohm) (ADS7830 A1 thru 10k ohm)

import board
import busio
import time

# ADS7830 I2C address (default 0x48, A0/A1/A2 pins all GND)
ADS7830_ADDR = 0x48

# Command byte: single-ended mode, channel select
# Bits [7:4] = 1000 for single-ended, channel in bits [6:4]
# Channel mapping for single-ended: 0x84=CH0, 0xC4=CH1
CHANNEL_CMD = {
    0: 0x84,  # A0 — single-ended CH0
    1: 0xC4,  # A1 — single-ended CH1
}

LIGHT_THRESHOLD = 30   # 0–255; tune this to your lighting conditions

def read_ads7830(i2c, channel: int) -> int:
    cmd = CHANNEL_CMD[channel]
    # Write the command byte, then read 1 byte result
    i2c.writeto(ADS7830_ADDR, bytes([cmd]))
    result = bytearray(1)
    i2c.readfrom_into(ADS7830_ADDR, result)
    return result[0]

def estimate_time_of_day(a0: int, a1: int) -> str:
    avg = (a0 + a1) / 2
    if avg > 200:
        return "Midday (bright)"
    elif avg > 120:
        return "Morning / Afternoon"
    elif avg > 60:
        return "Dawn / Dusk"
    else:
        return "Night / Very dark"

i2c = busio.I2C(board.SCL, board.SDA)  # SCL=GPIO3, SDA=GPIO2

print("Reading light sensors (Ctrl+C to stop)...\n")

try:
    while True:
        a0 = read_ads7830(i2c, 0)
        a1 = read_ads7830(i2c, 1)

        print(f"A0: {a0:3d}  |  A1: {a1:3d}  |  {estimate_time_of_day(a0, a1)}")

        if a0 < LIGHT_THRESHOLD and a1 < LIGHT_THRESHOLD:
            print(">>> closing gate <<<")

        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped.")