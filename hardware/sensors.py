# - Jax/Rune Stitt
# Combined sensor + display module for Smart Street Lamp
#
# Hardware:
#   128x64 OLED (SSD1306)     - I2C (SDA GPIO 2, SCL GPIO 3)
#   ADS7830 ADC + 2x Photoresistor - I2C (SDA GPIO 2, SCL GPIO 3)
#   DHT11 Temp/Humidity Sensor - GPIO 4
#
# ADS7830 Documentation: https://shorturl.at/n1RN0
# DHT11 Documentation:   https://shorturl.at/Jqfl2

import time
import board
import busio
import adafruit_dht
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

# ----------------------------------------------------------------------
# Shared I2C bus (OLED + ADS7830 both live on it)
# ----------------------------------------------------------------------
_i2c = busio.I2C(board.SCL, board.SDA)

# ----------------------------------------------------------------------
# OLED Display (SSD1306)
# ----------------------------------------------------------------------
_oled = adafruit_ssd1306.SSD1306_I2C(128, 64, _i2c)
_FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _load_font(size: int):
    try:
        return ImageFont.truetype(_FONT_PATH, size)
    except Exception:
        return ImageFont.load_default()


def _base_draw():
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    return image, draw


def clearDisplay():
    _oled.fill(0)
    _oled.show()


def showText(lines: list[str], font_size: int = 10):
    """Display a list of strings, one per line."""
    image, draw = _base_draw()
    font = _load_font(font_size)

    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=255)
        y += font_size + 2
        if y >= 64:
            break

    _oled.image(image)
    _oled.show()


def showCentered(text: str, font_size: int = 16):
    """Display a single string centered on screen."""
    image, draw = _base_draw()
    font = _load_font(font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (128 - w) // 2
    y = (64 - h) // 2
    draw.text((x, y), text, font=font, fill=255)

    _oled.image(image)
    _oled.show()


def showKV(pairs: dict, font_size: int = 10):
    """Display key-value pairs, e.g. {'Temp': '72F', 'Light': '183'}"""
    lines = [f"{k}: {v}" for k, v in pairs.items()]
    showText(lines, font_size)


def showProgressBar(label: str, value: float, max_value: float = 255):
    """Display a label and a horizontal progress bar (value / max_value)."""
    image, draw = _base_draw()
    font = _load_font(12)

    draw.text((0, 0), label, font=font, fill=255)
    bar_width = int((value / max_value) * 124)
    draw.rectangle([2, 40, 126, 58], outline=255, fill=0)
    draw.rectangle([2, 40, 2 + bar_width, 58], outline=255, fill=255)

    _oled.image(image)
    _oled.show()


# ----------------------------------------------------------------------
# ADS7830 ADC + Photoresistors
# ----------------------------------------------------------------------
ADS7830_ADDR = 0x48

# Command byte: single-ended mode, channel select
# Bits [7:4] = 1000 for single-ended, channel in bits [6:4]
# Channel mapping for single-ended: 0x84=CH0, 0xC4=CH1
_CHANNEL_CMD = {
    0: 0x84,  # A0 - single-ended CH0
    1: 0xC4,  # A1 - single-ended CH1
}

LIGHT_THRESHOLD = 30  # 0-255; tune this to your lighting conditions


def _read_ads7830(channel: int) -> int:
    cmd = _CHANNEL_CMD[channel]
    _i2c.writeto(ADS7830_ADDR, bytes([cmd]))
    result = bytearray(1)
    _i2c.readfrom_into(ADS7830_ADDR, result)
    return result[0]


def getLightA0() -> int:
    """Raw 0-255 reading from photoresistor on ADS7830 channel A0."""
    return _read_ads7830(0)


def getLightA1() -> int:
    """Raw 0-255 reading from photoresistor on ADS7830 channel A1."""
    return _read_ads7830(1)


def getLightLevels() -> tuple[int, int]:
    """Both photoresistor readings as (a0, a1)."""
    return getLightA0(), getLightA1()


def getTimeOfDayEstimate() -> str:
    """Rough estimate of time of day based on averaged light levels."""
    a0, a1 = getLightLevels()
    avg = (a0 + a1) / 2
    if avg > 200:
        return "Midday (bright)"
    elif avg > 120:
        return "Morning / Afternoon"
    elif avg > 60:
        return "Dawn / Dusk"
    else:
        return "Night / Very dark"


def isDark() -> bool:
    """True if both photoresistors read below LIGHT_THRESHOLD."""
    a0, a1 = getLightLevels()
    return a0 < LIGHT_THRESHOLD and a1 < LIGHT_THRESHOLD


# ----------------------------------------------------------------------
# DHT11 Temp/Humidity
# ----------------------------------------------------------------------
_dht_sensor = adafruit_dht.DHT11(board.D4)


def _read_dht():
    for _ in range(5):
        try:
            return _dht_sensor.temperature, _dht_sensor.humidity
        except RuntimeError:
            time.sleep(2)
    return None, None


def getTemperature(unit: int = 0):
    """0 = Celsius, 1 = Fahrenheit"""
    temp_c, _ = _read_dht()
    if temp_c is None:
        return None
    return temp_c if unit == 0 else temp_c * 9 / 5 + 32


def getHumidity(unit: int = 0):
    """0 = Percent, 1 = Raw (0.0-1.0)"""
    _, humidity = _read_dht()
    if humidity is None:
        return None
    return humidity if unit == 0 else humidity / 100.0


def cleanupDHT():
    _dht_sensor.exit()


# ----------------------------------------------------------------------
# Convenience: grab everything at once
# ----------------------------------------------------------------------
def getAllReadings(temp_unit: int = 0, humidity_unit: int = 0) -> dict:
    """Single call to get every sensor value as a dict."""
    a0, a1 = getLightLevels()
    return {
        "temperature": getTemperature(temp_unit),
        "humidity": getHumidity(humidity_unit),
        "light_a0": a0,
        "light_a1": a1,
        "time_of_day": getTimeOfDayEstimate(),
        "is_dark": a0 < LIGHT_THRESHOLD and a1 < LIGHT_THRESHOLD,
    }


# ----------------------------------------------------------------------
# Standalone test run
# ----------------------------------------------------------------------
if __name__ == "__main__":
    print("Reading all sensors (Ctrl+C to stop)...\n")
    try:
        while True:
            data = getAllReadings(temp_unit=1)  # Fahrenheit
            print(
                f"Temp: {data['temperature']}F  |  Humidity: {data['humidity']}%  |  "
                f"Light A0: {data['light_a0']}  A1: {data['light_a1']}  |  "
                f"{data['time_of_day']}"
            )
            if data["is_dark"]:
                print(">>> closing gate <<<")

            showKV({
                "T": f"{data['temperature']}F" if data['temperature'] is not None else "N/A",
                "H": f"{data['humidity']}%" if data['humidity'] is not None else "N/A",
                "L0": data["light_a0"],
                "L1": data["light_a1"],
            })

            time.sleep(2)
    except KeyboardInterrupt:
        print("Stopped.")
        clearDisplay()
        cleanupDHT()