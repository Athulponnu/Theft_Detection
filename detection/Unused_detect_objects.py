# person_detect.py � part of detection
# detection/person_detect.py
import cv2


proto = "models/MobileNetSSD_deploy.prototxt"
model = "models/MobileNetSSD_deploy.caffemodel"
net = cv2.dnn.readNetFromCaffe(proto, model)
CLASSES = ["background","aeroplane","bicycle","bird","boat","bottle","bus","car","cat","chair","cow","diningtable","dog","horse","motorbike","person",
           "pottedplant","sheep","sofa","train","tvmonitor"]

# def detect_person(frame, conf_thresh=0.5):
#     (h, w) = frame.shape[:2]
#     blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),0.007843,(300,300),127.5)
#     net.setInput(blob)
#     detections = net.forward()
#     persons = []
#     for i in range(detections.shape[2]):
#         confidence = detections[0,0,i,2]
#         idx = int(detections[0,0,i,1])
#         if confidence > conf_thresh and CLASSES[idx] == "person":
#             box = detections[0,0,i,3:7]*[w,h,w,h]
#             persons.append(box.astype("int"))
#     return persons
def detect_objects(frame, conf_thresh=0.5):
    (h, w) = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(frame,(300,300)),0.007843,(300,300),127.5)
    net.setInput(blob)
    detections = net.forward()
    objects = []
    for i in range(detections.shape[2]):
        confidence = detections[0,0,i,2]
        idx = int(detections[0,0,i,1])
        if confidence > conf_thresh:
            box = detections[0,0,i,3:7]*[w,h,w,h]
            objects.append({"class": CLASSES[idx], "confidence": confidence, "box": box.astype("int")})
    return objects


