
# display.py - OLED slideshow for the Smart Street Lamp + COOP status
# Cycles: Temp F/Humidity % -> Temp C/Humidity g/kg -> Light -> Door -> COOP Status

import math
import time

from PIL import Image, ImageDraw

import sensors
from sensors import _oled, _load_font, getTemperature, getHumidity

SLIDE_DURATION = 2
ATM_PRESSURE_KPA = 101.325

# Placeholders
PLACEHOLDER_LIGHT_OHMS = 4700
PLACEHOLDER_TIME_ESTIMATE = "Evening (dusk)"
PLACEHOLDER_DOOR_STATUS = "Unknown"

# COOP STATUS
COOP_STATUS = "SAFE"


def update_status(status: str):
    global COOP_STATUS
    COOP_STATUS = status


# DISPLAY CORE
def _render_slide(title: str, big_text: str, sub_text: str = ""):
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    title_font = _load_font(10)
    big_font = _load_font(22)
    sub_font = _load_font(10)

    draw.text((0, 0), title.upper(), font=title_font, fill=255)
    draw.line([(0, 12), (128, 12)], fill=255)

    content_top = 14
    content_bottom = 52 if sub_text else 64

    bbox = draw.textbbox((0, 0), big_text, font=big_font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (128 - w) // 2
    y = content_top + ((content_bottom - content_top) - h) // 2
    draw.text((x, y), big_text, font=big_font, fill=255)

    if sub_text:
        bbox2 = draw.textbbox((0, 0), sub_text, font=sub_font)
        w2 = bbox2[2] - bbox2[0]
        x2 = (128 - w2) // 2
        draw.text((x2, 64 - 12), sub_text, font=sub_font, fill=255)

    _oled.image(image)
    _oled.show()


# SENSOR MATH
def _relative_to_absolute_humidity(temp_c, rh_percent, pressure_kpa=ATM_PRESSURE_KPA):
    if temp_c is None or rh_percent is None:
        return None
    es = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    e = (rh_percent / 100.0) * es
    return 621.97 * e / (pressure_kpa - e)


# SLIDES
def slide_temp_fahrenheit():
    temp_f = getTemperature(unit=1)
    rh = getHumidity(unit=0)

    temp_str = f"{temp_f:.1f}F" if temp_f is not None else "N/A"
    rh_str = f"{rh:.0f}% RH" if rh is not None else "N/A"
    _render_slide("Temp & Humidity", temp_str, rh_str)


def slide_temp_celsius():
    temp_c = getTemperature(unit=0)
    rh = getHumidity(unit=0)
    abs_h = _relative_to_absolute_humidity(temp_c, rh)

    temp_str = f"{temp_c:.1f}C" if temp_c is not None else "N/A"
    abs_str = f"{abs_h:.1f} g/kg" if abs_h is not None else "N/A"
    _render_slide("Temp & Humidity", temp_str, abs_str)


def slide_light():
    ohms_str = f"{PLACEHOLDER_LIGHT_OHMS} \u03a9"
    _render_slide("Light Level", ohms_str, PLACEHOLDER_TIME_ESTIMATE)


def slide_door():
    _render_slide("Door Status", PLACEHOLDER_DOOR_STATUS)


# COOP STATUS SLIDE
def slide_coop_status():
    if COOP_STATUS == "THREAT":
        text = "THREAT!"
        sub = "ALERT ACTIVE"
    elif COOP_STATUS == "UNKNOWN":
        text = "CHECK"
        sub = "MONITORING"
    else:
        text = "SAFE"
        sub = "NO THREATS"

    _render_slide("COOP STATUS", text, sub)


# SLIDE LIST
SLIDES = [
    slide_temp_fahrenheit,
    slide_temp_celsius,
    slide_light,
    slide_door,
    slide_coop_status,
]


# MAIN LOOP
def run(duration: float = SLIDE_DURATION):
    print("Starting OLED slideshow (Ctrl+C to stop)...")
    try:
        while True:
            for slide in SLIDES:
                slide()
                time.sleep(duration)
    except KeyboardInterrupt:
        print("Stopped.")
        sensors.clearDisplay()
        sensors.cleanupDHT()


if __name__ == "__main__":
    run()
