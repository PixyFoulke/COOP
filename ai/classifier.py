# classifies labels as either SAFE, THREAT, or UNKNOWN based on labels from the yolo_detection code

SAFE = {
    "deer",
    "chipmunk",
    "human",
    "cow",
    "chicken",
    "domestic cat",
    "horse",
    "squirrel",
    "dog"
}

THREAT = {
    "fox",
    "predatory bird",
    "bear",
    "opossum",
    "snake",
    "coyote",
    "raccoon",
    "skunk"
}


def classify(label: str):
    label = label.lower().strip()

    if label in SAFE:
        return "SAFE"
    elif label in THREAT:
        return "THREAT"
    else:
        return "UNKNOWN"
