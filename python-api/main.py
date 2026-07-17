from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import base64
from hernandez_corvo import apply_hernandez_corvo
from largest_contour import largest_contour, foot_contours
from preprocessing import preprocess_foot_image
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


# Colors per foot: left=blue-green, right=magenta-pink
_FOOT_COLORS = [(0, 200, 120), (200, 60, 200)]
# Semi-transparent overlay tints (BGR)
_FOOT_TINTS  = [(0, 180, 100), (180, 40, 180)]


def _put_label(img, text, pos, scale=0.55, color=(255, 255, 255), thickness=1):
    """Draw text with a dark background rectangle for readability."""
    (tw, th), baseline = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, thickness)
    x, y = pos
    cv2.rectangle(img, (x - 3, y - th - 4), (x + tw + 3, y + baseline), (20, 20, 20), cv2.FILLED)
    cv2.putText(img, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, scale, color, thickness, cv2.LINE_AA)


def _draw_circle(img, pt, r=6, color=(255, 255, 0), thickness=2):
    cv2.circle(img, pt, r + 2, (20, 20, 20), -1)
    cv2.circle(img, pt, r, color, thickness)


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

    invert_bool = invert.lower() != 'false'

    try:
        steps = preprocess_foot_image(
            img,
            binarization_type=binarization_type,
            adaptive_c=adaptive_c,
            fixed_threshold=fixed_threshold,
            invert=invert_bool,
        )

        h_img, w_img = img.shape[:2]
        img_area = h_img * w_img
        # Save debug images so we can inspect preprocessing output
        cv2.imwrite('/tmp/debug_binary.png', steps['binary'])
        cv2.imwrite('/tmp/debug_clean.png', steps['clean'])
        print(f"[DEBUG] img={w_img}x{h_img}  binary_white%={np.mean(steps['binary']==255):.3f}  clean_white%={np.mean(steps['clean']==255):.3f}")
        for name, mask in [("clean", steps["clean"]), ("binary", steps["binary"])]:
            cnts_all, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            print(f"[DEBUG] {name}: total_contours={len(cnts_all)}")
            from largest_contour import _solidity
            for i, c in enumerate(sorted(cnts_all, key=cv2.contourArea, reverse=True)[:5]):
                area = cv2.contourArea(c)
                x, y, bw, bh = cv2.boundingRect(c)
                ratio = area / img_area
                aspect = max(bw, bh) / (min(bw, bh) + 1e-5)
                sol = _solidity(c)
                print(f"  [{i}] ratio={ratio:.3f} aspect={aspect:.2f} solidity={sol:.2f} bbox=({x},{y},{bw},{bh})")

        # Pass 1: two feet from the cleaned mask
        contours = foot_contours(steps["clean"], max_n=2)
        print(f"[DEBUG] Pass1 foot_contours(clean): {len(contours)}")

        # Pass 2: single largest from cleaned mask
        if not contours:
            c = largest_contour(steps["clean"], min_area_ratio=0.002, max_area_ratio=0.85)
            print(f"[DEBUG] Pass2 largest_contour(clean): {'found' if c is not None else 'None'}")
            if c is not None:
                contours = [c]

        # Pass 3: fall back to raw binary (before heavy morphological cleanup)
        if not contours:
            contours = foot_contours(steps["binary"], max_n=2)
            print(f"[DEBUG] Pass3 foot_contours(binary): {len(contours)}")

        # Pass 4: single largest from raw binary
        if not contours:
            c = largest_contour(steps["binary"], min_area_ratio=0.001, max_area_ratio=0.90)
            print(f"[DEBUG] Pass4 largest_contour(binary): {'found' if c is not None else 'None'}")
            if c is not None:
                contours = [c]

        if not contours:
            return JSONResponse(status_code=422, content={"error": "No se detectó contorno de pie"})

        # Start with the original image for annotation
        annotated = img.copy()

        # Draw a semi-transparent filled overlay for each detected foot
        overlay = annotated.copy()
        for i, contour in enumerate(contours):
            tint = _FOOT_TINTS[i % len(_FOOT_TINTS)]
            foot_fill = np.zeros_like(img)
            cv2.drawContours(foot_fill, [contour], -1, tint, thickness=cv2.FILLED)
            cv2.addWeighted(overlay, 0.65, foot_fill, 0.35, 0, overlay)
        annotated = overlay

        metrics_list = []
        SIDE_LABELS = ["Izquierdo", "Derecho"]

        for i, contour in enumerate(contours):
            side = SIDE_LABELS[i] if i < len(SIDE_LABELS) else f"Pie {i + 1}"
            draw_color = _FOOT_COLORS[i % len(_FOOT_COLORS)]

            # --- Per-foot mask (critical: avoids measuring the other foot) ---
            foot_mask = np.zeros_like(steps["clean"])
            cv2.drawContours(foot_mask, [contour], -1, 255, thickness=cv2.FILLED)
            foot_mask = cv2.bitwise_and(steps["clean"], foot_mask)

            try:
                hc_result, widths_info = apply_hernandez_corvo(foot_mask, contour)

                # Calibration
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

                x_row = widths_info["x_row"]
                y_row = widths_info["y_row"]
                x_min_r = widths_info["x_min"]
                x_max_r = widths_info["x_max"]

                # Forefoot width line (X)
                x_p1 = to_orig(x_min_r, x_row)
                x_p2 = to_orig(x_max_r, x_row)
                cv2.line(annotated, x_p1, x_p2, draw_color, 3, cv2.LINE_AA)
                x_label = (f"X {side[:3]}: {x_width_cm_val:.2f} cm"
                           if x_width_cm_val else f"X {side[:3]}: {hc_result.x_width:.0f} px")
                mid_x = ((x_p1[0] + x_p2[0]) // 2, min(x_p1[1], x_p2[1]) - 10)
                _put_label(annotated, x_label, mid_x, color=draw_color)

                # Arch width line (Y)
                y_p1 = to_orig(x_min_r, y_row)
                y_p2 = to_orig(x_max_r, y_row)
                arch_color = (0, 200, 220)
                cv2.line(annotated, y_p1, y_p2, arch_color, 3, cv2.LINE_AA)
                y_label = (f"Y {side[:3]}: {y_width_cm_val:.2f} cm"
                           if y_width_cm_val else f"Y {side[:3]}: {hc_result.y_width:.0f} px")
                mid_y = ((y_p1[0] + y_p2[0]) // 2, min(y_p1[1], y_p2[1]) - 10)
                _put_label(annotated, y_label, mid_y, color=arch_color)

                # Contour outline
                cv2.drawContours(annotated, [contour], -1, draw_color, 2)

                # Anterior (toe) and posterior (heel) points
                _draw_circle(annotated, hc_result.anterior_point,  r=7, color=(255, 230,  0))
                _draw_circle(annotated, hc_result.posterior_point, r=7, color=(255, 140,  0))

                # Side + classification label near the foot bounding box
                bx, by, bw, bh = cv2.boundingRect(contour)
                idx_label = f"{side} | {hc_result.classification} | I: {hc_result.index:.1f}%"
                _put_label(annotated, idx_label, (bx, max(0, by - 12)), scale=0.52, color=draw_color)

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
        return JSONResponse(status_code=500, content={"error": str(e)})
