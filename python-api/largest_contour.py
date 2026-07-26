import cv2
import numpy as np


def _solidity(cnt: np.ndarray) -> float:
    hull_area = cv2.contourArea(cv2.convexHull(cnt))
    return cv2.contourArea(cnt) / (hull_area + 1e-5)


def _is_foot_shaped(cnt: np.ndarray, img_w: int, img_h: int, min_solidity: float = 0.25) -> bool:
    x, y, bw, bh = cv2.boundingRect(cnt)
    aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
    # Feet are roughly oval — reject very thin strips and near-circles
    if not (1.2 < aspect < 5.0):
        return False
    # Reject blobs spanning nearly the full image height (podoscope frame strips)
    if bh > img_h * 0.90:
        return False
    if _solidity(cnt) < min_solidity:
        return False
    return True


def _split_at_midpoint(mask: np.ndarray, min_area_ratio: float = 0.005) -> list:
    """
    Split mask at the vertical midpoint and return the largest contour from each half.
    Used when two feet are fused into one wide blob.
    """
    img_h, img_w = mask.shape[:2]
    img_area = img_h * img_w
    mid = img_w // 2
    results = []
    for x0, x1 in [(0, mid), (mid, img_w)]:
        half = mask.copy()
        half[:, :x0] = 0
        half[:, x1:] = 0
        cnts, _ = cv2.findContours(half, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        cnts = [c for c in cnts if cv2.contourArea(c) > img_area * min_area_ratio]
        if cnts:
            results.append(max(cnts, key=cv2.contourArea))
    return results


def largest_contour(mask: np.ndarray, min_area_ratio: float = 0.002, max_area_ratio: float = 0.85):
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return None
    img_h, img_w = mask.shape[:2]
    img_area = img_h * img_w

    size_ok = [c for c in contours
               if img_area * min_area_ratio < cv2.contourArea(c) < img_area * max_area_ratio]
    if not size_ok:
        return None

    for min_sol in (0.40, 0.30, 0.20, 0.10):
        shaped = [c for c in size_ok
                  if _is_foot_shaped(c, img_w, img_h, min_solidity=min_sol)]
        if shaped:
            return max(shaped, key=cv2.contourArea)

    # Last resort: biggest blob that isn't a full-height strip
    non_strip = [c for c in size_ok
                 if cv2.boundingRect(c)[3] < img_h * 0.75]
    if non_strip:
        return max(non_strip, key=cv2.contourArea)
    return max(size_ok, key=cv2.contourArea)


def foot_contours(
    mask: np.ndarray,
    max_n: int = 2,
    min_area_ratio: float = 0.002,
    max_area_ratio: float = 0.55,
) -> list:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return []

    img_h, img_w = mask.shape[:2]
    img_area = img_h * img_w
    min_area = img_area * min_area_ratio
    max_area = img_area * max_area_ratio

    size_ok = [c for c in contours if min_area < cv2.contourArea(c) < max_area]

    # If a single oversized blob exists, try splitting it
    if not size_ok:
        big = [c for c in contours
               if img_area * max_area_ratio <= cv2.contourArea(c) < img_area * 0.95]
        if big:
            halves = _split_at_midpoint(mask, min_area_ratio)
            if halves:
                halves.sort(key=lambda c: cv2.boundingRect(c)[0])
                return halves
        return []

    # Remove full-height strips from candidates
    size_ok = [c for c in size_ok if cv2.boundingRect(c)[3] < img_h * 0.75]
    if not size_ok:
        return []

    # Try progressively relaxed shape filters
    candidates = []
    for min_sol in (0.40, 0.30, 0.20, 0.10):
        candidates = [c for c in size_ok
                      if _is_foot_shaped(c, img_w, img_h, min_solidity=min_sol)]
        if candidates:
            break
    if not candidates:
        candidates = size_ok

    candidates.sort(key=cv2.contourArea, reverse=True)
    selected = candidates[:max_n]

    # If 1 very wide blob, try to split it
    if len(selected) == 1:
        x, y, bw, bh = cv2.boundingRect(selected[0])
        if bw > img_w * 0.50:
            halves = _split_at_midpoint(mask, min_area_ratio)
            if len(halves) == 2:
                selected = halves

    # Validate foot pair
    if len(selected) == 2:
        a0 = cv2.contourArea(selected[0])
        a1 = cv2.contourArea(selected[1])
        if max(a0, a1) / (min(a0, a1) + 1e-5) > 5.0:
            selected = [selected[0]]
        else:
            rects = [cv2.boundingRect(c) for c in selected]
            cx = [r[0] + r[2] / 2 for r in rects]
            cy = [r[1] + r[3] / 2 for r in rects]
            if abs(cy[0] - cy[1]) > abs(cx[0] - cx[1]) * 2.0:
                selected = [selected[0]]

    selected.sort(key=lambda c: cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] / 2)
    return selected
