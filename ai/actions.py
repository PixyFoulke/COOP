
# actions that can be taken based on the results of the yolo detection code

def trigger_alarm():
    print("ALARM TRIGGERED: Threat detected!")


def safe_state():
    print("SAFE: No threats detected.")


def warning_state():
    print("WARNING: Unknown objects detected.")

# Future upgrades:
    # Displayed on OLED screen
    # Predator noise played through speaker
    # phone notification
