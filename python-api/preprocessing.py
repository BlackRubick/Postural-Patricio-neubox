import cv2
import numpy as np

def preprocess_foot_image(image: np.ndarray, binarization_type='otsu', adaptive_c=10, fixed_threshold=120, invert=True):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = image.shape[:2]
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    if binarization_type == 'adaptive':
        binary = cv2.adaptiveThreshold(
            blur, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=35,
            C=int(adaptive_c)
        )
    elif binarization_type == 'fixed':
        _, binary = cv2.threshold(blur, int(fixed_threshold), 255, cv2.THRESH_BINARY)
    else:
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    if invert:
        binary = cv2.bitwise_not(binary)
    else:
        if np.sum(binary == 255) > np.sum(binary == 0):
            binary = cv2.bitwise_not(binary)

    # Scale morphological kernel to image size to work correctly at any resolution
    k_size = max(3, int(min(h, w) * 0.007) | 1)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_size, k_size))
    clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel, iterations=1)
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE, kernel, iterations=2)
    edges = cv2.Canny(clean, 50, 150)
    return {
        "gray": gray,
        "binary": binary,
        "clean": clean,
        "edges": edges,
    }
