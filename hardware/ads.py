import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the default I2C address
ads = ADS.ADS1115(i2c)

# FIXED: Use a period instead of a comma, and reference the correct pin names
pr1 = AnalogIn(ads, ADS.P0)
pr2 = AnalogIn(ads, ADS.P1)

# Cleaned up the header for two distinct sensors
print("PR1 (Raw / V)\t\tPR2 (Raw / V)")
print("-" * 38)

while True:
    # Print both sensors on the same line to keep the terminal easy to read
    print(f"{pr1.value:>5} / {pr1.voltage:.3f}V\t{pr2.value:>5} / {pr2.voltage:.3f}V")
    time.sleep(1.0)
