# capture.py � part of camera
# camera/capture.py
import cv2

cap = cv2.VideoCapture(0)

def get_frame():
    ret, frame = cap.read()
    return frame
