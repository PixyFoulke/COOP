# code needs to be run from the COOP directory

import os
import cv2
from ultralytics import YOLO
from picamera2 import Picamera2

# Model path (safe)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "outsidecoop.pt")

model = YOLO(MODEL_PATH)

# Camera
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()

print("COOP Detection Running... Press 'q' to quit")

while True:
    frame = picam2.capture_array()

    # YOLO inference
    results = model(frame, verbose=False)

    annotated_frame = results[0].plot()

    cv2.imshow("COOP Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
picam2.stop()
