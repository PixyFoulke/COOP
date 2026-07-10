
import sqlite3
import time


DB_PATH = "coop_data.db"


def init_database():

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

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

    conn.commit()
    conn.close()


def save_reading(temp, humidity, chickens, threats):

    conn = sqlite3.connect(DB_PATH)

    cursor = conn.cursor()

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO readings
    (timestamp, temperature, humidity, chickens, threats)

    VALUES (?, ?, ?, ?, ?)
    """,
                   (
                       timestamp,
                       temp,
                       humidity,
                       chickens,
                       str(threats)
                   ))

    conn.commit()
    conn.close()
