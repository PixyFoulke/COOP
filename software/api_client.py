
from flask import Flask, jsonify, Response
from flask_cors import CORS
import cv2
import threading


app = Flask(__name__)

# ALLOW WEBSITE CONNECTIONS
CORS(app)


# SHARED SYSTEM STATE
system_data = {
    "status": "SAFE",
    "temperature": 0,
    "humidity": 0,
    "chicken_count": 0,
    "threats": [],
    "unknowns": []
}


# SHARED VIDEO FRAME
output_frame = None
lock = threading.Lock()


# UPDATE JSON DATA
def update_system_data(
    status,
    temperature,
    humidity,
    chicken_count,
    threats,
    unknowns
):
    system_data["status"] = status
    system_data["temperature"] = round(temperature, 1)
    system_data["humidity"] = round(humidity, 1)
    system_data["chicken_count"] = chicken_count
    system_data["threats"] = threats
    system_data["unknowns"] = unknowns


# UPDATE VIDEO FRAME
def update_frame(frame):
    global output_frame

    with lock:
        output_frame = frame.copy()


# JSON ENDPOINT
@app.route("/status")
def status():
    return jsonify(system_data)


# VIDEO STREAM
def generate_frames():
    global output_frame

    while True:
        with lock:

            if output_frame is None:
                continue

            ret, buffer = cv2.imencode(".jpg", output_frame)

            if not ret:
                continue

            frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )


@app.route("/video_feed")
def video_feed():
    return Response(
        generate_frames(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


# START SERVER
def start_api():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
