
# code for processing the yolo detection results and labeling them

from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import os

from ai.classifier import classify

# OLED status link
from hardware.oled_display import update_status

# MODEL PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "outsidecoop.pt")

model = YOLO(MODEL_PATH)

# CAMERA SETUP
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 640)}
)
picam2.configure(config)
picam2.start()

print("COOP Safety System Running... (press Q to quit)")

# MAIN LOOP
while True:
    frame = picam2.capture_array()

    results = model(frame, verbose=False)
    detections = results[0].boxes

    threats = []
    unknowns = []

    # CLASSIFY DETECTIONS
    if detections is not None:
        for box in detections:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            status = classify(label)

            if status == "THREAT":
                threats.append(label)
            elif status == "UNKNOWN":
                unknowns.append(label)

    # COOP STATUS DECISION
    if len(threats) > 0:
        update_status("THREAT")

    elif len(unknowns) > 0:
        update_status("UNKNOWN")

    else:
        update_status("SAFE")

    # DISPLAY
    annotated = results[0].plot()
    cv2.imshow("COOP Safety System", annotated)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# CLEANUP
cv2.destroyAllWindows()
picam2.stop()
