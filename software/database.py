import os
import sqlite3
import time


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        ".."
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "coop_data.db"
)


def init_database():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # SENSOR READINGS
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature REAL,
            humidity REAL,
            chickens INTEGER,
            threats TEXT
        )
    """)

    # THREAT EVENTS AND IMAGES
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS threat_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            threat_type TEXT,
            image_filename TEXT
        )
    """)

    conn.commit()
    conn.close()


def save_reading(temp, humidity, chickens, threats):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO readings
        (
            timestamp,
            temperature,
            humidity,
            chickens,
            threats
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        timestamp,
        temp,
        humidity,
        chickens,
        str(threats)
    ))

    conn.commit()
    conn.close()


def save_threat_event(threat_type, image_filename):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO threat_events
        (
            timestamp,
            threat_type,
            image_filename
        )
        VALUES (?, ?, ?)
    """, (
        timestamp,
        threat_type,
        image_filename
    ))

    conn.commit()
    conn.close()
