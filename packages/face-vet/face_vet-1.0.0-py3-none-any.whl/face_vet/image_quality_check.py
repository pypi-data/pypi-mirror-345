import cv2
import os

def checj_image_quality(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()
    if variance < 30: 
        print("Image is blurry (variance):", variance)
        return True
    height, width = img.shape[:2]
    if height < 200 or width < 200:
        print("Image too small:", height, width)
        return True
    file_size = os.path.getsize(image_path)
    if file_size < 20 * 1024:  
        return True
    return False