
# code for processing yolo detections and labeling them

from ultralytics import YOLO
import os
from ai.classifier import classify

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "..", "models", "outsidecoop.pt")
MODEL_PATH = os.path.abspath(MODEL_PATH)

model = YOLO(MODEL_PATH)


def process_frame(frame):
    results = model(frame, verbose=False, imgsz=640)
    result = results[0]

    detections = result.boxes

    threats = []
    unknowns = []

    if detections is None:
        return result, threats, unknowns

    for box in detections:
        if box.cls is None:
            continue

        cls_id = int(box.cls[0])
        label = model.names[cls_id]

        status = classify(label)

        if status == "THREAT":
            threats.append(label)
        elif status == "UNKNOWN":
            unknowns.append(label)

    return result, threats, unknowns
