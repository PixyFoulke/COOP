from pathlib import Path
import os
import winsound
import cv2
import time
import io
import wave
import numpy as np
import threading
import subprocess
from ultralytics import YOLO

base_dir = Path(__file__).parent
hawk_sound_path = r"C:\Users\Student\Videos\Movavi Library\New project.mp4"
fox_sound_path = r"C:\Users\Student\Downloads\pwlpl-realistic-wolf-howling-sound-effect-echoing-wild-call-sfx-444193.mp3"
sound_cache = {}
hawk_play_thread = None
last_hawk_play_ms = 0
last_fox_play_ms = 0


def load_wav_sound(sound_file):
    path = resolve_path(sound_file)
    if path in sound_cache:
        return sound_cache[path]
    if os.path.exists(path) and path.lower().endswith('.wav'):
        try:
            with open(path, 'rb') as f:
                data = f.read()
            sound_cache[path] = data
            return data
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
    return None


def trigger_alarm():
    global sound_muted
    if sound_muted:
        return
    duration_ms = 700
    frequency_hz = 1000
    try:
        winsound.Beep(frequency_hz, duration_ms)
    except RuntimeError:
        winsound.PlaySound(
            "SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)


def play_sound(sound_file):
    global hawk_play_thread, sound_muted
    if sound_muted:
        return

    def play_file(path):
        global hawk_play_thread
        ext = os.path.splitext(path)[1].lower()
        if ext in ('.mp3', '.mp4'):
            abs_path = os.path.abspath(path)
            abs_hawk_path = os.path.abspath(hawk_sound_path)
            if abs_path == abs_hawk_path:
                if hawk_play_thread is not None and hawk_play_thread.is_alive():
                    return True

                def _play_hawk_file(file_path):
                    global hawk_play_thread
                    try:
                        subprocess.run(
                            f'start /wait "" "{file_path}"', shell=True)
                    except Exception as e:
                        print(f"Error playing hawk sound {file_path}: {e}")
                    finally:
                        hawk_play_thread = None

                hawk_play_thread = threading.Thread(
                    target=_play_hawk_file,
                    args=(path,),
                    daemon=True)
                hawk_play_thread.start()
                return True
            os.startfile(path)
            return True
        if ext == '.wav':
            sound_data = load_wav_sound(path)
            if sound_data is not None:
                winsound.PlaySound(
                    sound_data, winsound.SND_MEMORY | winsound.SND_ASYNC)
                return True
            try:
                winsound.PlaySound(
                    path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                return True
            except Exception:
                return False
        return False

    path = resolve_path(sound_file)

    try:
        if os.path.exists(sound_file) and play_file(sound_file):
            return
        if os.path.exists(path) and play_file(path):
            return
    except Exception as e:
        print(f"Error playing sound {sound_file}: {e}")

    # If file missing or unsupported, emit a beep pattern indicating which sound
    fname = os.path.basename(sound_file).lower()
    if 'hawk' in fname:
        winsound.Beep(1000, 300)
        time.sleep(0.05)
        winsound.Beep(1200, 300)
    elif 'fox' in fname:
        winsound.Beep(800, 250)
        time.sleep(0.05)
        winsound.Beep(900, 250)
        time.sleep(0.05)
        winsound.Beep(1000, 250)
    else:
        winsound.Beep(1000, 700)


def notify_user(threat):
    """Show a non-blocking Windows message box notification for the threat."""
    try:
        import ctypes

        def _msg():
            MB_TOPMOST = 0x40000
            ctypes.windll.user32.MessageBoxW(0,
                                             f"{threat} detected near the coop!",
                                             "C.O.O.P Alert",
                                             MB_TOPMOST | 0x0)

        t = threading.Thread(target=_msg, daemon=True)
        t.start()
    except Exception:
        # fallback to simple print
        print(f"ALERT: {threat} detected")


# Load model
model_path = base_dir / 'exp-4.pt'
model = YOLO(str(model_path))

# Camera utilities separated from app logic


def init_camera(device=0, width=640, height=480):
    cap = cv2.VideoCapture(device)
    cap.set(3, width)  # width
    cap.set(4, height)  # height
    return cap


def read_frame(cap):
    if cap is None:
        return False, None
    return cap.read()


def release_camera(cap):
    if cap is not None:
        cap.release()


window_name = 'C.O.O.P Live Detection'
enlarge_camera_view = False
predator_track_history = {}
sound_muted = False
in_settings = False
brightness = 50
contrast = 50
sensitivity = 50
show_time_info = True
show_mode_info = True


def set_window_fullscreen(window_name, enable):
    try:
        # Use cv2 constants for clarity: WINDOW_FULLSCREEN to enable, WINDOW_NORMAL to disable
        val = cv2.WINDOW_FULLSCREEN if enable else cv2.WINDOW_NORMAL
        cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, val)
        if not enable:
            cv2.resizeWindow(window_name, 640, 480)
    except Exception:
        pass


def handle_mouse(event, x, y, flags, param):
    global enlarge_camera_view, in_settings, sound_muted, show_time_info, show_mode_info
    if event == cv2.EVENT_LBUTTONDOWN:
        if in_settings:
            # Back button in settings
            back_button_rect = (50, 90, 150, 120)
            if back_button_rect[0] <= x <= back_button_rect[2] and back_button_rect[1] <= y <= back_button_rect[3]:
                in_settings = False
                return
            # Mute toggle button
            mute_button_rect = (50, 180, 400, 220)
            if mute_button_rect[0] <= x <= mute_button_rect[2] and mute_button_rect[1] <= y <= mute_button_rect[3]:
                sound_muted = not sound_muted
                return
            # Show time toggle button
            time_toggle_rect = (50, 270, 400, 310)
            if time_toggle_rect[0] <= x <= time_toggle_rect[2] and time_toggle_rect[1] <= y <= time_toggle_rect[3]:
                show_time_info = not show_time_info
                return
            # Show mode toggle button
            mode_toggle_rect = (50, 320, 400, 360)
            if mode_toggle_rect[0] <= x <= mode_toggle_rect[2] and mode_toggle_rect[1] <= y <= mode_toggle_rect[3]:
                show_mode_info = not show_mode_info
                return
        else:
            # Enlarge button
            button_left, button_top, button_right, button_bottom = 430, 18, 610, 42
            if button_left <= x <= button_right and button_top <= y <= button_bottom:
                enlarge_camera_view = not enlarge_camera_view
                return
            # Settings button (bottom left) -- match drawn button coordinates
            # drawn as (15, 340, width=100, height=24) so rect is (15,340,115,364)
            settings_button_rect = (15, 340, 115, 364)
            if settings_button_rect[0] <= x <= settings_button_rect[2] and settings_button_rect[1] <= y <= settings_button_rect[3]:
                in_settings = True
                return


def get_class_name(box, names):
    try:
        if hasattr(box.cls, '__len__'):
            cls_index = int(box.cls[0])
        else:
            cls_index = int(box.cls)
        return names[cls_index]
    except Exception:
        return str(box.cls)


def normalize_xyxy(value):
    try:
        if hasattr(value, 'tolist'):
            value = value.tolist()
        if isinstance(value, np.ndarray):
            value = value.tolist()
        if isinstance(value, (list, tuple)) and len(value) > 0 and isinstance(value[0], (list, tuple)):
            value = value[0]
        if isinstance(value, (list, tuple)) and len(value) == 4:
            return [float(v) for v in value]
    except Exception:
        pass
    return None


def get_box_xyxy(box):
    try:
        return normalize_xyxy(box.xyxy)
    except Exception:
        return None


def get_detection_id(box):
    try:
        if hasattr(box, 'track_id') and box.track_id is not None:
            track_id = box.track_id.tolist() if hasattr(
                box.track_id, 'tolist') else box.track_id
            if isinstance(track_id, (list, tuple)) and len(track_id) > 0:
                return int(track_id[0])
            if isinstance(track_id, np.ndarray) and track_id.size == 1:
                return int(track_id.item())
            if isinstance(track_id, int):
                return track_id
        if hasattr(box, 'id') and box.id is not None:
            box_id = box.id.tolist() if hasattr(box.id, 'tolist') else box.id
            if isinstance(box_id, (list, tuple)) and len(box_id) > 0:
                return int(box_id[0])
            if isinstance(box_id, np.ndarray) and box_id.size == 1:
                return int(box_id.item())
            if isinstance(box_id, int):
                return box_id
    except Exception:
        pass
    xyxy = get_box_xyxy(box)
    if xyxy is None:
        return None
    return tuple(int(round(v)) for v in xyxy)


def get_box_area(xyxy):
    try:
        x1, y1, x2, y2 = [float(v) for v in xyxy]
        width = max(0.0, x2 - x1)
        height = max(0.0, y2 - y1)
        return width * height
    except Exception:
        return 0.0


DEFAULT_APP_WIDTH = 640
DEFAULT_APP_HEIGHT = 480
PREVIEW_SIZE = (320, 240)
ENLARGE_BUTTON_RECT = (430, 18, 180, 26)
ALERT_FRAME_THRESHOLD = 5
APPROACH_AREA_RATIO = 1.12
NEAR_CAMERA_HEIGHT_RATIO = 0.35
HAWK_SOUND_COOLDOWN_MS = 10000
FOX_SOUND_COOLDOWN_MS = 6000


def resolve_path(path):
    if not os.path.isabs(path):
        path = str(base_dir / path)
    return path


def draw_label(frame, text, x, y, color):
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)[0]
    cv2.rectangle(frame,
                  (x, y - text_size[1] - 2),
                  (x + text_size[0] + 2, y + 2),
                  (0, 0, 0),
                  -1)
    cv2.putText(frame,
                text,
                (x, y),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                1)


