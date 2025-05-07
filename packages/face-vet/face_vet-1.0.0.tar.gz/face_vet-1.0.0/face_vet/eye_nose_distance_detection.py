# import cv2
# import dlib
# import numpy as np

# # Load predictor once (optional optimization)
# predictor = dlib.shape_predictor("face_vet/face_vet/models/shape_predictor_68_face_landmarks.dat")
# detector = dlib.get_frontal_face_detector()

# def eye_nose_distance(image_array):
#     if image_array is None:
#         return False

#     gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

#     # Detect faces
#     faces = detector(gray)

#     if len(faces) == 0:
#         return False

#     # Use first detected face
#     landmarks = predictor(gray, faces[0])

#     # Eye and nose coordinates
#     left_eye = (landmarks.part(36).x, landmarks.part(36).y)
#     right_eye = (landmarks.part(45).x, landmarks.part(45).y)
#     nose = (landmarks.part(30).x, landmarks.part(30).y)

#     # Distances
#     left_eye_distance = np.linalg.norm(np.array(left_eye) - np.array(nose))
#     right_eye_distance = np.linalg.norm(np.array(right_eye) - np.array(nose))

#     # Return True if suspiciously short distances (e.g., fake image)
#     if left_eye_distance < 80 or right_eye_distance < 80:
#         return True
#     return False
import os
import cv2
import dlib
import numpy as np

# Construct absolute path to the model file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "shape_predictor_68_face_landmarks.dat")

# Load the face detector and shape predictor
predictor = dlib.shape_predictor(MODEL_PATH)
detector = dlib.get_frontal_face_detector()

def eye_nose_distance(image_array):
    if image_array is None:
        return False

    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)

    if len(faces) == 0:
        return False

    # Use the first detected face
    landmarks = predictor(gray, faces[0])

    # Get coordinates for eyes and nose
    left_eye = (landmarks.part(36).x, landmarks.part(36).y)
    right_eye = (landmarks.part(45).x, landmarks.part(45).y)
    nose = (landmarks.part(30).x, landmarks.part(30).y)

    # Calculate distances
    left_eye_distance = np.linalg.norm(np.array(left_eye) - np.array(nose))
    right_eye_distance = np.linalg.norm(np.array(right_eye) - np.array(nose))

    # Return True if distances are unusually short (e.g., might be fake or low-quality image)
    if left_eye_distance < 80 or right_eye_distance < 80:
        return True

    return False
