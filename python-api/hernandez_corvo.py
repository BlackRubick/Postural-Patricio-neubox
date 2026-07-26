import cv2
import numpy as np
from dataclasses import dataclass
from typing import Tuple


def normalize_vector(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


@dataclass
class HCResult:
    index: float
    x_width: float
    y_width: float
    classification: str
    anterior_point: Tuple[int, int]
    posterior_point: Tuple[int, int]


def classify_plantar_index(index_value: float) -> str:
    """
    Hernández-Corvo plantar index: (X - Y) / X × 100
    where X = forefoot max width, Y = arch min width.
    Low index → arch is wide relative to forefoot → flat foot.
    High index → arch is very narrow → cavus foot.

    Standard classification (Hernández Corvo, 1987):
      0 – 34  : Pie plano
      35 – 39 : Pie plano-normal
      40 – 54 : Pie normal
      55 – 59 : Pie cavo-normal
      60 – 74 : Pie cavo
      ≥ 75    : Pie cavo fuerte
    """
    if index_value < 35:
        return "Pie plano"
    elif index_value < 40:
        return "Pie plano-normal"
    elif index_value < 55:
        return "Pie normal"
    elif index_value < 60:
        return "Pie cavo-normal"
    elif index_value < 75:
        return "Pie cavo"
    else:
        return "Pie cavo fuerte"


def _principal_axis_from_contour(contour: np.ndarray):
    pts = contour.reshape(-1, 2).astype(np.float32)
    mean, eigenvectors, _ = cv2.PCACompute2(pts, mean=None)
    center = mean[0]
    axis = normalize_vector(eigenvectors[0])
    projections = np.dot(pts - center, axis)
    posterior = tuple(pts[int(np.argmin(projections))].astype(int))
    anterior  = tuple(pts[int(np.argmax(projections))].astype(int))
    return center, axis, posterior, anterior


def _smooth_widths(widths: np.ndarray, window: int = 5) -> np.ndarray:
    """Moving-average smoothing to reduce pixel-level noise in the width profile."""
    if len(widths) < window:
        return widths
    return np.convolve(widths, np.ones(window) / window, mode='same')


def _measure_widths_rotated(
    mask: np.ndarray,
    center: np.ndarray,
    axis: np.ndarray,
    posterior: tuple,
):
    """
    Rotate the (single-foot) mask so the foot axis is vertical, then measure
    row-wise widths to compute the Hernández-Corvo X and Y values.

    HC requires the forefoot (toes + ball) at the TOP of the rotated image so
    that zone 0-40 % captures the widest part (metatarsal heads).  We resolve
    the PCA eigenvector ambiguity by checking where the *posterior* point
    (heel) lands after rotation: if it is in the top half we flip 180°.
    """
    angle = np.degrees(np.arctan2(axis[1], axis[0]))
    h, w = mask.shape[:2]
    rot_mat = cv2.getRotationMatrix2D((float(center[0]), float(center[1])), angle - 90.0, 1.0)
    rotated = cv2.warpAffine(mask, rot_mat, (w, h), flags=cv2.INTER_NEAREST)

    ys, xs = np.where(rotated > 0)
    if len(xs) == 0:
        raise ValueError("No hay píxeles válidos tras la rotación")

    y_min, y_max = int(np.min(ys)), int(np.max(ys))
    x_min, x_max = int(np.min(xs)), int(np.max(xs))

    # Check orientation: if the heel (posterior point) is in the top half of
    # the rotated foot, the foot is upside-down (toes at bottom) → flip 180°.
    post_rot = cv2.transform(
        np.array([[[float(posterior[0]), float(posterior[1])]]], dtype=np.float32),
        rot_mat,
    )[0][0]
    y_mid = (y_min + y_max) / 2.0
    if float(post_rot[1]) < y_mid:
        rot_mat = cv2.getRotationMatrix2D(
            (float(center[0]), float(center[1])), angle + 90.0, 1.0
        )
        rotated = cv2.warpAffine(mask, rot_mat, (w, h), flags=cv2.INTER_NEAREST)
        ys, xs = np.where(rotated > 0)
        y_min, y_max = int(np.min(ys)), int(np.max(ys))
        x_min, x_max = int(np.min(xs)), int(np.max(xs))

    roi = rotated[y_min: y_max + 1, x_min: x_max + 1]
    raw_widths = np.sum(roi > 0, axis=1).astype(float)
    n_rows = len(raw_widths)
    if n_rows < 10:
        raise ValueError("Máscara insuficiente para medir anchos")

    # Smooth to reduce noise spikes (window ≈ 5% of foot length)
    widths = _smooth_widths(raw_widths, window=max(3, n_rows // 20))

    # Hernández-Corvo zones:
    #   Forefoot (antepié):  0 – 40 % of length
    #   Arch (mediopié):    40 – 75 % of length
    fore_s, fore_e = 0,              max(1, int(0.40 * n_rows))
    arch_s, arch_e = int(0.40 * n_rows), max(int(0.75 * n_rows), int(0.40 * n_rows) + 1)

    fore_region = widths[fore_s:fore_e]
    arch_region = widths[arch_s:arch_e]

    if len(fore_region) == 0 or len(arch_region) == 0:
        raise ValueError("Zonas de medición vacías")

    # 90th-percentile for forefoot (robust against edge noise)
    x_width = float(np.percentile(fore_region, 90))
    # 15th-percentile for arch (robust against filled pixels from morphology)
    y_width = float(np.percentile(arch_region, 15))

    x_row = y_min + fore_s + int(np.argmax(fore_region))
    y_row = y_min + arch_s + int(np.argmin(arch_region))

    return {
        "rotated": rotated,
        "rot_mat": rot_mat,
        "x_width": x_width,
        "y_width": y_width,
        "x_row":   x_row,
        "y_row":   y_row,
        "x_min":   x_min,
        "x_max":   x_max,
    }


def apply_hernandez_corvo(mask: np.ndarray, contour: np.ndarray):
    """
    Compute the Hernández-Corvo plantar index for a single foot.

    IMPORTANT: `mask` must already be restricted to this foot only
    (i.e. a per-foot mask, not the full image mask with both feet).
    """
    center, axis, posterior, anterior = _principal_axis_from_contour(contour)
    widths_info = _measure_widths_rotated(mask, center, axis, posterior)

    x_width = widths_info["x_width"]
    y_width = widths_info["y_width"]
    if x_width <= 0:
        raise ValueError("Ancho del antepié es cero; no se pudo medir")

    index_value = (x_width - y_width) / x_width * 100
    classification = classify_plantar_index(index_value)

    return HCResult(
        index=index_value,
        x_width=x_width,
        y_width=y_width,
        classification=classification,
        anterior_point=anterior,
        posterior_point=posterior,
    ), widths_info
