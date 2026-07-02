
# controls display based on input from sensors and AI detection

from PIL import Image, ImageDraw

from hardware.sensors import _oled  # ONLY hardware driver


def update_status(status: str, temp: float, humidity: float, current_time: str):
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)

    # Format safety text
    if status == "THREAT":
        coop = "THREAT!"
    elif status == "UNKNOWN":
        coop = "CHECK"
    else:
        coop = "SAFE"

    # Format sensor values
    temp_str = f"{temp:.1f}F" if temp is not None else "N/A"
    hum_str = f"{humidity:.0f}%" if humidity is not None else "N/A"

    # Draw OLED screen
    draw.text((0, 0), f"{coop}", fill=255)
    draw.text((0, 16), f"T:{temp_str} H:{hum_str}", fill=255)
    draw.text((0, 32), f"{current_time}", fill=255)

    # Push to OLED
    _oled.image(image)
    _oled.show()
