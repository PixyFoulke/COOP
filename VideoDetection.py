import os
from ultralytics import YOLO
import cv2
import smtplib

model = YOLO("exp-29.pt")
# no tracking, replace with actual path to video file
video_path = r"C:\Users\Student\Downloads\Clipto AI Video Downloader Our Chickens Have Grown So Much! 🐔 Meet the Flock in June 2026 - Backyard Chickens.mp4"
if not os.path.exists(video_path):
    raise FileNotFoundError(f"Video file not found: {video_path}")
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise RuntimeError(f"Unable to open video file: {video_path}")

while cap.isOpened():
    success, frame = cap.read()

    if not success:
        break

    results = model(frame)

    annotated_frame = results[0].plot()

    cv2.imshow("YOLO Video Analysis", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
