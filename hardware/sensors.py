
# simplified sensor code

import adafruit_dht
import board

sensor = adafruit_dht.DHT11(board.D4)


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
