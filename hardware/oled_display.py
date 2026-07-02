
# controls display based on input from sensors and YOLO

import time
import math
from PIL import Image, ImageDraw

import sensors
from sensors import _oled, getTemperature, getHumidity

ATM_PRESSURE_KPA = 101.325

# COOP STATUS (updated from YOLO)
COOP_STATUS = "SAFE"


def update_status(status: str):
    global COOP_STATUS
    COOP_STATUS = status


def _relative_to_absolute_humidity(temp_c, rh_percent, pressure_kpa=ATM_PRESSURE_KPA):
    if temp_c is None or rh_percent is None:
        return None
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    e = (rh_percent / 100.0) * es
    return 621.97 * e / (pressure_kpa - e)


def _render_dashboard():
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    # Read sensors
    temp_c = getTemperature(unit=0)
    temp_f = getTemperature(unit=1)
    hum = getHumidity(unit=0)

    # Convert
    temp_f_str = f"{temp_f:.1f}F" if temp_f else "N/A"
    hum_str = f"{hum:.0f}%" if hum else "N/A"

    # COOP status formatting
    if COOP_STATUS == "THREAT":
        coop = "THREAT!"
    elif COOP_STATUS == "UNKNOWN":
        coop = "CHECK"
    else:
        coop = "SAFE"

    # Draw text
    draw.text((0, 0), f"T:{temp_f_str}  H:{hum_str}", fill=255)
    draw.text((0, 16), f"COOP: {coop}", fill=255)

    draw.text((0, 32), "SYSTEM ACTIVE", fill=255)

    # Push to OLED
    _oled.image(image)
    _oled.show()


def run():
    print("OLED dashboard running...")
    try:
        while True:
            _render_dashboard()
            time.sleep(1)  # refresh rate
    except KeyboardInterrupt:
        print("Stopped.")
        sensors.clearDisplay()
        sensors.cleanupDHT()


if __name__ == "__main__":
    run()
