
# classifies labels as either SAFE, THREAT, UNKNOWN, or IGNORE
# based on labels from the YOLO detection code

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
    "opossum",
    "snake",
    "coyote",
    "raccoon",
    "skunk"
}

IGNORE = {
    "bear"
}


def classify(label: str):

    label = label.lower().strip()

    if label in IGNORE:
        return "IGNORE"

    elif label in SAFE:
        return "SAFE"

    elif label in THREAT:
        return "THREAT"

    else:
        return "UNKNOWN"
