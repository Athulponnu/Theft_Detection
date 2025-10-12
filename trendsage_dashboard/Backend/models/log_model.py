from pydantic import BaseModel
from typing import List, Optional

class LogEntry(BaseModel):
    timestamp: str
    face_name: Optional[str] = None
    objects_detected: List[str]
    alert: bool
    capture_path: Optional[str] = None
