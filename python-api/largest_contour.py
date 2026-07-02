import cv2
import numpy as np

def largest_contour(mask: np.ndarray, min_area_ratio: float = 0.01, max_area_ratio: float = 0.8):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    img_h, img_w = mask.shape[:2]
    img_area = img_h * img_w
    min_area = img_area * min_area_ratio
    max_area = img_area * max_area_ratio

    def is_reasonable_foot_shape(cnt):
        x, y, w, h = cv2.boundingRect(cnt)
        long_side = max(w, h)
        short_side = min(w, h)
        aspect = long_side / (short_side + 1e-5)
        # Accept both vertical and horizontal foot orientations
        if not (1.2 < aspect < 4.0):
            return False
        # 5px margin: allows foot to reach near the image edge
        margin = 5
        if x < margin or y < margin or (x + w) > (img_w - margin) or (y + h) > (img_h - margin):
            return False
        return True

    filtered = [c for c in contours if min_area < cv2.contourArea(c) < max_area and is_reasonable_foot_shape(c)]
    if not filtered:
        return None
    # Return the largest contour by area, not by aspect ratio
    return max(filtered, key=cv2.contourArea)
