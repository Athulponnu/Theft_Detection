# main.py - IoT Theft Detection with YOLO + Face Recognition + Pose Detection + Restricted Area + Microphone

import cv2
import time
import os
import numpy as np
from ultralytics import YOLO
import sounddevice as sd
from detection.face_recognize import recognize_faces
from alerts.telegram import send_telegram_alert
from utils.logger import log_event
import serial
import time
import winsound 
# -----------------------------
# Sound detection parameters
# -----------------------------
SOUND_THRESHOLD = 0.2  # Adjust based on mic sensitivity
DURATION = 0.1         # seconds to sample per frame


arduino = serial.Serial('COM5', 9600, timeout=1)
time.sleep(2)  # wait for NodeMCU to initialize

def detect_sound_from_arduino():
    if arduino.in_waiting > 0:
        try:
            line = arduino.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"[Serial] {line}")
            return line == "SOUND"
        except Exception as e:
            print("[ERROR] Serial read failed:", e)
    return False



# def detect_sound():
#     """Return True if sound exceeds threshold"""
#     try:
#         audio = sd.rec(int(DURATION * 44100), samplerate=44100, channels=1, blocking=True)
#         peak = np.abs(audio).max()
#         return peak > SOUND_THRESHOLD
#     except:
#         return False

# -----------------------------
# Load YOLO models
# -----------------------------
MODEL_PATH = "models/Training_model/yolov8n.pt"
POSE_MODEL_PATH = "models/yolov8n-pose.pt"

yolo = YOLO(MODEL_PATH)
pose_model = YOLO(POSE_MODEL_PATH)

os.makedirs("captures/known", exist_ok=True)
os.makedirs("captures/unknown", exist_ok=True)

# -----------------------------
# Restricted area
# -----------------------------
restricted_area = [(100, 200), (500, 200), (500, 400), (100, 400)]
def point_in_polygon(point, polygon):
    return cv2.pointPolygonTest(np.array(polygon, np.int32), point, False) >= 0

def main():
    print("[INFO] 🚀 IoT Theft Detection started with microphone input. Press 'q' to quit.")
    cap = cv2.VideoCapture(0)
    last_log_time = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            if time.time() - last_log_time >= 3:
                print("[WARN] ⚠️ No frame captured.")
                last_log_time = time.time()
            continue

        # -----------------------------
        # Draw restricted area
        # -----------------------------
        pts = np.array(restricted_area, np.int32).reshape((-1,1,2))
        cv2.polylines(frame, [pts], isClosed=True, color=(0,0,255), thickness=2)
        cv2.putText(frame, "Restricted Area", (restricted_area[0][0], restricted_area[0][1]-10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

        # -----------------------------
        # YOLO object detection
        # -----------------------------
        results = yolo(frame, conf=0.5)
        objects = []
        persons = []
        for r in results:
            for box in r.boxes:
                cls_id = int(box.cls[0])
                cls_name = yolo.names[cls_id]
                conf = float(box.conf[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                obj = {"class": cls_name, "confidence": conf, "box": (x1, y1, x2, y2)}
                objects.append(obj)
                if cls_name == "person":
                    persons.append(obj)

                cv2.rectangle(frame, (x1,y1),(x2,y2),(255,0,0),2)
                cv2.putText(frame, f"{cls_name} {conf:.2f}", (x1,y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0),2)

        # -----------------------------
        # Face recognition
        # -----------------------------
        face_results = recognize_faces(frame) if persons else []

        # -----------------------------
        # Pose detection
        # -----------------------------
        hand_in_restricted_area = False
        if persons:
            pose_results = pose_model(frame)
            if pose_results:
                frame = pose_results[0].plot()
                for person in pose_results:
                    keypoints = person.keypoints
                    num_keypoints = keypoints.shape[0]
                    for idx in [9,10]:  # wrists
                        if idx >= num_keypoints:
                            continue
                        x,y,conf = keypoints[idx]
                        if conf > 0.3:
                            hand_point = (int(x),int(y))
                            cv2.circle(frame, hand_point, 24, (0,255,255), -1)
                            if point_in_polygon(hand_point, restricted_area):
                                hand_in_restricted_area = True
                                cv2.putText(frame, "⚠️ HAND IN RESTRICTED AREA!",
                                            (hand_point[0]+10, hand_point[1]),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255),2)

        # -----------------------------
        # Microphone sound detection
        # -----------------------------
        sound_detected = detect_sound_from_arduino()
        # sound_detected = detect_sound_from_arduino()
        if sound_detected:
            print("[INFO] 🔊 Sound detected!")
            # winsound.Beep(1000, 500)

        # -----------------------------
        # Trigger alert if both hand in restricted area AND sound detected
        # -----------------------------
        if hand_in_restricted_area and sound_detected:
            print("[ALERT] 🚨 Intrusion with sound detected!")
            alert_path = f"captures/alert_{int(time.time())}.jpg"
            cv2.imwrite(alert_path, frame)
            send_telegram_alert(alert_path, "🚨 Intruder detected with sound!")
            log_event(face=None, objects=[obj["class"] for obj in objects], alerts=True, capture_path=alert_path)

        # -----------------------------
        # Log detections every 3 sec
        # -----------------------------
        if time.time() - last_log_time >= 3:
            if persons:
                print(f"[INFO] 🧍 Persons detected: {len(persons)}, Faces recognized: {len(face_results)}")
            elif objects:
                detected_classes = [obj["class"] for obj in objects]
                print(f"[INFO] 🔎 No person, but detected: {', '.join(detected_classes)}")
            else:
                print("[INFO] ❌ No objects detected.")
            last_log_time = time.time()

        # -----------------------------
        # Draw face results
        # -----------------------------
        for name, loc in face_results:
            if loc is None or len(loc)!=4:
                continue
            top,right,bottom,left = loc
            label = name if name else "Unknown"
            color = (0,255,0) if label!="Unknown" else (0,0,255)
            cv2.rectangle(frame, (left,top),(right,bottom),color,2)
            y_label = max(top-10,10)
            (text_w,text_h),_ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX,0.8,2)
            cv2.rectangle(frame,(left,y_label-text_h-2),(left+text_w,y_label+2),color,-1)
            cv2.putText(frame,label,(left,y_label),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)

        # -----------------------------
        # Show live video
        # -----------------------------
        cv2.imshow("IoT Theft Detection + Pose + Mic", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print("[INFO] 👋 Exiting program...")
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
