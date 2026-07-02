
# code for processing the yolo detection results and labeling them

from ultralytics import YOLO
import os

from ai.classifier import classify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "outsidecoop.pt")
MODEL_PATH = os.path.abspath(MODEL_PATH)

model = YOLO(MODEL_PATH)


def process_frame(frame):
    results = model(frame, verbose=False)
    result = results[0]

    detections = result.boxes

    threats = []
    unknowns = []

    if detections is not None:
        for box in detections:
            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            status = classify(label)

            if status == "THREAT":
                threats.append(label)
            elif status == "UNKNOWN":
                unknowns.append(label)

    return result, threats, unknowns
