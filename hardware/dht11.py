# - Jax/Rune Stitt
# DHT11 standalone test script
# DHT11 Sensor on GPIO 4

import time
import adafruit_dht
import board

sensor = adafruit_dht.DHT11(board.D4)

print("Reading DHT11 (Ctrl+C to stop)...\n")

try:
    while True:
        try:
            temp_c = sensor.temperature
            temp_f = temp_c * 9 / 5 + 32
            humidity = sensor.humidity
            print(f"Temp: {temp_c:.1f}C / {temp_f:.1f}F  |  Humidity: {humidity:.1f}%")
        except RuntimeError as e:
            # DHT11 read failures are common/expected, just retry
            print(f"Read error: {e.args[0]}")

        time.sleep(2)

except KeyboardInterrupt:
    print("Stopped.")
    sensor.exit()