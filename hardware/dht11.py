# - Jax/Rune Stitt
#DHT11 Sensor on GPIO 4
#DHT11 Documentation: https://shorturl.at/Jqfl2
import adafruit_dht
import board
import time


_sensor = adafruit_dht.DHT11(board.D4)

def _read():
    for _ in range(5):
        try:
            return _sensor.temperature, _sensor.humidity
        except RuntimeError:
            time.sleep(2)
    return None, None

def getTemperature(unit=0):
    #0 = Celsius, 1 = Fahrenheit
    temp_c, _ = _read()
    if temp_c is None:
        return None
    return temp_c if unit == 0 else temp_c * 9/5 + 32

def getHumidity(unit=0):
    #0 = Percent, 1 = Raw
    _, humidity = _read()
    if humidity is None:
        return None
    return humidity if unit == 0 else humidity / 100.0

def cleanup():
    _sensor.exit()