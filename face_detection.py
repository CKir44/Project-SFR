import cv2
import numpy as np
import mediapipe as mp
import time
import os
from datetime import datetime
import face_recognition
import requests

# --------------------------- SETUP ---------------------------

# Nextcloud Configuration for cloud saving
# NEXTCLOUD_URL = ""
# NEXTCLOUD_USERNAME = ""
# NEXTCLOUD_APP_PASSWORD = ""

# Function to upload video to Nextcloud
'''
def upload_to_nextcloud(file_path):
    with open(file_path, "rb") as file:
        response = requests.put(
            NEXTCLOUD_URL + "recorded_video.mp4",
            auth=(NEXTCLOUD_USERNAME, NEXTCLOUD_APP_PASSWORD),
            data=file
        )
        if response.status_code in [201, 204]:
            print("✅ Video uploaded successfully to Nextcloud.")
        else:
            print(f"❌ Upload failed: {response.status_code}, {response.text}")
'''

os.makedirs("recordings", exist_ok=True)
os.makedirs("headshots", exist_ok=True)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

RECORDINGS_DIR = "recordings"
os.makedirs(RECORDINGS_DIR, exist_ok=True)

HEADSHOTS_FOLDER = "opencv_env/headshots/"
known_face_encodings = []
known_face_names = []

# Timed face recognition
face_check_interval = 30
face_check_duration = 10
face_check_active = False
face_check_start_time = 0

# Load known faces
if os.path.exists(HEADSHOTS_FOLDER):
    for filename in os.listdir(HEADSHOTS_FOLDER):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            image_path = os.path.join(HEADSHOTS_FOLDER, filename)
            image = face_recognition.load_image_file(image_path)
            encodings = face_recognition.face_encodings(image)
            if encodings:
                known_face_encodings.append(encodings[0])
                known_face_names.append("Kirby")
            else:
                print(f"⚠ No face found in {filename}")
else:
    print("⚠ 'headshots/' folder not found. Skipping face recognition setup.")

# Camera setup
cap = cv2.VideoCapture(2)
if not cap.isOpened():
    print("❌ Camera failed to open.")
    exit()
else:
    print("✅ Camera successfully opened.")

frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_filename = os.path.join(RECORDINGS_DIR, f"recorded_video_{timestamp}.mp4")
out = cv2.VideoWriter(output_filename, fourcc, 30.0, (frame_width, frame_height))

zoom_factor = 1.0
zooming_in = False
counter = ""
last_number = None
last_input_time = time.time()
counter_cooldown = 1.5

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame capture failed.")
        break

    current_time = time.time()

    # Timed face recognition activation
    if int(current_time) % face_check_interval == 0:
        face_check_active = True
        face_check_start_time = current_time

    if face_check_active and (current_time - face_check_start_time <= face_check_duration):
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
            if any(matches):
                name = "Kirby"
                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                cv2.putText(frame, f"Face Recognized: {name}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    else:
        face_check_active = False

    # Gesture recognition
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            landmarks = [(lm.x, lm.y) for lm in hand_landmarks.landmark]

            tips_ids = [4, 8, 12, 16, 20]
            raised_fingers = sum(landmarks[tip][1] < landmarks[tip - 2][1] for tip in tips_ids[1:])

            # Closed fist for zoom
            zooming_in = raised_fingers == 0

            # Finger counter logic
            if time.time() - last_input_time > counter_cooldown:
                if raised_fingers in [1, 2, 3, 4, 5] and raised_fingers != last_number:
                    counter += str(raised_fingers)
                    last_input_time = time.time()
                    last_number = raised_fingers

    # Zooming effect
    if zooming_in:
        zoom_factor = min(2.0, zoom_factor + 0.02)
    else:
        zoom_factor = max(1.0, zoom_factor - 0.02)

    h, w, _ = frame.shape
    center_x, center_y = w // 2, h // 2
    new_w, new_h = int(w / zoom_factor), int(h / zoom_factor)
    x1, y1 = center_x - new_w // 2, center_y - new_h // 2
    x2, y2 = center_x + new_w // 2, center_y + new_h // 2
    zoomed_frame = frame[y1:y2, x1:x2]
    zoomed_frame = cv2.resize(zoomed_frame, (w, h))

    # Overlay labels
    if zooming_in:
        cv2.putText(zoomed_frame, "Zooming In", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)
    cv2.putText(zoomed_frame, f"Counter: {counter}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)

    # Show + record
    cv2.imshow("Final Iter - Face + Gesture", zoomed_frame)
    out.write(zoomed_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
cv2.destroyAllWindows()
