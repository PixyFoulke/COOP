
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn


i2c = busio.I2C(board.SCL, board.SDA)

ads = ADS.ADS1115(i2c)


pr1 = AnalogIn(ads, 0)
pr2 = AnalogIn(ads, 1)


def get_light_values():
    return pr1.value, pr2.value


def get_light_voltages():
    return pr1.voltage, pr2.voltage


def is_night(threshold=1.0):
    avg_voltage = (pr1.voltage + pr2.voltage) / 2
    return avg_voltage < threshold


def get_light_state():
    return "NIGHT" if is_night() else "DAY"
