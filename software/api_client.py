
from flask import (
    Flask,
    jsonify,
    Response,
    request,
    send_from_directory
)

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


# DOOR SCHEDULE
door_schedule = {
    "open_time": "",
    "close_time": ""
}


# SHARED VIDEO FRAME
output_frame = None
lock = threading.Lock()


# OPEN DOOR COMMAND
@app.route("/door/open", methods=["POST"])
def open_door_command():

    global door_command

    door_command = "open"

    return jsonify({
        "message": "Open command sent"
    })


# CLOSE DOOR COMMAND
@app.route("/door/close", methods=["POST"])
def close_door_command():

    global door_command

    door_command = "close"

    return jsonify({
        "message": "Close command sent"
    })


# GET DOOR COMMAND
def get_door_command():

    global door_command

    command = door_command
    door_command = None

    return command


# SAVE DOOR SCHEDULE
@app.route("/door/schedule", methods=["POST"])
def save_door_schedule():

    global door_schedule

    data = request.get_json()

    if data is None:

        return jsonify({
            "error": "No schedule data received"
        }), 400

    open_time = data.get(
        "open_time",
        ""
    )

    close_time = data.get(
        "close_time",
        ""
    )

    if not open_time or not close_time:

        return jsonify({
            "error": "Both times are required"
        }), 400

    if open_time == close_time:

        return jsonify({
            "error": "Open and close times must be different"
        }), 400

    door_schedule = {
        "open_time": open_time,
        "close_time": close_time
    }

    schedule_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "door_schedule.json"
        )
    )

    try:

        with open(schedule_file, "w") as file:

            json.dump(
                door_schedule,
                file,
                indent=4
            )

    except Exception as error:

        return jsonify({
            "error": f"Could not save schedule: {error}"
        }), 500

    return jsonify({
        "message": "Door schedule saved",
        "open_time": open_time,
        "close_time": close_time
    })


# GET DOOR SCHEDULE
@app.route("/door/schedule", methods=["GET"])
def read_door_schedule():

    return jsonify(door_schedule)


# ALLOW RUN.PY TO READ CURRENT SCHEDULE
def get_door_schedule():

    return door_schedule.copy()


# LOAD SAVED DOOR SCHEDULE
def load_door_schedule():

    global door_schedule

    schedule_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "door_schedule.json"
        )
    )

    try:

        with open(schedule_file, "r") as file:

            saved_schedule = json.load(file)

        door_schedule = {
            "open_time": saved_schedule.get(
                "open_time",
                ""
            ),
            "close_time": saved_schedule.get(
                "close_time",
                ""
            )
        }

        print(
            "Door schedule loaded:",
            door_schedule
        )

    except FileNotFoundError:

        print(
            "No saved door schedule found"
        )

    except Exception as error:

        print(
            f"Door schedule load error: {error}"
        )


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
    system_data["temperature"] = round(
        temperature,
        1
    )
    system_data["humidity"] = round(
        humidity,
        1
    )
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
        SELECT
            timestamp,
            temperature,
            humidity,
            chickens,
            threats
        FROM readings
        WHERE timestamp >= datetime(
            'now',
            '-24 hours'
        )
        ORDER BY timestamp ASC
        LIMIT 96
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "timestamp": row[0],
            "temperature": row[1],
            "humidity": row[2],
            "chickens": row[3],
            "threats": row[4]
        })

    return jsonify(data)


# SAVE USER SETTINGS
@app.route("/settings", methods=["POST"])
def save_settings():

    data = request.get_json()

    if data is None:

        return jsonify({
            "error": "No settings data received"
        }), 400

    try:

        settings = {
            "chicken_count": int(
                data["chicken_count"]
            ),
            "email": data["email"]
        }

    except (
        KeyError,
        TypeError,
        ValueError
    ):

        return jsonify({
            "error": "Invalid settings data"
        }), 400

    settings_file = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "config",
            "settings.json"
        )
    )

    try:

        with open(settings_file, "w") as file:

            json.dump(
                settings,
                file,
                indent=4
            )

    except Exception as error:

        return jsonify({
            "error": f"Could not save settings: {error}"
        }), 500

    return jsonify({
        "message": "Settings saved",
        "settings": settings
    })


# THREAT EVENT HISTORY
@app.route("/threats/history")
def threat_history():

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
        SELECT
            timestamp,
            threat_type,
            image_filename
        FROM threat_events
        WHERE timestamp >= datetime(
            'now',
            '-24 hours'
        )
        ORDER BY timestamp DESC
    """)

    rows = cursor.fetchall()

    conn.close()

    data = []

    for row in rows:

        data.append({
            "timestamp": row[0],
            "threat_type": row[1],
            "image_filename": row[2],
            "image_url": (
                "/alerts/" + row[2]
            )
        })

    return jsonify(data)


# SERVE THREAT IMAGES
@app.route("/alerts/<path:filename>")
def alert_image(filename):

    alerts_directory = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "alerts"
        )
    )

    return send_from_directory(
        alerts_directory,
        filename
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
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame
            + b"\r\n"
        )


@app.route("/video_feed")
def video_feed():

    return Response(
        generate_frames(),
        mimetype=(
            "multipart/x-mixed-replace; "
            "boundary=frame"
        )
    )


# START SERVER
def start_api():

    load_door_schedule()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True
    )
