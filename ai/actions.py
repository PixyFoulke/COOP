
# actions that can be taken based on the results of the yolo detection code

last_state = None


def trigger_alarm():
    global last_state

    if last_state != "THREAT":
        print("ALARM TRIGGERED: Threat detected!")

    last_state = "THREAT"


def safe_state():
    global last_state

    if last_state != "SAFE":
        print("SAFE: No threats detected.")

    last_state = "SAFE"


def warning_state():
    global last_state

    if last_state != "WARNING":
        print("WARNING: Unknown objects detected.")

    last_state = "WARNING"


# Future upgrades:
    # Displayed on OLED screen
    # Predator noise played through speaker
    # phone notification
