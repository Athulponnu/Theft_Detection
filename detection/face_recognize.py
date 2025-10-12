# face_recognize.py � part of detection
# detection/face_recognize.py
import face_recognition, os, cv2

known_encodings = []
known_names = []

def load_known_faces():
    global known_encodings, known_names
    for file in os.listdir("known_faces"):
        path = os.path.join("known_faces", file)
        image = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(image)
        if enc:
            known_encodings.append(enc[0])
            known_names.append(file.split(".")[0])

load_known_faces()

def recognize_faces(frame):
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locs = face_recognition.face_locations(rgb)
    encs = face_recognition.face_encodings(rgb, face_locs)
    results = []
    for enc, loc in zip(encs, face_locs):
        matches = face_recognition.compare_faces(known_encodings, enc, tolerance=0.5)
        name = "Unknown"
        if True in matches:
            name = known_names[matches.index(True)]
        results.append((name, loc))
    return results
