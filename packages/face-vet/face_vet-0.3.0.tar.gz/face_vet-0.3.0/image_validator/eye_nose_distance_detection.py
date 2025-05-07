import cv2
import dlib
import numpy as np

# Load predictor once (optional optimization)
predictor = dlib.shape_predictor("image_validator/image_validator/models/shape_predictor_68_face_landmarks.dat")
detector = dlib.get_frontal_face_detector()

def eye_nose_distance(image_array):
    if image_array is None:
        return "No image provided"

    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = detector(gray)

    if len(faces) == 0:
        return "No face detected"

    # Use first detected face
    landmarks = predictor(gray, faces[0])

    # Eye and nose coordinates
    left_eye = (landmarks.part(36).x, landmarks.part(36).y)
    right_eye = (landmarks.part(45).x, landmarks.part(45).y)
    nose = (landmarks.part(30).x, landmarks.part(30).y)

    # Distances
    left_eye_distance = np.linalg.norm(np.array(left_eye) - np.array(nose))
    right_eye_distance = np.linalg.norm(np.array(right_eye) - np.array(nose))

    # Return True if suspiciously short distances (e.g., fake image)
    if left_eye_distance < 80 or right_eye_distance < 80:
        return True
    return False
