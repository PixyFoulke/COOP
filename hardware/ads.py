
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create ADC object
ads = ADS.ADS1115(i2c)

# Photoresistors
pr1 = AnalogIn(ads, ADS.P0)
pr2 = AnalogIn(ads, ADS.P1)


def get_light_values():
    return pr1.value, pr2.value


def get_light_voltages():
    return pr1.voltage, pr2.voltage


def is_night(threshold=1.0):
    """
    Returns True if the average light voltage is below the threshold.
    Adjust the threshold after testing.
    """
    avg_voltage = (pr1.voltage + pr2.voltage) / 2
    return avg_voltage < threshold


def get_light_state():
    return "NIGHT" if is_night() else "DAY"
