
# Runs actions.py based on results from YOLO detection and classification

import os
import cv2
import time
import threading
from picamera2 import Picamera2

from ai.actions import trigger_alarm, safe_state, warning_state
from hardware.oled_display import update_status
from software.email_alert import send_email_alert
from hardware.sensors import getTemperature, getHumidity
from hardware.ads import get_light_state
from hardware.button import get_button_action, reboot_pi
from hardware.door import toggle_door, door_open, door_close
from ai.yolo_detector import process_frame
from ai.chicken_counter import get_chicken_count
from config.settings import get_settings

from software.api_client import (
    update_system_data,
    update_frame,
    start_api,
    get_door_command
)

from software.database import init_database, save_reading


# Used to stop background loops cleanly
stop_event = threading.Event()
lock = threading.Lock()


# Shared inside-camera data
chicken_count = 0
inside_frame = None


# Timing settings
last_email_time = 0
EMAIL_COOLDOWN = 180

last_log_time = 0
LOG_INTERVAL = 900

last_settings_update = 0
SETTINGS_REFRESH = 5


# User settings
expected_chickens = 0
alert_email = ""


def chicken_loop():
    global chicken_count
    global inside_frame

    while not stop_event.is_set():
        try:
            count, frame = get_chicken_count()

            with lock:
                chicken_count = count
                inside_frame = frame

        except Exception as error:
            print(f"Inside camera error: {error}")
            time.sleep(1)
            continue

        time.sleep(1)


