import os
import cv2

def crop_face(image_path):
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Construct absolute path to the Haar cascade XML file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cascade_path = os.path.join(base_dir, 'models', 'haarcascade_frontalface_alt2.xml')

    if not os.path.exists(cascade_path):
        raise FileNotFoundError(f"Haar cascade file not found at: {cascade_path}")

    face_cascade = cv2.CascadeClassifier(cascade_path)

    faces = face_cascade.detectMultiScale(gray, 1.1, 4)

    if len(faces) == 0:
        return None

    # Crop largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_crop = img[y:y + h, x:x + w]
    return face_crop
