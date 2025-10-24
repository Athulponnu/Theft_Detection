# theft_skeleton_watch_items.py
import cv2
import mediapipe as mp
import numpy as np
import time
import sqlite3
import os
import json
from datetime import datetime

# ---------- CONFIG ----------
ITEM_JSON = "items.json"        # Annotated items from annotator
DIST_THRESH_PX = 120
VEL_SCALE = 200.0
W_D, W_V, W_C = 0.6, 0.3, 0.1
SCORE_THRESHOLD = 0.6
CONSECUTIVE_FRAMES_REQ = 6
COOLDOWN_SECONDS = 8
SNAP_DIR = "theft_snaps"
DB_PATH = "theft_events.db"
CAM_INDEX = 0
# -----------------------------

os.makedirs(SNAP_DIR, exist_ok=True)

# ---------------------- DB SETUP ----------------------
conn = sqlite3.connect(DB_PATH, check_same_thread=False)
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS events (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  ts TEXT,
  img_path TEXT,
  score REAL,
  dist_px REAL,
  vel REAL,
  hand TEXT,
  item_name TEXT
)
''')
conn.commit()

# ---------------------- LOAD ANNOTATED ITEMS ----------------------
if not os.path.exists(ITEM_JSON):
    print(f"Missing {ITEM_JSON}. Run annotate_items.py first.")
    exit(1)

with open(ITEM_JSON, "r") as f:
    items_data = json.load(f)

ref_w = items_data.get("ref_size", {}).get("w", 1)
ref_h = items_data.get("ref_size", {}).get("h", 1)
items = items_data.get("items", [])

def scale_poly(poly, scale_x, scale_y):
    return [(int(x*scale_x), int(y*scale_y)) for (x,y) in poly]

# ---------------------- MEDIAPIPE SETUP ----------------------
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(CAM_INDEX)
prev_hand_pos = {'R': None, 'L': None}
prev_time = None
consec_counter = 0
last_trigger_time = 0

# ---------------------- HELPERS ----------------------
def point_to_roi_signed_dist(point, contour):
    return cv2.pointPolygonTest(contour, (float(point[0]), float(point[1])), True)

def save_event_snapshot(frame, score, dist_px, vel, hand_side, item_name):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{SNAP_DIR}/event_{ts}_{hand_side}_{item_name}.jpg"
    cv2.imwrite(filename, frame)
    c.execute("INSERT INTO events (ts, img_path, score, dist_px, vel, hand, item_name) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (ts, filename, float(score), float(dist_px), float(vel), hand_side, item_name))
    conn.commit()
    print(f"[EVENT] saved {filename} score={score:.3f} item={item_name} dist={dist_px:.1f} vel={vel:.1f}")

# ---------------------- MAIN LOOP ----------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break
    fh, fw = frame.shape[:2]
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb)
    now = time.time()
    if prev_time is None:
        prev_time = now

    # Scale item polygons for current frame
    scale_x = fw / ref_w
    scale_y = fh / ref_h
    contours = []
    for it in items:
        scaled = scale_poly(it["poly"], scale_x, scale_y)
        cnt = np.array(scaled, dtype=np.int32).reshape((-1,1,2))
        contours.append({"name": it["name"], "poly": scaled, "cnt": cnt})

    # Draw item ROIs
    for it in contours:
        cv2.polylines(frame, [it["cnt"]], True, (0,0,255), 2)
        cx = int(sum([p[0] for p in it["poly"]]) / len(it["poly"]))
        cy = int(sum([p[1] for p in it["poly"]]) / len(it["poly"]))
        cv2.putText(frame, it["name"], (cx+5, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    max_score_frame = 0.0
    best_details = None
    best_item_for_best_score = None

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        for side, lm_idx in (('R', mp_pose.PoseLandmark.RIGHT_WRIST),
                             ('L', mp_pose.PoseLandmark.LEFT_WRIST)):
            wk = lm[lm_idx]
            if wk.visibility < 0.3:
                continue
            x_px = int(wk.x * fw)
            y_px = int(wk.y * fh)
            hand_pt = (x_px, y_px)
            cv2.circle(frame, hand_pt, 6, (0,255,0), -1)

            # compute score for each item polygon
            for it in contours:
                dist_px = point_to_roi_signed_dist(hand_pt, it["cnt"])
                prev = prev_hand_pos.get(side)
                vel = 0.0
                vel_signed = 0.0
                if prev is not None:
                    dx = hand_pt[0] - prev[0]
                    dy = hand_pt[1] - prev[1]
                    dt = now - prev_time if (now - prev_time) > 1e-6 else 1e-6
                    vel = np.sqrt(dx*dx + dy*dy) / dt
                    prev_dist = point_to_roi_signed_dist(prev, it["cnt"])
                    vel_signed = (dist_px - prev_dist) / dt
                approach_vel = -vel_signed

                d_comp = max(0.0, (DIST_THRESH_PX - dist_px) / DIST_THRESH_PX)
                v_comp = max(0.0, min(1.0, approach_vel / VEL_SCALE))
                c_comp = wk.visibility

                score = W_D * d_comp + W_V * v_comp + W_C * c_comp

                # Only consider scores if hand is inside or very close to polygon
                if dist_px >= 0 and score > max_score_frame:
                    max_score_frame = score
                    best_details = (side, score, dist_px, approach_vel)
                    best_item_for_best_score = it["name"]

            prev_hand_pos[side] = hand_pt

    # consecutive frame check for trigger
    if max_score_frame > SCORE_THRESHOLD:
        consec_counter += 1
    else:
        consec_counter = 0

    # Trigger only when hand is inside or approaching object
    if consec_counter >= CONSECUTIVE_FRAMES_REQ and (time.time() - last_trigger_time) > COOLDOWN_SECONDS and best_details is not None:
        side, sc, dist_px, approach_vel = best_details
        item_name = best_item_for_best_score or "unknown"
        save_event_snapshot(frame, sc, dist_px, approach_vel, side, item_name)
        last_trigger_time = time.time()
        consec_counter = 0

    cv2.putText(frame, f"max_score:{max_score_frame:.2f} consec:{consec_counter}", (10,30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,255), 2)

    cv2.imshow("Theft Skeleton Watch (items)", frame)
    prev_time = now
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC to exit
        break

cap.release()
cv2.destroyAllWindows()
conn.close()
