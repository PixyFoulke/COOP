
# Runs actions.py based off of the results of yolo_detector.py and classifier.py

import os
import cv2
import time
from picamera2 import Picamera2

from ai.actions import trigger_alarm, safe_state, warning_state
from hardware.oled_display import update_status
from hardware.email_alert import send_email_alert
from hardware.sensors import getTemperature, getHumidity
from ai.yolo_detector import process_frame


# CAMERA SETUP
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()

print("COOP Safety System Running... Press 'q' to quit")


# EMAIL COOLDOWN
last_email_time = 0
EMAIL_COOLDOWN = 180


# MAIN LOOP
while True:
    frame = picam2.capture_array()

    # YOLO PROCESSING
    try:
        result, threats, unknowns = process_frame(frame)
        annotated_frame = result.plot()   # <-- Moved here
    except:
        continue

    # SENSOR DATA
    temp = getTemperature()
    humidity = getHumidity()

    # SAFE FALLBACKS + FAHRENHEIT CONVERSION
    if temp is None:
        temp_f = 0
    else:
        temp_f = (temp * 9/5) + 32

    if humidity is None:
        humidity = 0

    current_time = time.strftime("%H:%M:%S")

    # DECISION LOGIC
    if len(threats) > 0:
        trigger_alarm()

        update_status("THREAT", temp_f, humidity, current_time)

        if time.time() - last_email_time > EMAIL_COOLDOWN:
            cv2.imwrite("threat.jpg", annotated_frame)
            send_email_alert("threat.jpg")
            last_email_time = time.time()

    elif len(unknowns) > 0:
        warning_state()

        update_status("UNKNOWN", temp_f, humidity, current_time)

    else:
        safe_state()

        update_status("SAFE", temp_f, humidity, current_time)

    # DISPLAY
    cv2.imshow("COOP Safety System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.01)


# CLEAN EXIT
cv2.destroyAllWindows()
picam2.stop()