def main():
    global last_email_time
    global last_log_time
    global last_settings_update
    global expected_chickens
    global alert_email

    picam2 = None

    try:
        # CAMERA 1: OUTSIDE
        picam2 = Picamera2(0)

        config = picam2.create_preview_configuration(
            main={
                "format": "RGB888",
                "size": (640, 480)
            }
        )

        picam2.configure(config)
        picam2.start()

        # START INSIDE CAMERA THREAD
        chicken_thread = threading.Thread(
            target=chicken_loop,
            daemon=True
        )
        chicken_thread.start()

        # START API SERVER
        api_thread = threading.Thread(
            target=start_api,
            daemon=True
        )
        api_thread.start()

        init_database()

        print("COOP Safety System Running")
        print("Press Ctrl+C to stop")
        print("Press q in the camera window to stop")

        while not stop_event.is_set():

            # UPDATE USER SETTINGS
            if time.time() - last_settings_update > SETTINGS_REFRESH:
                try:
                    settings = get_settings()

                    expected_chickens = settings.get(
                        "chicken_count",
                        0
                    )

                    alert_email = settings.get(
                        "email",
                        ""
                    )

                    last_settings_update = time.time()

                except Exception as error:
                    print(f"Settings error: {error}")

            # CAPTURE OUTSIDE CAMERA FRAME
            try:
                frame = picam2.capture_array()
                result, threats, unknowns = process_frame(frame)
                annotated_frame = result.plot()

            except Exception as error:
                print(f"Outside camera or YOLO error: {error}")
                time.sleep(1)
                continue

            # SENSOR DATA
            try:
                temp = getTemperature()
            except Exception as error:
                print(f"Temperature sensor error: {error}")
                temp = None

            try:
                humidity = getHumidity()
            except Exception as error:
                print(f"Humidity sensor error: {error}")
                humidity = None

            if temp is None:
                temp_f = 0
            else:
                temp_f = (temp * 9 / 5) + 32

            if humidity is None:
                humidity = 0

            try:
                light_state = get_light_state()
            except Exception as error:
                print(f"Light sensor error: {error}")
                light_state = "UNKNOWN"

            current_time = time.strftime("%H:%M:%S")

            # BUTTON CONTROLS
            try:
                action = get_button_action()

                if action == "toggle":
                    print("Door button pressed")
                    toggle_door()

                elif action == "alarm":
                    print("Manual alarm test")
                    trigger_alarm()
                    time.sleep(3)
                    safe_state()

                elif action == "restart":
                    print("Restarting Raspberry Pi")
                    reboot_pi()

            except Exception as error:
                print(f"Button error: {error}")

            # WEBSITE DOOR CONTROLS
            try:
                website_command = get_door_command()

                if website_command == "open":
                    print("Website opening door")
                    door_open()

                elif website_command == "close":
                    print("Website closing door")
                    door_close()

            except Exception as error:
                print(f"Website door command error: {error}")

            # GET INSIDE CAMERA DATA
            with lock:
                chickens = chicken_count

                if inside_frame is not None:
                    inside_display = inside_frame.copy()
                else:
                    inside_display = None

            # LOG DATA EVERY 15 MINUTES
            if time.time() - last_log_time > LOG_INTERVAL:
                try:
                    save_reading(
                        temp_f,
                        humidity,
                        chickens,
                        threats
                    )

                    print("Data logged")
                    last_log_time = time.time()

                except Exception as error:
                    print(f"Database error: {error}")

            # ADD CHICKEN COUNT TEXT
            if inside_display is not None:
                cv2.putText(
                    inside_display,
                    f"Chickens: {chickens}",
                    (20, 450),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.5,
                    (0, 255, 0),
                    3
                )

            # DETERMINE SYSTEM STATUS
            if len(threats) > 0:
                status = "THREAT"

            elif len(unknowns) > 0:
                status = "UNKNOWN"

            elif chickens < expected_chickens:
                status = (
                    f"MISSING "
                    f"({chickens}/{expected_chickens})"
                )

            else:
                status = f"SAFE ({chickens})"

            # RUN ACTIONS
            if status == "THREAT":
                trigger_alarm()

                if time.time() - last_email_time > EMAIL_COOLDOWN:
                    cv2.imwrite(
                        "threat.jpg",
                        annotated_frame
                    )

                    if alert_email:
                        try:
                            send_email_alert(
                                "threat.jpg",
                                alert_email
                            )

                            last_email_time = time.time()

                        except Exception as error:
                            print(f"Email error: {error}")

            elif status == "UNKNOWN":
                warning_state()

            else:
                safe_state()

            # UPDATE OLED
            try:
                update_status(
                    status,
                    temp_f,
                    humidity,
                    current_time,
                    chickens,
                    light_state
                )

            except Exception as error:
                print(f"OLED error: {error}")

            # UPDATE WEBSITE DATA
            try:
                update_system_data(
                    status=status,
                    temperature=temp_f,
                    humidity=humidity,
                    chicken_count=chickens,
                    threats=threats,
                    unknowns=unknowns,
                    light_state=light_state
                )

            except Exception as error:
                print(f"API data error: {error}")

            # CREATE COMBINED VIDEO FRAME
            if inside_display is not None:
                try:
                    combined_frame = cv2.hconcat(
                        [
                            annotated_frame,
                            inside_display
                        ]
                    )

                except Exception as error:
                    print(f"Frame combination error: {error}")
                    combined_frame = annotated_frame

            else:
                combined_frame = annotated_frame

            # SEND VIDEO TO API
            try:
                update_frame(combined_frame)
            except Exception as error:
                print(f"Video API error: {error}")

            # DISPLAY CAMERA WINDOW WHEN DESKTOP IS AVAILABLE
            if os.environ.get("DISPLAY"):
                cv2.imshow(
                    "COOP Safety System",
                    combined_frame
                )

                if cv2.waitKey(1) & 0xFF == ord("q"):
                    print("Q pressed. Stopping...")
                    break

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nCtrl+C pressed. Stopping COOP system...")

    finally:
        stop_event.set()

        try:
            safe_state()
        except Exception:
            pass

        cv2.destroyAllWindows()

        if picam2 is not None:
            try:
                picam2.stop()
            except Exception:
                pass

        print("Cameras stopped")
        print("GPIO resources released")
        print("COOP system shut down safely")


if __name__ == "__main__":
    main()
