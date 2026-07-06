
# Runs actions.py based off of the results of yolo_detector.py and classifier.py

import os
import cv2
import time
import threading
from picamera2 import Picamera2

from ai.actions import trigger_alarm, safe_state, warning_state
from hardware.oled_display import update_status
from hardware.email_alert import send_email_alert
from hardware.sensors import getTemperature, getHumidity
from ai.yolo_detector import process_frame
from ai.chicken_counter import get_chicken_count


# CAMERA 1 (OUTSIDE)
picam2 = Picamera2(0)
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()


# SHARED DATA
last_email_time = 0
EMAIL_COOLDOWN = 180

chicken_count = 0
lock = threading.Lock()


# CHICKEN THREAD (CAMERA 2 INSIDE COOP)
def chicken_loop():
    global chicken_count

    while True:
        try:
            count, _ = get_chicken_count()

            with lock:
                chicken_count = count

        except:
            continue

        time.sleep(1)


# Start chicken thread
threading.Thread(target=chicken_loop, daemon=True).start()


print("COOP Safety System Running... Press 'q' to quit")


# MAIN LOOP (THREAT DETECTION CAMERA)
while True:
    frame = picam2.capture_array()

    try:
        result, threats, unknowns = process_frame(frame)
        annotated_frame = result.plot()
    except:
        continue

    temp = getTemperature()
    humidity = getHumidity()

    if temp is None:
        temp_f = 0
    else:
        temp_f = (temp * 9 / 5) + 32

    if humidity is None:
        humidity = 0

    current_time = time.strftime("%H:%M:%S")

    with lock:
        chickens = chicken_count

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

    elif chickens < 10:
        update_status(f"MISSING ({chickens})", temp_f, humidity, current_time)

    else:
        safe_state()
        update_status(f"SAFE ({chickens})", temp_f, humidity, current_time)

    cv2.imshow("COOP Safety System", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    time.sleep(0.01)

cv2.destroyAllWindows()
picam2.stop()
