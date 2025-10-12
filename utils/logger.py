# utils/logger.py

import os
import json
from datetime import datetime

# Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# File paths
KNOWN_LOG_FILE = os.path.join(LOG_DIR, "known.json")
UNKNOWN_LOG_FILE = os.path.join(LOG_DIR, "unknown.json")

# Initialize JSON files if not exists
for file_path in [KNOWN_LOG_FILE, UNKNOWN_LOG_FILE]:
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f)  # Start with empty list

def load_json_file(file_path):
    """Safely load JSON file, return empty list if file is empty or invalid."""
    try:
        with open(file_path, "r") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except json.JSONDecodeError:
        return []

def log_event(face, objects, alerts=False, capture_path=""):
    """
    Logs detection events to known.json or unknown.json
    :param face: Name of face recognized ("Unknown" if intruder)
    :param objects: List of detected objects
    :param alerts: True if alert triggered
    :param capture_path: Path to saved image if any
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "face_name": face,
        "objects_detected": objects,
        "alert": alerts,
        "capture_path": capture_path
    }

    # Choose file based on known/unknown
    file_path = UNKNOWN_LOG_FILE if face == "Unknown" else KNOWN_LOG_FILE

    # Load existing data safely
    data = load_json_file(file_path)

    # Append new log entry
    data.append(log_entry)

    # Write back to JSON
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)

    print(f"[LOG] Event logged -> {file_path}: {face}, alert={alerts}")
