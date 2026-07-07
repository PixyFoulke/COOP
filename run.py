
# Runs actions.py based off of the results of yolo_detector.py and classifier.py

import os
import cv2
import time
import threading
from picamera2 import Picamera2

from ai.actions import trigger_alarm, safe_state, warning_state
from hardware.oled_display import update_status
from software.email_alert import send_email_alert
from hardware.sensors import getTemperature, getHumidity
from ai.yolo_detector import process_frame
from ai.chicken_counter import get_chicken_count

from software.api_client import (
    update_system_data,
    update_frame,
    start_api
)


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
inside_frame = None

lock = threading.Lock()


# CHICKEN THREAD (CAMERA 2 INSIDE COOP)
def chicken_loop():
    global chicken_count
    global inside_frame

    while True:
        try:
            count, frame = get_chicken_count()

            with lock:
                chicken_count = count
                inside_frame = frame

        except:
            continue

        time.sleep(1)


# Start chicken thread
threading.Thread(target=chicken_loop, daemon=True).start()


# START API SERVER
threading.Thread(
    target=start_api,
    daemon=True
).start()


print("COOP Safety System Running... Press 'q' to quit")


# MAIN LOOP (OUTSIDE THREAT DETECTION CAMERA)
while True:

    # OUTSIDE CAMERA
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

    # GET INSIDE CAMERA DATA
    with lock:
        chickens = chicken_count
        inside_display = inside_frame

    # ADD CHICKEN COUNT TEXT
    if inside_display is not None:

        inside_display = inside_display.copy()

        cv2.putText(
            inside_display,
            f"Chickens: {chickens}",
            (20, 450),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.5,
            (0, 255, 0),
            3
        )

    # DETERMINE SYSTEM STATUS
    if len(threats) > 0:
        status = "THREAT"

    elif len(unknowns) > 0:
        status = "UNKNOWN"

    elif chickens < 10:
        status = f"MISSING ({chickens})"

    else:
        status = f"SAFE ({chickens})"

    # RUN ACTIONS
    if status == "THREAT":

        trigger_alarm()
        update_status(status, temp_f, humidity, current_time, chickens)

        if time.time() - last_email_time > EMAIL_COOLDOWN:
            cv2.imwrite("threat.jpg", annotated_frame)
            send_email_alert("threat.jpg")
            last_email_time = time.time()

    elif status == "UNKNOWN":

        warning_state()
        update_status(status, temp_f, humidity, current_time, chickens)

    else:

        safe_state()
        update_status(status, temp_f, humidity, current_time, chickens)

    # UPDATE API DATA (ALL STATUSES)
    update_system_data(
        status=status,
        temperature=temp_f,
        humidity=humidity,
        chicken_count=chickens,
        threats=threats,
        unknowns=unknowns
    )

    # CREATE COMBINED VIDEO FRAME
    if inside_display is not None:

        combined_frame = cv2.hconcat(
            [
                annotated_frame,
                inside_display
            ]
        )

    else:
        combined_frame = annotated_frame

    # SEND VIDEO TO API
    update_frame(combined_frame)

    # DISPLAY BOTH CAMERAS LOCALLY
    cv2.imshow(
        "COOP Safety System",
        combined_frame
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    time.sleep(0.01)


cv2.destroyAllWindows()
picam2.stop()
