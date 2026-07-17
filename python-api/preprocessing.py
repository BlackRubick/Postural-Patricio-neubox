import cv2
import numpy as np


def _score_closed(closed: np.ndarray, img_area: int) -> float:
    """Score an already-closed binary — no extra morphology."""
    white_pct = np.mean(closed == 255)
    cnts, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    img_h = closed.shape[0]
    valid = []
    for c in cnts:
        area = cv2.contourArea(c)
        ratio = area / img_area
        if not (0.002 < ratio < 0.55):
            continue
        x, y, bw, bh = cv2.boundingRect(c)
        if not (1.1 < max(bw, bh) / (min(bw, bh) + 1e-5) < 5.5):
            continue
        if bh > img_h * 0.78:          # reject full-height strips
            continue
        hull = cv2.contourArea(cv2.convexHull(c))
        if area / (hull + 1e-5) < 0.18:
            continue
        valid.append((ratio, area / (hull + 1e-5)))
    if not valid:
        return 0.0
    base = sum(r * s for r, s in valid)
    pair = 0.0
    if len(valid) >= 2:
        rs = sorted(r for r, _ in valid)[-2:]
        pair = (rs[0] / (rs[1] + 1e-5)) * 0.5
    bg_pen = max(0.0, white_pct - 0.45) * 2.0
    return (base + pair) * max(0.1, 1.0 - bg_pen)


def _close_open(mask, ker_lg, ker_sm, n=3):
    out = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ker_lg, iterations=n)
    out = cv2.morphologyEx(out,  cv2.MORPH_OPEN,  ker_sm, iterations=1)
    return out


def _post_strip(mask, left, right, top, bottom):
    """Strip applied AFTER close, so dilation cannot undo it."""
    out = mask.copy()
    out[:top, :]     = 0
    out[-bottom:, :] = 0
    out[:, :left]    = 0
    out[:, -right:]  = 0
    return out


def _bright_vs_dark_bg(gray_uint8: np.ndarray, ker_size: int, iterations: int = 5) -> np.ndarray:
    """
    Detect pixels significantly brighter than the local darkest area.
    Uses morphological erosion as 'local minimum' → robust background estimate.
    Works for any podoscope: feet are always brighter than the dark platform.
    """
    ker = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ker_size, ker_size))
    # Local minimum = background. More iterations → erosion passes through larger feet.
    bg = cv2.erode(gray_uint8, ker, iterations=iterations)
    above = np.clip(gray_uint8.astype(np.int32) - bg.astype(np.int32), 0, 255).astype(np.uint8)
    return above


