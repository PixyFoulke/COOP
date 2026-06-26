# - Jax/Rune Stitt
#DHT11 (GPIO 4)
#ADS7830 (SDA GPIO 2) (SCL GPIO 3)
#128x64 OLED Display (SDA GPIO 2) (SCL GPIO 3)
#2x Photoresistor (5539) (ADS7830 A0 thru 10k ohm) (ADS7830 A1 thru 10k ohm)

# main.py - Jax Stitt

import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "sensors"))

import analog
import dht11
import display

print("Starting sensor readout... (Ctrl+C to stop)")
display.show_centered("Starting...")
time.sleep(1)

try:
    while True:
        # Read sensors
        a0 = analog.read_ads7830(analog.i2c, 0)
        a1 = analog.read_ads7830(analog.i2c, 1)
        time_of_day = analog.estimate_time_of_day(a0, a1)

        temp_f = getattr(dht11.getTemperature(unit=1), "__round__", lambda n: dht11.getTemperature(unit=1))
        temp_f = dht11.getTemperature(unit=1)
        humidity = dht11.getHumidity(unit=0)

        temp_str = f"{temp_f:.1f}F" if temp_f is not None else "Err"
        hum_str  = f"{humidity:.0f}%" if humidity is not None else "Err"

        print(f"A0: {a0:3d} | A1: {a1:3d} | {time_of_day} | Temp: {temp_str} | Humidity: {hum_str}")

        # Gate check
        if a0 < analog.LIGHT_THRESHOLD and a1 < analog.LIGHT_THRESHOLD:
            print(">>> closing gate <<<")
            display.show_centered("CLOSING GATE")
        else:
            display.show_kv({
                "Temp":     temp_str,
                "Humidity": hum_str,
                "Light A0": str(a0),
                "Light A1": str(a1),
                "Time":     time_of_day,
            })

        time.sleep(2)

except KeyboardInterrupt:
    print("\nStopped.")
    display.show_centered("Goodbye!")
    time.sleep(1)
    display.clear()
    dht11.cleanup()