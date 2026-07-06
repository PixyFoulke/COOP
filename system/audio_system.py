
import os
import sys


try:
    import winsound
except ImportError:
    winsound = None

try:
    from pip import playsound
except ImportError:
    playsound = None

TARGET_ANIMALS = {"fox", "snake", "coyote", "raccoon", "racoon"}
PREDATORY_BIRDS = {"hawk", "eagle", "owl", "falcon",
                   "osprey", "vulture", "buzzard", "harrier", "kestrel"}
# actual bundled audio file (keeps extension used in repository)
AUDIO_FILE_NAME = "pwlpl-realistic-wolf-howling-sound-effect-echoing-wild-call-sfx-444193.mp3"
BIRD_AUDIO_FILE_NAME = "C:\\Users\\Student\\Desktop\\COOP\\COOP\\COOP\\system\\Audio Files\\XC691878 - Red-tailed Hawk - Buteo jamaicensis.mp3"


def _get_audio_file_path(file_name=AUDIO_FILE_NAME):
    base_dir = os.path.dirname(__file__)
    # audio file is stored in a subdirectory named 'Audio Files' next to this module
    return os.path.join(base_dir, "Audio Files", file_name)


def _normalize_label(label):
    if label is None:
        return ""
    if isinstance(label, bytes):
        label = label.decode("utf-8", errors="ignore")
    return str(label).strip().lower()


def _extract_labels_from_detection(detection):
    if isinstance(detection, str):
        yield detection
        return

    if isinstance(detection, dict):
        for key in ("label", "class", "name", "class_name"):
            if key in detection and detection[key] is not None:
                yield detection[key]
                return
        return

    for attr in ("label", "class_name", "name", "class"):
        if hasattr(detection, attr):
            value = getattr(detection, attr)
            if value is not None:
                yield value
                return


def _has_target_animal(detections):
    if detections is None:
        return False

    if isinstance(detections, (str, bytes)):
        return _normalize_label(detections) in TARGET_ANIMALS

    if isinstance(detections, dict):
        detections = [detections]

    try:
        iterator = iter(detections)
    except TypeError:
        detections = [detections]

    for detection in detections:
        if detection is None:
            continue
        if isinstance(detection, (str, bytes)):
            label = _normalize_label(detection)
            if label in TARGET_ANIMALS:
                return True
            continue
        for label in _extract_labels_from_detection(detection):
            if _normalize_label(label) in TARGET_ANIMALS:
                return True
    return False


def _has_predatory_bird(detections):
    if detections is None:
        return False

    if isinstance(detections, (str, bytes)):
        return _normalize_label(detections) in PREDATORY_BIRDS

    if isinstance(detections, dict):
        detections = [detections]

    try:
        iterator = iter(detections)
    except TypeError:
        detections = [detections]

    for detection in detections:
        if detection is None:
            continue
        if isinstance(detection, (str, bytes)):
            label = _normalize_label(detection)
            if label in PREDATORY_BIRDS:
                return True
            continue
        for label in _extract_labels_from_detection(detection):
            if _normalize_label(label) in PREDATORY_BIRDS:
                return True
    return False


def _play_sound(file_path):
    if winsound is not None:
        try:
            winsound.PlaySound(
                file_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return
        except RuntimeError:
            pass

    if playsound is not None:
        playsound(file_path)
        return

    raise RuntimeError(
        "Audio playback is not available. Install playsound or run on Windows with winsound.")


def play_pwlpl_on_target_detection(detections):
    """Play pwlpl sound when YOLO detects a fox, snake, coyote, raccoon, or predatory bird."""
    if _has_predatory_bird(detections):
        audio_file = _get_audio_file_path(BIRD_AUDIO_FILE_NAME)
    elif _has_target_animal(detections):
        audio_file = _get_audio_file_path()
    else:
        return False

    if not os.path.isfile(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")

    _play_sound(audio_file)
    return True
