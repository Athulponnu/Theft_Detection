from ultralytics import YOLO
import cv2

# Load the YOLOv8-Pose model from your models folder
model = YOLO("models/yolov8n-pose.pt")

# Open webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run pose detection
    results = model(frame)

    # Draw skeletons
    annotated_frame = results[0].plot()

    cv2.imshow("Pose Detection", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
