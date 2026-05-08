# Like face_detect but with a more elaborate model that detects the face gestures
import os

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

mod_path = "face_landmarker_v2_with_blendshapes.task"

if not os.path.exists(mod_path):
    os.system(f"wget -O {mod_path} https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker_v2_with_blendshapes/int8/1/face_landmarker_v2_with_blendshapes.task")

# config the landmarker
base_options = python.BaseOptions(model_asset_path=mod_path)
options = vision.FaceLandmarkerOptions(
    base_options = base_options,
    output_face_blendshapes = True,
    num_faces = 1 # Should worry about this later. Depends on how many faces are in the frame.
)
detector = vision.FaceLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    sucess, frame = cap.read()
    if not sucess: break

    # Mediapipe format
    rgb_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_img)

    # Detect
    result = detector.detect(mp_image)

    # Visualization
    if result.face_landmarks:
        for face_landmarks in result.face_landmarks:
            for landmark in face_landmarks:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])
                cv2.circle(frame, (x, y), 1, (0, 255, 0), -1)

    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == 27: break

detector.close()
cap.release()
cv2.destroyAllWindows()
