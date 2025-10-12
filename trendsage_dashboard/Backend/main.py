from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path

# Import your router
from Backend.routers import logs

app = FastAPI(title="TrendSage API")

# Allow JS frontend to call your API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define base directory (parent of Backend folder)
BASE_DIR = Path(__file__).resolve().parent.parent

# Mount static folders located in root (next to Backend folder)
app.mount("/utils", StaticFiles(directory=BASE_DIR / "utils"), name="utils")
app.mount("/data", StaticFiles(directory=BASE_DIR / "data"), name="data")
app.mount("/components", StaticFiles(directory=BASE_DIR / "components"), name="components")

# Mount captures folders
CAPTURES_KNOWN_DIR = BASE_DIR.parent / "captures" / "known"
CAPTURES_UNKNOWN_DIR = BASE_DIR.parent / "captures" / "unknown"

# Ensure the directories exist
CAPTURES_KNOWN_DIR.mkdir(parents=True, exist_ok=True)
CAPTURES_UNKNOWN_DIR.mkdir(parents=True, exist_ok=True)

app.mount("/captures/known", StaticFiles(directory=CAPTURES_KNOWN_DIR), name="captures_known")
app.mount("/captures/unknown", StaticFiles(directory=CAPTURES_UNKNOWN_DIR), name="captures_unknown")

# Include your API router
app.include_router(logs.router, prefix="/api", tags=["logs"])

print("BASE_DIR:", BASE_DIR)
print("utils folder exists?", (BASE_DIR / "utils").exists())
print("captures/known exists?", CAPTURES_KNOWN_DIR.exists())
print("captures/unknown exists?", CAPTURES_UNKNOWN_DIR.exists())

# Serve the main HTML dashboard at the root route "/"
@app.get("/", response_class=HTMLResponse)
def serve_dashboard():
    index_file = BASE_DIR / "index.html"  # HTML file in root folder
    return index_file.read_text(encoding="utf-8")
