
import cv2
import pytesseract
import re

def extract_text_from_image(path):
    result = {
        "path": path,
        "fake": False,
        "reason": []
    }

    img = cv2.imread(path)
    if img is None:
        result["fake"] = True
        result["reason"].append("Unable to read image.")
        return result['fake']

    text = pytesseract.image_to_string(img)

    # Regex patterns for date and time
    date_patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",      # 12/04/2023 or 12-04-2023
        r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b",        # 2023-04-12
        r"\b\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4}",  # 12 Apr 2023
    ]
    time_patterns = [
        r"\b\d{1,2}:\d{2}(:\d{2})?\s*(AM|PM|am|pm)?\b",  # 14:30, 2:30 PM
    ]

    # Combine all regex checks
    for pattern in date_patterns + time_patterns:
        if re.search(pattern, text):
            result["fake"] = True
            result["reason"].append("Date/time detected in image text.")
            break

    return result['fake']
