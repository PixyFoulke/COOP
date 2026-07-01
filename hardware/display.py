# - Jax/Rune Stitt
#128x64 OLED Display (SDA GPIO 2) (SCL GPIO 3)

import board
import busio
import adafruit_ssd1306
from PIL import Image, ImageDraw, ImageFont

i2c = busio.I2C(board.SCL, board.SDA)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c)

def clear():
    oled.fill(0)
    oled.show()

def _base_draw():
    image = Image.new("1", (128, 64))
    draw = ImageDraw.Draw(image)
    return image, draw

def show_text(lines: list[str], font_size: int = 10):
    #Display a list of strings, one per line.
    image, draw = _base_draw()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    y = 0
    for line in lines:
        draw.text((0, y), line, font=font, fill=255)
        y += font_size + 2
        if y >= 64:
            break

    oled.image(image)
    oled.show()

def show_centered(text: str, font_size: int = 16):
    #Display a single string centered on screen.
    image, draw = _base_draw()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
    except:
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), text, font=font)
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (128 - w) // 2
    y = (64 - h) // 2
    draw.text((x, y), text, font=font, fill=255)

    oled.image(image)
    oled.show()

def show_kv(pairs: dict, font_size: int = 10):
    #Display key-value pairs, e.g. {'Temp': '72F', 'Light': '183'}
    lines = [f"{k}: {v}" for k, v in pairs.items()]
    show_text(lines, font_size)

def show_progress_bar(label: str, value: float, max_value: float = 255):
    #Display a label and a horizontal progress bar (value / max_value).
    image, draw = _base_draw()
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
    except:
        font = ImageFont.load_default()

    draw.text((0, 0), label, font=font, fill=255)
    bar_width = int((value / max_value) * 124)
    draw.rectangle([2, 40, 126, 58], outline=255, fill=0)
    draw.rectangle([2, 40, 2 + bar_width, 58], outline=255, fill=255)

    oled.image(image)
    oled.show()