def preprocess_foot_image(
    image: np.ndarray,
    binarization_type: str = 'otsu',
    adaptive_c: int = 10,
    fixed_threshold: int = 120,
    invert: bool = True,
) -> dict:
    h, w = image.shape[:2]
    dim = min(h, w)

    k_sm = max(3, int(dim * 0.006) | 1)
    k_lg = max(15, int(dim * 0.038) | 1)
    ker_sm = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_sm, k_sm))
    ker_lg = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_lg, k_lg))

    # CLAHE for equalized gray
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l_ch, a_ch, b_ch_lab = cv2.split(lab)
    clahe    = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    image_eq = cv2.cvtColor(cv2.merge([clahe.apply(l_ch), a_ch, b_ch_lab]),
                            cv2.COLOR_LAB2BGR)
    gray     = cv2.cvtColor(image_eq, cv2.COLOR_BGR2GRAY)
    gray_raw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Post-close strip sizes — must exceed (edge_width + k_lg * n_close / 2)
    # so that edge artifacts can't survive dilation expansion.
    # Edge strip ≈ 130px; expansion ≈ 41 * 3 = 123px → need > 253px → use 14% width
    pl = max(20, int(w * 0.14))
    pr = max(20, int(w * 0.04))
    pt = max(10, int(h * 0.03))
    pb = max(10, int(h * 0.03))

    img_area = h * w
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    v_ch = hsv[:, :, 2]
    b_ch = image[:, :, 0].astype(np.float32)
    g_ch = image[:, :, 1].astype(np.float32)
    r_ch = image[:, :, 2].astype(np.float32)

    candidates: list[tuple[float, np.ndarray]] = []

    def add(raw):
        if np.mean(raw == 255) > 0.55:
            raw = cv2.bitwise_not(raw)
        closed = _close_open(raw, ker_lg, ker_sm)
        stripped = _post_strip(closed, pl, pr, pt, pb)
        sc = _score_closed(stripped, img_area)
        candidates.append((sc, stripped))

    if binarization_type == 'otsu':
        # ── 1. Percentile threshold on V (brightness) — guaranteed coverage ──
        # "The top N% brightest pixels are the feet" works for any podoscope.
        for pct in (75, 80, 84, 87, 90):
            thresh = float(np.percentile(v_ch, pct))
            _, raw = cv2.threshold(v_ch, thresh, 255, cv2.THRESH_BINARY)
            add(raw)

        # ── 2. Bright-vs-dark-background (erosion-based local minimum) ──
        # iterations=5 ensures erosion passes through even large feet (~300px wide)
        bright_ch = _bright_vs_dark_bg(gray_raw, max(51, int(dim * 0.09) | 1),
                                       iterations=5)
        for thresh in (15, 30, 50):
            _, raw = cv2.threshold(bright_ch, thresh, 255, cv2.THRESH_BINARY)
            add(raw)

        # ── 3. HSV wide range — V≥80 keeps out dark background ──────────────
        for lo, hi in [
            (np.array([60, 10, 100]), np.array([130, 255, 255])),
            (np.array([60, 10,  70]), np.array([130, 255, 255])),
            (np.array([50,  5,  50]), np.array([140, 255, 255])),
        ]:
            raw = cv2.inRange(hsv, lo, hi)
            add(raw)

        # ── 4. Multi-channel Otsu / Triangle ─────────────────────────────────
        cyan2 = np.clip(2 * g_ch - r_ch - b_ch, 0, 255).astype(np.uint8)
        for ch in (cyan2, np.clip(g_ch - r_ch, 0, 255).astype(np.uint8),
                   v_ch, gray, gray_raw):
            blur = cv2.GaussianBlur(ch, (7, 7), 0)
            for flag in (cv2.THRESH_BINARY + cv2.THRESH_OTSU,
                         cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE):
                try:
                    _, raw = cv2.threshold(blur, 0, 255, flag)
                except cv2.error:
                    continue
                add(raw)

        # Pick highest-scoring; ties → closest white% to 18% (expected foot area)
        if candidates:
            best_sc = max(sc for sc, _ in candidates)
            if best_sc > 0:
                binary = max(candidates, key=lambda x: x[0])[1]
            else:
                binary = min(candidates,
                             key=lambda x: abs(np.mean(x[1] == 255) - 0.18))[1]
        else:
            _, binary = cv2.threshold(
                cv2.GaussianBlur(gray, (7, 7), 0), 0, 255,
                cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    elif binarization_type == 'adaptive':
        blur = cv2.GaussianBlur(
            cv2.bilateralFilter(gray, 9, 55, 55), (5, 5), 0)
        binary = cv2.adaptiveThreshold(blur, 255,
                     cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                     cv2.THRESH_BINARY, 35, int(adaptive_c))
        if invert:
            binary = cv2.bitwise_not(binary)
        if np.mean(binary == 255) > 0.55:
            binary = cv2.bitwise_not(binary)
    else:
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, binary = cv2.threshold(blur, int(fixed_threshold), 255, cv2.THRESH_BINARY)
        if invert:
            binary = cv2.bitwise_not(binary)
        if np.mean(binary == 255) > 0.55:
            binary = cv2.bitwise_not(binary)

    if np.mean(binary == 255) > 0.55:
        binary = cv2.bitwise_not(binary)

    # Light additional close to seal micro-gaps, then re-strip to be safe
    clean = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, ker_sm, iterations=2)
    clean = _post_strip(clean, pl, pr, pt, pb)
    clean = cv2.morphologyEx(clean, cv2.MORPH_OPEN, ker_sm, iterations=1)

    edges = cv2.Canny(clean, 50, 150)
    return {"gray": gray, "binary": binary, "clean": clean, "edges": edges}
