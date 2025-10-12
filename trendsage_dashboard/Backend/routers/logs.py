from fastapi import APIRouter
import json
from pathlib import Path

router = APIRouter()

# Use raw strings for Windows paths
KNOWN_LOGS = Path(r"E:\iot_theft_detection\logs\known.json")
UNKNOWN_LOGS = Path(r"E:\iot_theft_detection\logs\unknown.json")

@router.get("/logs/known")
def get_known_logs():
    with open(KNOWN_LOGS, "r") as f:
        return json.load(f)

@router.get("/logs/unknown")
def get_unknown_logs():
    with open(UNKNOWN_LOGS, "r") as f:
        return json.load(f)
