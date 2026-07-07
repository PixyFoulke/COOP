import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the default I2C address
ads = ADS.ADS1115(i2c)

# Create single-ended input on channel 0 (A0)
pr1 = AnalogIn(ads, ADS.P0)
pr2 = AnalogIn(ads, ADS,P1)
print("{:>5}\t{:>5}".format('Raw', 'v'))

while True:
    print("{:>5}\t{:>5.3f}".format(pr1.value, pr1.voltage))
    print("{:>5}\t{:>5.3f}".format(pr2.value, pr2.voltage))
    time.sleep(1.0)
