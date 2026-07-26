from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import base64
from hernandez_corvo import apply_hernandez_corvo
from fastapi.middleware.cors import CORSMiddleware
from knee_api import router as knee_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(knee_router)

# Colors: left=green, right=magenta
_FOOT_COLORS = [(0, 200, 120), (200, 60, 200)]
_FOOT_TINTS  = [(0, 180, 100), (180, 40, 180)]


def _put_label(img, text, pos, scale=0.55, color=(255, 255, 255), thickness=1):
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x, y = pos
    cv2.rectangle(img, (x - 3, y - th - 4), (x + tw + 3, y + baseline), (20, 20, 20), cv2.FILLED)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _draw_circle(img, pt, r=6, color=(255, 255, 0), thickness=2):
    cv2.circle(img, pt, r + 2, (20, 20, 20), -1)
    cv2.circle(img, pt, r, color, thickness)


def _detect_podoscope_feet(img: np.ndarray) -> list:
    """
    Detects up to two foot contours in a podoscope image.

    Handles any spatial arrangement (side-by-side OR stacked top-bottom)
    by finding the two largest colored blobs without splitting the image
    at a fixed axis.  A moderate MORPH_CLOSE (smaller than the inter-foot
    gap) fills the arch gap within each foot without fusing two feet that
    are close together.
    """
    h, w = img.shape[:2]
    dim = min(h, w)
    img_area = h * w

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    s_ch = hsv[:, :, 1]
    v_ch = hsv[:, :, 2]

    # Moderate close: fills arch gap (~20-40 px) but usually won't bridge
    # the gap between two feet (typically 80+ px).
    k_close = max(15, int(dim * 0.022)) | 1
    k_open  = max(5,  int(dim * 0.007)) | 1
    ker_close = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_close, k_close))
    ker_open  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k_open,  k_open))
    border   = max(5, int(dim * 0.01))
    min_area = img_area * 0.02
    max_area = img_area * 0.50

    def _build_mask(s_thresh: int) -> np.ndarray:
        mask = ((s_ch > s_thresh) & (v_ch > 25)).astype(np.uint8) * 255
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, ker_close, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  ker_open,  iterations=1)
        mask[:border, :]  = 0
        mask[-border:, :] = 0
        mask[:, :border]  = 0
        mask[:, -border:] = 0
        return mask

    def _pick_contours(mask: np.ndarray) -> list:
        conts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        result = []
        for c in conts:
            area = cv2.contourArea(c)
            if not (min_area < area < max_area):
                continue
            bx, by, bw, bh = cv2.boundingRect(c)
            # Reject very thin strips (aspect > 7) or near-squares that are too
            # small to be a full foot
            aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
            if aspect > 7.0:
                continue
            # Center must be away from image edges
            cx, cy = bx + bw // 2, by + bh // 2
            if cx < w * 0.03 or cx > w * 0.97:
                continue
            if cy < h * 0.03 or cy > h * 0.97:
                continue
            result.append(c)
        result.sort(key=cv2.contourArea, reverse=True)
        return result[:2]

    def _split_blob(mask: np.ndarray, contour) -> list:
        """Split one large blob along its shortest axis."""
        bx, by, bw, bh = cv2.boundingRect(contour)
        filled = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(filled, [contour], -1, 255, cv2.FILLED)
        halves = []
        if bh >= bw:                       # taller than wide → split horizontally
            mid_y = by + bh // 2
            splits = [(0, mid_y), (mid_y, h)]
            for y0, y1 in splits:
                hm = filled.copy(); hm[:y0, :] = 0; hm[y1:, :] = 0
                cs, _ = cv2.findContours(hm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if cs:
                    halves.append(max(cs, key=cv2.contourArea))
        else:                              # wider than tall → split vertically
            mid_x = bx + bw // 2
            splits = [(0, mid_x), (mid_x, w)]
            for x0, x1 in splits:
                hm = filled.copy(); hm[:, :x0] = 0; hm[:, x1:] = 0
                cs, _ = cv2.findContours(hm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
                if cs:
                    halves.append(max(cs, key=cv2.contourArea))
        return halves if len(halves) == 2 else []

    valid: list = []
    for s_thresh in [80, 65, 50, 35, 20]:
        mask = _build_mask(s_thresh)
        valid = _pick_contours(mask)
        if len(valid) >= 2:
            break

    # One large blob → try to split it
    if len(valid) == 1:
        halves = _split_blob(_build_mask(50), valid[0])
        if halves:
            valid = halves

    if not valid:
        return []

    result = valid[:2]

    # Sort: left-to-right when side-by-side, top-to-bottom when stacked
    if len(result) == 2:
        r0, r1 = cv2.boundingRect(result[0]), cv2.boundingRect(result[1])
        cx0, cy0 = r0[0] + r0[2] // 2, r0[1] + r0[3] // 2
        cx1, cy1 = r1[0] + r1[2] // 2, r1[1] + r1[3] // 2
        if abs(cy0 - cy1) > abs(cx0 - cx1):
            result.sort(key=lambda c: cv2.boundingRect(c)[1] + cv2.boundingRect(c)[3] // 2)
        else:
            result.sort(key=lambda c: cv2.boundingRect(c)[0] + cv2.boundingRect(c)[2] // 2)

    return result


@app.post("/analyze-foot/")
def analyze_foot(
    file: UploadFile = File(...),
    binarization_type: str = Form(default='otsu'),
    adaptive_c: int = Form(default=10),
    fixed_threshold: int = Form(default=120),
    invert: str = Form(default='true'),
    foot_length_cm: float = Form(default=0.0),
):
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "No se pudo leer la imagen"})

    try:
        contours = _detect_podoscope_feet(img)
        print(f"[DEBUG] _detect_podoscope_feet: {len(contours)} pies encontrados")
        for i, c in enumerate(contours):
            bx, by, bw, bh = cv2.boundingRect(c)
            print(f"  [{i}] area={cv2.contourArea(c):.0f} bbox=({bx},{by},{bw},{bh})")

        if not contours:
            return JSONResponse(status_code=422, content={"error": "No se detectó contorno de pie. Asegúrate de que la imagen muestre la planta del pie sobre el podoscopio."})

        annotated = img.copy()

        # Per-foot contact masks with adaptive brightness threshold.
        # Otsu within each foot separates bright contact pixels from dark arch gap.
        # When the foot V-channel is clearly bimodal (dark arch + bright contact),
        # the Otsu threshold isolates actual contact pixels.
        # For feet with a uniform sole (pie plano / full contact), falls back to
        # a low fixed threshold so the arch contact area is fully captured.
        _hsv_orig = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _s_orig = _hsv_orig[:, :, 1]
        _v_orig = _hsv_orig[:, :, 2]
        _ker_micro = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))

        def _build_foot_contact(cnt: np.ndarray) -> np.ndarray:
            filled = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.drawContours(filled, [cnt], -1, 255, cv2.FILLED)
            foot_v = _v_orig[filled > 0].flatten().astype(np.uint8)
            if len(foot_v) > 200:
                v_thresh_otsu, _ = cv2.threshold(
                    foot_v.reshape(1, -1), 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                )
                v_thresh_otsu = float(v_thresh_otsu)
                dark_fraction = float(np.mean(foot_v < v_thresh_otsu))
                # Bimodal (arch gap present): use adaptive Otsu clamped to [55, 130]
                # Unimodal (pie plano, all contact): use low threshold to capture full sole
                v_thresh = float(np.clip(v_thresh_otsu, 55, 130)) if dark_fraction > 0.12 else 30.0
            else:
                v_thresh = 55.0
            contact = ((_s_orig > 40) & (_v_orig > v_thresh) & (filled > 0)).astype(np.uint8) * 255
            return cv2.morphologyEx(contact, cv2.MORPH_CLOSE, _ker_micro, iterations=1)

        foot_contact_masks = [_build_foot_contact(c) for c in contours]

        overlay = annotated.copy()
        for i, contour in enumerate(contours):
            tint = _FOOT_TINTS[i % len(_FOOT_TINTS)]
            foot_fill = np.zeros_like(img)
            foot_fill[foot_contact_masks[i] > 0] = tint
            cv2.addWeighted(overlay, 0.60, foot_fill, 0.40, 0, overlay)
        annotated = overlay

        # Contour outlines (dark border + colored line)
        for i, contour in enumerate(contours):
            color = _FOOT_COLORS[i % len(_FOOT_COLORS)]
            cv2.drawContours(annotated, [contour], -1, (10, 10, 10), 5)
            cv2.drawContours(annotated, [contour], -1, color, 3)

        metrics_list = []

        # Determine spatial arrangement: left-right vs top-bottom
        if len(contours) == 2:
            _r0, _r1 = cv2.boundingRect(contours[0]), cv2.boundingRect(contours[1])
            _dx = abs((_r0[0]+_r0[2]//2) - (_r1[0]+_r1[2]//2))
            _dy = abs((_r0[1]+_r0[3]//2) - (_r1[1]+_r1[3]//2))
            SIDE_LABELS = (["Izquierdo", "Derecho"] if _dx >= _dy
                           else ["Superior", "Inferior"])
        else:
            SIDE_LABELS = ["Izquierdo", "Derecho"]

        for i, contour in enumerate(contours):
            side = SIDE_LABELS[i] if i < len(SIDE_LABELS) else f"Pie {i + 1}"
            draw_color = _FOOT_COLORS[i % len(_FOOT_COLORS)]

            bx_hc, by_hc, bw_hc, bh_hc = cv2.boundingRect(contour)
            foot_hc_mask = foot_contact_masks[i]

            try:
                # contour → axis orientation (smooth shape from detection)
                # foot_hc_mask → actual pixel widths (arch gap preserved)
                hc_result, widths_info = apply_hernandez_corvo(foot_hc_mask, contour)

                foot_length_px = float(np.linalg.norm(
                    np.array(hc_result.anterior_point, dtype=float) -
                    np.array(hc_result.posterior_point, dtype=float)
                ))
                if foot_length_cm > 0 and foot_length_px > 0:
                    px_to_cm = foot_length_cm / foot_length_px
                    x_width_cm_val = hc_result.x_width * px_to_cm
                    y_width_cm_val = hc_result.y_width * px_to_cm
                else:
                    px_to_cm = None
                    x_width_cm_val = None
                    y_width_cm_val = None

                rot_mat_inv = cv2.invertAffineTransform(widths_info["rot_mat"])

                def to_orig(px, py):
                    pt = np.array([[[float(px), float(py)]]], dtype=np.float32)
                    return tuple(cv2.transform(pt, rot_mat_inv)[0][0].astype(int))

                x_row  = widths_info["x_row"]
                y_row  = widths_info["y_row"]
                x_min_r = widths_info["x_min"]
                x_max_r = widths_info["x_max"]

                # Forefoot width line (X)
                x_p1 = to_orig(x_min_r, x_row)
                x_p2 = to_orig(x_max_r, x_row)
                cv2.line(annotated, x_p1, x_p2, (10, 10, 10), 5, cv2.LINE_AA)
                cv2.line(annotated, x_p1, x_p2, draw_color, 3, cv2.LINE_AA)
                x_label = (f"Antepie {side[:3]}: {x_width_cm_val:.2f} cm"
                           if x_width_cm_val else f"Antepie {side[:3]}: {hc_result.x_width:.0f} px")
                mid_x = ((x_p1[0] + x_p2[0]) // 2, min(x_p1[1], x_p2[1]) - 12)
                _put_label(annotated, x_label, mid_x, scale=0.55, color=draw_color)

                # Arch width line (Y)
                y_p1 = to_orig(x_min_r, y_row)
                y_p2 = to_orig(x_max_r, y_row)
                arch_color = (0, 230, 255)
                cv2.line(annotated, y_p1, y_p2, (10, 10, 10), 5, cv2.LINE_AA)
                cv2.line(annotated, y_p1, y_p2, arch_color, 3, cv2.LINE_AA)
                y_label = (f"Arco {side[:3]}: {y_width_cm_val:.2f} cm"
                           if y_width_cm_val else f"Arco {side[:3]}: {hc_result.y_width:.0f} px")
                mid_y = ((y_p1[0] + y_p2[0]) // 2, min(y_p1[1], y_p2[1]) - 12)
                _put_label(annotated, y_label, mid_y, scale=0.55, color=arch_color)

                # Anterior (toe) and posterior (heel) axis points
                _draw_circle(annotated, hc_result.anterior_point,  r=8, color=(255, 230, 0))
                _draw_circle(annotated, hc_result.posterior_point, r=8, color=(255, 140, 0))

                # Classification label below the foot
                bx, by, bw, bh = cv2.boundingRect(contour)
                label_y = min(by + bh + 24, annotated.shape[0] - 4)
                idx_label = f"{side}  {hc_result.classification}  I={hc_result.index:.1f}%"
                _put_label(annotated, idx_label, (bx, label_y), scale=0.60, color=draw_color, thickness=2)

                metrics_list.append({
                    "side":           side,
                    "classification": hc_result.classification,
                    "plantar_index":  hc_result.index,
                    "x_width_cm":     x_width_cm_val,
                    "y_width_cm":     y_width_cm_val,
                    "x_width_px":     hc_result.x_width,
                    "y_width_px":     hc_result.y_width,
                    "calibrated":     px_to_cm is not None,
                })

            except Exception as foot_err:
                print(f"[ERROR] Hernandez-Corvo {side}: {foot_err}")
                metrics_list.append({"side": side, "error": str(foot_err)})

        _, buffer = cv2.imencode('.png', annotated)
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "metrics": metrics_list,
            "images": {
                "annotated": f"data:image/png;base64,{annotated_b64}"
            },
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})
