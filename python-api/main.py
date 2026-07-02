from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import numpy as np
import cv2
import base64
from hernandez_corvo import apply_hernandez_corvo
from largest_contour import largest_contour
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
        contour = largest_contour(steps["clean"], min_area_ratio=0.01, max_area_ratio=0.8)
        if contour is None:
            return JSONResponse(status_code=422, content={"error": "No se detectó contorno de pie"})

        hc_result, widths_info = apply_hernandez_corvo(steps["clean"], contour)

        # Calibrate px→cm using the real foot length measured by the user.
        # Without a physical reference in the image, any hardcoded factor would be wrong.
        foot_length_px = float(np.linalg.norm(
            np.array(hc_result.anterior_point, dtype=float) -
            np.array(hc_result.posterior_point, dtype=float)
        ))
        if foot_length_cm > 0 and foot_length_px > 0:
            px_to_cm = foot_length_cm / foot_length_px
            x_width_cm = hc_result.x_width * px_to_cm
            y_width_cm = hc_result.y_width * px_to_cm
        else:
            px_to_cm = None
            x_width_cm = None
            y_width_cm = None

        annotated = img.copy()

        # Coordinates in widths_info are in the rotated image space.
        # Apply the inverse rotation to draw lines correctly on the original image.
        rot_mat_inv = cv2.invertAffineTransform(widths_info["rot_mat"])

        def to_orig(x, y):
            pt = np.array([[[float(x), float(y)]]], dtype=np.float32)
            tp = cv2.transform(pt, rot_mat_inv)[0][0]
            return (int(tp[0]), int(tp[1]))

        x_row = widths_info["x_row"]
        y_row = widths_info["y_row"]
        x_min_r = widths_info["x_min"]
        x_max_r = widths_info["x_max"]

        x_p1 = to_orig(x_min_r, x_row)
        x_p2 = to_orig(x_max_r, x_row)
        cv2.line(annotated, x_p1, x_p2, (0, 255, 0), 3)
        x_label = f"X: {x_width_cm:.2f} cm" if x_width_cm is not None else f"X: {hc_result.x_width:.0f}px"
        cv2.putText(annotated, x_label, (x_p1[0] + 5, x_p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        y_p1 = to_orig(x_min_r, y_row)
        y_p2 = to_orig(x_max_r, y_row)
        cv2.line(annotated, y_p1, y_p2, (0, 255, 255), 3)
        y_label = f"Y: {y_width_cm:.2f} cm" if y_width_cm is not None else f"Y: {hc_result.y_width:.0f}px"
        cv2.putText(annotated, y_label, (y_p1[0] + 5, y_p1[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        cv2.drawContours(annotated, [contour], -1, (255, 0, 255), 2)
        _, buffer = cv2.imencode('.png', annotated)
        annotated_b64 = base64.b64encode(buffer).decode('utf-8')

        return {
            "metrics": {
                "plantar_index": hc_result.index,
                "x_width_cm": x_width_cm,
                "y_width_cm": y_width_cm,
                "x_width_px": hc_result.x_width,
                "y_width_px": hc_result.y_width,
                "classification": hc_result.classification,
                "calibrated": px_to_cm is not None,
            },
            "images": {
                "annotated": f"data:image/png;base64,{annotated_b64}"
            }
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
