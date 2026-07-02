
# code for processing the yolo detection results and labeling them

from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import os
import time

from ai.classifier import classify
from ai.actions import trigger_alarm, safe_state, warning_state

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "outsidecoop.pt")

model = YOLO(MODEL_PATH)

picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()

print("Running safety layer...")

while True:
    frame = picam2.capture_array()

    results = model(frame, verbose=False)

    detections = results[0].boxes

    threats = []
    unknowns = []

    for box in detections:
        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        status = classify(label)

        if status == "THREAT":
            threats.append(label)
        elif status == "UNKNOWN":
            unknowns.append(label)

    if len(threats) > 0:
        trigger_alarm()
    elif len(unknowns) > 0:
        warning_state()
    else:
        safe_state()

    annotated = results[0].plot()
    cv2.imshow("COOP Safety System", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
picam2.stop()
