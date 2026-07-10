
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import cv2
import threading
import json
import os
import sqlite3


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
    "unknowns": [],
    "light_state": "DAY"

}


# DOOR COMMAND
door_command = None


# OPEN DOOR COMMAND
@app.route("/door/open", methods=["POST"])
def open_door_command():

    global door_command

    door_command = "open"

    return jsonify(
        {
            "message": "Open command sent"
        }
    )


# CLOSE DOOR COMMAND
@app.route("/door/close", methods=["POST"])
def close_door_command():

    global door_command

    door_command = "close"

    return jsonify(
        {
            "message": "Close command sent"
        }
    )


# GET DOOR COMMAND
def get_door_command():

    global door_command

    command = door_command

    door_command = None

    return command


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
    unknowns,
    light_state
):

    system_data["status"] = status
    system_data["temperature"] = round(temperature, 1)
    system_data["humidity"] = round(humidity, 1)
    system_data["chicken_count"] = chicken_count
    system_data["threats"] = threats
    system_data["unknowns"] = unknowns
    system_data["light_state"] = light_state


# UPDATE VIDEO FRAME
def update_frame(frame):

    global output_frame

    with lock:

        output_frame = frame.copy()


# STATUS JSON ENDPOINT
@app.route("/status")
def status():

    return jsonify(system_data)


# COOP DATA HISTORY
@app.route("/history")
def history():

    db_path = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "coop_data.db"
        )
    )

    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT timestamp, temperature, humidity, chickens, threats
        FROM readings
        WHERE timestamp >= datetime('now','-24 hours')
        ORDER BY timestamp ASC
        LIMIT 96
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append(

            {

                "timestamp": row[0],

                "temperature": row[1],

                "humidity": row[2],

                "chickens": row[3],

                "threats": row[4]

            }

        )

    return jsonify(data)


# SAVE USER SETTINGS
@app.route("/settings", methods=["POST"])
def save_settings():

    data = request.json

    settings = {

        "chicken_count": int(data["chicken_count"]),

        "email": data["email"]

    }

    settings_file = os.path.join(

        os.path.dirname(__file__),

        "..",

        "config",

        "settings.json"

    )

    with open(settings_file, "w") as file:

        json.dump(

            settings,

            file,

            indent=4

        )

    return jsonify(

        {

            "message": "Settings saved",

            "settings": settings

        }

    )


# VIDEO STREAM
def generate_frames():

    global output_frame

    while True:

        with lock:

            if output_frame is None:

                continue

            ret, buffer = cv2.imencode(

                ".jpg",

                output_frame

            )

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
