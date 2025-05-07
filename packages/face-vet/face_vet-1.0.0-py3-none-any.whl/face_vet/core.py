# face_vet/core.py
from .face_detection import check_face_detection
from .image_quality_check import checj_image_quality
from .text_extraction import extract_text_from_image
from .eye_nose_distance_detection import eye_nose_distance
from .crop_face import crop_face


def analyze_image(image_path):
    result = {
        "is_fake": False,
        "reasons": ""
    }

    if not check_face_detection(image_path):
        result["is_fake"] = True
        result["reasons"]+="No face detected"
        return result
    
    if extract_text_from_image(image_path):
        result["is_fake"] = True
        result["reasons"]+="Date/time detected in image text."
        return result

    face_crop = crop_face(image_path)
    if eye_nose_distance(face_crop):
        result["is_fake"] = True
        result["reasons"]+="Fake image detected based on eye-nose distance."
        return result
    
    if checj_image_quality(image_path):
        result["is_fake"] = True
        result["reasons"]+="image quality is bad"
        return result
    
    result.update({"is_fake": False, "reasons": "No issues detected"})
    return result
