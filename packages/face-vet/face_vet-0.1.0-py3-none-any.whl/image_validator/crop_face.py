import cv2
def crop_face(image_path, cascade_path='image_validator/image_validator/models/haarcascade_frontalface_alt2.xml'):
    img = cv2.imread(image_path)
    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    face_cascade = cv2.CascadeClassifier(cascade_path)

    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    if len(faces) == 0:
        return None

    # Crop largest face
    x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
    face_crop = img[y:y + h, x:x + w]
    return face_crop