def draw_detection_boxes(frame, results, scale_x=1.0, scale_y=1.0):
    if frame is None or not results:
        return
    for result in results:
        for box in getattr(result, 'boxes', []):
            cls = get_class_name(box, result.names)
            xyxy = get_box_xyxy(box)
            if xyxy is None:
                continue
            x1 = int(xyxy[0] * scale_x)
            y1 = int(xyxy[1] * scale_y)
            x2 = int(xyxy[2] * scale_x)
            y2 = int(xyxy[3] * scale_y)
            color = (0, 255, 0) if cls == "Chicken" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            label_y = y1 - 10 if y1 - 10 > 10 else y1 + 20
            draw_label(frame, cls, x1, label_y, color)


cap = init_camera()
if not cap.isOpened():
    print('Unable to open camera')
    release_camera(cap)
    cv2.destroyAllWindows()
    exit()

cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setMouseCallback(window_name, handle_mouse)
# Ensure the app starts in windowed (not fullscreen) mode and at a reasonable size
try:
    set_window_fullscreen(window_name, False)
    cv2.resizeWindow(window_name, 800, 600)
except Exception:
    pass

consecutive_alert_frames = 0
max_chicken_count = 0
hold_count_until = 0
while True:
    try:
        current_time_ms = time.time() * 1000
        # formatted current time for display
        current_time = time.strftime('%H:%M:%S')
        chicken_count = 0
        current_chicken_ids = set()
        ret, frame = read_frame(cap)
        if not ret or frame is None:
            break

        results = model.track(frame, persist=True)
        if results is None or len(results) == 0:
            results = []

        alert = False
        detected_threat = None
        heightened_threat = False
        threat_condition = None
        for result in results:
            if result.boxes is None or len(result.boxes) == 0:
                continue
            boxes = result.boxes
            for box_idx, box in enumerate(boxes):
                try:
                    cls = get_class_name(box, result.names)
                    xyxy = get_box_xyxy(box)
                    if xyxy is None:
                        continue
                    if cls == "Chicken":
                        chicken_id = get_detection_id(box)
                        if chicken_id is not None:
                            current_chicken_ids.add(chicken_id)
                    else:
                        alert = True
                        detected_threat = cls
                        x1 = int(xyxy[0])
                        y1 = int(xyxy[1])
                        x2 = int(xyxy[2])
                        y2 = int(xyxy[3])
                        current_area = get_box_area(xyxy)
                        box_id = get_detection_id(box)
                        if box_id is None:
                            box_id = f"{cls}_{box_idx}"
                        prev_info = predator_track_history.get(box_id)
                        if prev_info is not None:
                            prev_area = prev_info.get('area', 0.0)
                            if prev_area > 0 and current_area > prev_area * APPROACH_AREA_RATIO:
                                heightened_threat = True
                                threat_condition = "Approaching"
                        if (y2 - y1) / frame.shape[0] >= NEAR_CAMERA_HEIGHT_RATIO or y2 >= frame.shape[0] * 0.80:
                            heightened_threat = True
                            if threat_condition is None:
                                threat_condition = "Near Camera"
                        predator_track_history[box_id] = {
                            'area': current_area,
                            'y2': y2,
                            'cx': (x1 + x2) / 2,
                            'cy': (y1 + y2) / 2
                        }
                except Exception:
                    continue

        chicken_count = len(current_chicken_ids)

        if chicken_count > max_chicken_count:
            max_chicken_count = chicken_count
            hold_count_until = current_time_ms + 1000

        if current_time_ms >= hold_count_until:
            max_chicken_count = chicken_count
            hold_count_until = current_time_ms + 1000

        chicken_count = max_chicken_count

        if alert:
            consecutive_alert_frames += 1
        else:
            consecutive_alert_frames = 0

        high_threat = alert and heightened_threat

        # require 5 continuous frames with a threat before raising alarm
        if consecutive_alert_frames == 5 or (high_threat and consecutive_alert_frames >= 3):
            if detected_threat == "Hawk":
                # play hawk sound only if at least 10 seconds have passed since last play
                try:
                    if current_time_ms - last_hawk_play_ms >= HAWK_SOUND_COOLDOWN_MS:
                        play_sound(hawk_sound_path)
                        last_hawk_play_ms = current_time_ms
                except Exception:
                    pass
            elif detected_threat == "Fox":
                try:
                    if current_time_ms - last_fox_play_ms >= FOX_SOUND_COOLDOWN_MS:
                        play_sound(fox_sound_path)
                        last_fox_play_ms = current_time_ms
                except Exception:
                    pass
            else:
                trigger_alarm()

        if high_threat:
            alert_color = (0, 0, 255)
            alert_text = "HIGH THREAT"
        else:
            alert_color = (190, 80, 80) if alert else (80, 190, 120)
            alert_text = "THREAT" if alert else "SAFE"

        app_height, app_width = 480, 640

        # Settings page
        if in_settings:
            display_frame = np.zeros(
                (app_height, app_width, 3), dtype=np.uint8)
            display_frame[:, :] = (20, 20, 25)

            # Header
            cv2.rectangle(display_frame, (0, 0),
                          (app_width, 65), (12, 40, 70), -1)
            cv2.line(display_frame, (0, 65),
                     (app_width, 65), (70, 130, 180), 2)
            cv2.putText(display_frame, "SETTINGS", (15, 40),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (240, 240, 240), 2)

            # Back button
            cv2.rectangle(display_frame, (50, 90),
                          (150, 120), (70, 130, 180), -1)
            cv2.rectangle(display_frame, (50, 90),
                          (150, 120), (220, 220, 235), 2)
            cv2.putText(display_frame, "< Back", (60, 110),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 235), 1)

            # Sound settings section
            cv2.putText(display_frame, "Notifications:", (50, 160),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (190, 190, 190), 1)

            # Mute button
            mute_status = "MUTED" if sound_muted else "ENABLED"
            mute_color = (100, 100, 255) if sound_muted else (110, 240, 110)
            cv2.rectangle(display_frame, (50, 180),
                          (400, 220), (70, 130, 180), -1)
            cv2.rectangle(display_frame, (50, 180), (400, 220), mute_color, 2)
            cv2.putText(display_frame, "Sound: " + mute_status, (70, 205),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, mute_color, 2)

            # Display toggles section
            cv2.putText(display_frame, "Display options:", (50, 250),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (190, 190, 190), 1)

            time_status = "ON" if show_time_info else "OFF"
            time_color = (110, 240, 110) if show_time_info else (180, 80, 80)
            cv2.rectangle(display_frame, (50, 270),
                          (400, 310), (70, 130, 180), -1)
            cv2.rectangle(display_frame, (50, 270), (400, 310), time_color, 2)
            cv2.putText(display_frame, f"Show Time: {time_status}", (70, 295),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, time_color, 2)

            mode_status = "ON" if show_mode_info else "OFF"
            mode_color = (110, 240, 110) if show_mode_info else (180, 80, 80)
            cv2.rectangle(display_frame, (50, 320),
                          (400, 360), (70, 130, 180), -1)
            cv2.rectangle(display_frame, (50, 320), (400, 360), mode_color, 2)
            cv2.putText(display_frame, f"Show Mode: {mode_status}", (70, 345),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, mode_color, 2)

            cv2.putText(display_frame, "Click a button to toggle display items.", (50, 390),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (150, 150, 150), 1)

            # Footer
            cv2.rectangle(display_frame, (0, app_height - 28),
                          (app_width, app_height), (12, 18, 28), -1)
            cv2.putText(display_frame,
                        "press 'q' to quit",
                        (20, app_height - 6),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (220, 220, 235),
                        1)

            cv2.imshow(window_name, display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        if enlarge_camera_view:
            display_frame = cv2.resize(frame, (app_width, app_height))
            overlay = display_frame.copy()
            cv2.rectangle(overlay, (0, 0), (app_width,
                          app_height), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.18, display_frame,
                            0.82, 0, display_frame)

            scale_x = display_frame.shape[1] / \
                frame.shape[1] if frame.shape[1] > 0 else 1
            scale_y = display_frame.shape[0] / \
                frame.shape[0] if frame.shape[0] > 0 else 1
            draw_detection_boxes(display_frame, results, scale_x, scale_y)

            button_x, button_y, button_w, button_h = 430, 18, 180, 26
            cv2.rectangle(display_frame,
                          (button_x, button_y),
                          (button_x + button_w, button_y + button_h),
                          (12, 40, 70),
                          -1)
            cv2.rectangle(display_frame,
                          (button_x, button_y),
                          (button_x + button_w, button_y + button_h),
                          (70, 130, 180),
                          2)
            cv2.putText(display_frame,
                        "Restore Camera",
                        (button_x + 10, button_y + 18),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (220, 220, 235),
                        1)
            cv2.putText(display_frame,
                        "Press button to restore the interface",
                        (15, app_height - 12),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (220, 220, 235),
                        1)
            cv2.imshow(window_name, display_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        display_frame = np.zeros((app_height, app_width, 3), dtype=np.uint8)
        display_frame[:, :] = (20, 20, 25)
        overlay = display_frame.copy()
        cv2.rectangle(overlay, (0, 0), (app_width,
                      app_height), (35, 35, 45), -1)
        cv2.addWeighted(overlay, 0.08, display_frame, 0.92, 0, display_frame)

        # Header
        cv2.rectangle(display_frame, (0, 0), (app_width, 65), (12, 40, 70), -1)
        cv2.line(display_frame, (0, 65), (app_width, 65), (70, 130, 180), 2)
        cv2.putText(display_frame,
                    "C.O.O.P",
                    (15, 38),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.3,
                    (240, 240, 240),
                    2)
        cv2.putText(display_frame,
                    "Live Detection",
                    (165, 36),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (200, 220, 240),
                    1)
        cv2.putText(display_frame,
                    "Advanced Coop Monitoring",
                    (15, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.45,
                    (170, 190, 220),
                    1)

        # Settings button (bottom left)
        settings_button_x, settings_button_y, settings_button_w, settings_button_h = 15, 340, 100, 24
        cv2.rectangle(display_frame,
                      (settings_button_x, settings_button_y),
                      (settings_button_x + settings_button_w,
                       settings_button_y + settings_button_h),
                      (12, 40, 70),
                      -1)
        cv2.rectangle(display_frame,
                      (settings_button_x, settings_button_y),
                      (settings_button_x + settings_button_w,
                       settings_button_y + settings_button_h),
                      (70, 130, 180),
                      2)
        cv2.putText(display_frame,
                    "Settings",
                    (settings_button_x + 5, settings_button_y + 16),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (220, 220, 235),
                    1)

        # Enlarge Camera button
        button_x, button_y, button_w, button_h = 430, 18, 180, 26
        cv2.rectangle(display_frame,
                      (button_x, button_y),
                      (button_x + button_w, button_y + button_h),
                      (12, 40, 70),
                      -1)
        cv2.rectangle(display_frame,
                      (button_x, button_y),
                      (button_x + button_w, button_y + button_h),
                      (70, 130, 180),
                      2)
        cv2.putText(display_frame,
                    "Enlarge Camera",
                    (button_x + 10, button_y + 18),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (220, 220, 235),
                    1)

        # Info cards with modern styling
        card_y = 85
        card_height = 65
        card_width = 290

        cv2.rectangle(display_frame, (15, card_y),
                      (15 + card_width, card_y + card_height), (35, 40, 50), -1)
        cv2.rectangle(display_frame, (15, card_y),
                      (15 + card_width, card_y + card_height), (80, 180, 110), 1)
        cv2.putText(display_frame, "Chickens", (25, card_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (190, 190, 190), 1)
        cv2.putText(display_frame, str(chicken_count), (25, card_y + card_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.4, (110, 240, 110), 2)

        alert_color = (190, 80, 80) if alert else (80, 190, 120)
        alert_text = "THREAT" if alert else "SAFE"
        cv2.rectangle(display_frame, (330, card_y),
                      (330 + card_width, card_y + card_height), (35, 40, 50), -1)
        cv2.rectangle(display_frame, (330, card_y),
                      (330 + card_width, card_y + card_height), alert_color, 1)
        cv2.putText(display_frame, "Alert Status", (340, card_y + 15),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.72, (190, 190, 190), 1)
        cv2.putText(display_frame, alert_text, (340, card_y + card_height - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.25, alert_color, 2)

        card_y = 155
        if show_time_info:
            cv2.rectangle(display_frame, (15, card_y),
                          (15 + card_width, card_y + card_height), (35, 40, 50), -1)
            cv2.rectangle(display_frame, (15, card_y),
                          (15 + card_width, card_y + card_height), (140, 140, 140), 1)
            cv2.putText(display_frame, "Time", (25, card_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (190, 190, 190), 1)
            cv2.putText(display_frame, current_time, (25, card_y + card_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (220, 220, 220), 2)
        else:
            cv2.rectangle(display_frame, (15, card_y),
                          (15 + card_width, card_y + card_height), (35, 40, 50), -1)
            cv2.rectangle(display_frame, (15, card_y),
                          (15 + card_width, card_y + card_height), (100, 100, 100), 1)
            cv2.putText(display_frame, "Time", (25, card_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (150, 150, 150), 1)
            cv2.putText(display_frame, "Hidden", (25, card_y + card_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (150, 150, 150), 2)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray_frame)
        if brightness > 100:
            day_night_status = "DAY"
            day_night_color = (60, 170, 220)
        else:
            day_night_status = "NIGHT"
            day_night_color = (130, 90, 190)

        if show_mode_info:
            cv2.rectangle(display_frame, (330, card_y),
                          (330 + card_width, card_y + card_height), (35, 40, 50), -1)
            cv2.rectangle(display_frame, (330, card_y),
                          (330 + card_width, card_y + card_height), day_night_color, 1)
            cv2.putText(display_frame, "Mode", (340, card_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (190, 190, 190), 1)
            cv2.putText(display_frame, day_night_status, (340, card_y + card_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, day_night_color, 2)
        else:
            cv2.rectangle(display_frame, (330, card_y),
                          (330 + card_width, card_y + card_height), (35, 40, 50), -1)
            cv2.rectangle(display_frame, (330, card_y),
                          (330 + card_width, card_y + card_height), (100, 100, 100), 1)
            cv2.putText(display_frame, "Mode", (340, card_y + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.72, (150, 150, 150), 1)
            cv2.putText(display_frame, "Hidden", (340, card_y + card_height - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.1, (150, 150, 150), 2)

        status_text = f"Detected: {detected_threat if detected_threat else 'None'}"
        if alert and threat_condition:
            status_text += f" ({threat_condition})"
        # Background for status text
        cv2.rectangle(display_frame, (10, 225), (400, 250), (12, 18, 28), -1)
        cv2.putText(display_frame, status_text, (15, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (190, 190, 220), 1)
        cv2.line(display_frame, (15, 250),
                 (app_width - 15, 250), (70, 80, 100), 1)

        preview = cv2.resize(frame, (320, 240))
        ph, pw = preview.shape[:2]
        scale_x = pw / frame.shape[1] if frame.shape[1] > 0 else 1
        scale_y = ph / frame.shape[0] if frame.shape[0] > 0 else 1

        draw_detection_boxes(preview, results, scale_x, scale_y)

        x_offset = max(0, app_width - pw - 15)
        y_offset = max(0, app_height - ph - 15)
        if y_offset + ph <= app_height and x_offset + pw <= app_width:
            display_frame[y_offset:y_offset + ph,
                          x_offset:x_offset + pw] = preview
            cv2.rectangle(display_frame,
                          (x_offset - 2, y_offset - 2),
                          (x_offset + pw + 2, y_offset + ph + 2),
                          (70, 130, 180),
                          2)
            cv2.rectangle(display_frame,
                          (x_offset - 2, y_offset - 2),
                          (x_offset + pw + 2, y_offset + ph + 2),
                          (100, 150, 200),
                          1)

        cv2.rectangle(display_frame,
                      (0, app_height - 28),
                      (app_width, app_height),
                      (12, 18, 28),
                      -1)
        cv2.putText(display_frame,
                    "press 'q' to quit | enhanced c.o.o.p interface",
                    (20, app_height - 6),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (220, 220, 235),
                    1)

        cv2.imshow(window_name, display_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    except Exception as e:
        print(f"Error in main loop: {e}")
        continue

try:
    if 'cap' in locals() and cap is not None:
        try:
            release_camera(cap)
        except Exception:
            try:
                cap.release()
            except Exception:
                pass
finally:
    try:
        cv2.destroyAllWindows()
    except Exception:
        pass
