
# Runs actions.py based off of the results of yolo_detector.py and classifier.py

import os
import cv2
import time
from ultralytics import YOLO
from picamera2 import Picamera2

from ai.classifier import classify
from ai.actions import trigger_alarm, safe_state, warning_state


# MODEL SETUP
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "outsidecoop.pt")

model = YOLO(MODEL_PATH)


# CAMERA SETUP
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()

print("COOP Safety System Running... Press 'q' to quit")


# MAIN LOOP
while True:
    frame = picam2.capture_array()

    # YOLO inference
    results = model(frame, verbose=False)
    result = results[0]

    detections = result.boxes

    threats = []
    unknowns = []

    # CLASSIFY DETECTIONS
    for box in detections:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        status = classify(label)

        if status == "THREAT":
            threats.append(label)
        elif status == "UNKNOWN":
            unknowns.append(label)

    # DECISION LOGIC
    if len(threats) > 0:
        trigger_alarm()

    elif len(unknowns) > 0:
        warning_state()

    else:
        safe_state()

    # DISPLAY
    annotated_frame = result.plot()
    cv2.imshow("COOP Safety System", annotated_frame)

    # Quit key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(0.01)


# CLEAN EXIT
cv2.destroyAllWindows()
picam2.stop()
