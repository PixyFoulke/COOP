
# Chicken counter using YOLO (inside coop camera)

from ultralytics import YOLO
import os
from picamera2 import Picamera2

# MODEL PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "chicken.pt")
MODEL_PATH = os.path.abspath(MODEL_PATH)

model = YOLO(MODEL_PATH)

# CAMERA SETUP
picam2 = Picamera2()
config = picam2.create_preview_configuration(
    main={"format": "RGB888", "size": (640, 480)}
)
picam2.configure(config)
picam2.start()


def get_chicken_count():
    frame = picam2.capture_array()

    results = model(frame, verbose=False)
    result = results[0]

    boxes = result.boxes

    count = 0

    if boxes is not None:
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            if label.lower() == "chicken":
                count += 1

    return count, result
