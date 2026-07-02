
# simplified sensor + OLED hardware setup

import adafruit_dht
import board

import adafruit_ssd1306
from board import I2C

# DHT11
sensor = adafruit_dht.DHT11(board.D4)

# OLED
i2c = I2C()
_oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

# Clear OLED on startup
_oled.fill(0)
_oled.show()


# SENSOR FUNCTIONS
def getTemperature():
    try:
        return sensor.temperature
    except:
        return None


def getHumidity():
    try:
        return sensor.humidity
    except:
        return None
