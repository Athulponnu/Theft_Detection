# annotate_items.py
import cv2
import json
import os
import numpy as np

IMG_PATH = "reference.jpg"   # put your reference image here
OUT_JSON = "items.json"

if not os.path.exists(IMG_PATH):
    print(f"Place an image named {IMG_PATH} in the script folder and re-run.")
    exit(1)

img = cv2.imread(IMG_PATH)
display = img.copy()
h, w = img.shape[:2]

polygons = []
current = []
items = []

mode_text = "LEFT-click: add point | r: finish polygon | n: name & save polygon | s: save all | q: quit"

def mouse_cb(event, x, y, flags, param):
    global current, display
    if event == cv2.EVENT_LBUTTONDOWN:
        current.append((x,y))
        # draw small circle
        cv2.circle(display, (x,y), 4, (0,255,0), -1)
    elif event == cv2.EVENT_RBUTTONDOWN:
        # remove last point
        if current:
            current.pop()
            # redraw
            display = img.copy()
            for poly in polygons:
                cv2.polylines(display, [np.array(poly, dtype=np.int32)], True, (0,0,255), 2)
            for p in current:
                cv2.circle(display, p, 4, (0,255,0), -1)

cv2.namedWindow("Annotator")
cv2.setMouseCallback("Annotator", mouse_cb)

while True:
    tmp = display.copy()
    # draw current polygon lines
    if len(current) >= 2:
        pts = np.array(current, dtype=np.int32)
        cv2.polylines(tmp, [pts], False, (0,255,255), 2)
    # draw finished polygons with their labels
    for it in items:
        pts = np.array(it["poly"], dtype=np.int32)
        cv2.polylines(tmp, [pts], True, (0,0,255), 2)
        # label center
        cx = int(sum([p[0] for p in it["poly"]]) / len(it["poly"]))
        cy = int(sum([p[1] for p in it["poly"]]) / len(it["poly"]))
        cv2.putText(tmp, it["name"], (cx+5, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

    cv2.putText(tmp, mode_text, (10, h-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
    cv2.imshow("Annotator", tmp)
    key = cv2.waitKey(20) & 0xFF

    if key == ord('r'):  # finish polygon (needs >=3)
        if len(current) >= 3:
            polygons.append(current.copy())
            current = []
            display = img.copy()
        else:
            print("Polygon needs at least 3 points.")
    elif key == ord('n'):  # name last polygon and commit to items
        if polygons:
            name = input("Enter name for last polygon: ").strip()
            if not name:
                name = f"item_{len(items)+1}"
            items.append({"name": name, "poly": polygons[-1]})
            polygons.pop()  # consumed
            display = img.copy()
        else:
            print("No finished polygon to name. Press 'r' first.")
    elif key == ord('s'):  # save all to json
        with open(OUT_JSON, "w") as f:
            json.dump({"ref_size": {"w": w, "h": h}, "items": items}, f, indent=2)
        print(f"Saved {len(items)} items to {OUT_JSON}")
    elif key == ord('q'):
        break

cv2.destroyAllWindows()
