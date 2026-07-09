
door_open = False


def open_door():
    global door_open
    door_open = True
    print("Opening door...")


def close_door():
    global door_open
    door_open = False
    print("Closing door...")


def toggle_door():
    global door_open

    if door_open:
        close_door()
    else:
        open_door()

    return door_open


def is_door_open():
    return door_open
