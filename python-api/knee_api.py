from fastapi import APIRouter, File, UploadFile, Request
from fastapi.responses import StreamingResponse, JSONResponse
import io
import base64
import cv2
import numpy as np
import mediapipe as mp
import logging
from report_utils import generate_report_pdf

router = APIRouter()

@router.post("/generate-report/")
async def generate_report(request: Request):
    try:
        data = await request.json()
        pdf_bytes = generate_report_pdf(data)
        return StreamingResponse(io.BytesIO(pdf_bytes), media_type="application/pdf", headers={
            "Content-Disposition": "attachment; filename=ReportePaciente.pdf"
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


# -------- FUNCIONES --------
def angle_between_points(a, b, c):
    ba = np.array(a) - np.array(b)
    bc = np.array(c) - np.array(b)
    norm_ba = np.linalg.norm(ba)
    norm_bc = np.linalg.norm(bc)
    if norm_ba == 0 or norm_bc == 0:
        raise ValueError("Vectores inválidos para cálculo de ángulo (norma cero)")
    cos_angle = np.dot(ba, bc) / (norm_ba * norm_bc)
    angle = np.arccos(np.clip(cos_angle, -1.0, 1.0))
    deg = np.degrees(angle)
    if np.isnan(deg):
        raise ValueError("Ángulo inválido (NaN)")
    return deg

class PoseDetector:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

    def detect(self, image):
        img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)
        if not results.pose_landmarks:
            raise Exception("No landmarks")
        h, w = image.shape[:2]
        lm = results.pose_landmarks.landmark
        mp_lm = self.mp_pose.PoseLandmark

        def pt(lm_id):
            return (int(lm[lm_id].x * w), int(lm[lm_id].y * h))

        def vis(lm_id):
            return lm[lm_id].visibility

        return {
            "left_hip":    pt(mp_lm.LEFT_HIP),
            "left_knee":   pt(mp_lm.LEFT_KNEE),
            "left_ankle":  pt(mp_lm.LEFT_ANKLE),
            "right_hip":   pt(mp_lm.RIGHT_HIP),
            "right_knee":  pt(mp_lm.RIGHT_KNEE),
            "right_ankle": pt(mp_lm.RIGHT_ANKLE),
            "right_shoulder": pt(mp_lm.RIGHT_SHOULDER),
            "left_shoulder":  pt(mp_lm.LEFT_SHOULDER),
            # Visibility scores for side selection in sagittal view
            "left_hip_vis":   vis(mp_lm.LEFT_HIP),
            "left_knee_vis":  vis(mp_lm.LEFT_KNEE),
            "left_ankle_vis": vis(mp_lm.LEFT_ANKLE),
            "right_hip_vis":   vis(mp_lm.RIGHT_HIP),
            "right_knee_vis":  vis(mp_lm.RIGHT_KNEE),
            "right_ankle_vis": vis(mp_lm.RIGHT_ANKLE),
        }

# -------- ENDPOINTS --------

@router.post("/analyze-muscle-chain/")
def analyze_muscle_chain(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Imagen inválida"})
    img_b64 = base64.b64encode(image_bytes).decode('utf-8')
    detector = PoseDetector()
    try:
        lm = detector.detect(img)
        ang_left_knee  = angle_between_points(lm["left_hip"],      lm["left_knee"],  lm["left_ankle"])
        ang_right_knee = angle_between_points(lm["right_hip"],     lm["right_knee"], lm["right_ankle"])

        if not all(k in lm for k in ["left_hip", "left_shoulder", "right_hip", "right_shoulder"]):
            raise ValueError("No se detectaron hombros para análisis de cadena completa.")

        ang_left_hip  = angle_between_points(lm["left_shoulder"],  lm["left_hip"],  lm["left_knee"])
        ang_right_hip = angle_between_points(lm["right_shoulder"], lm["right_hip"], lm["right_knee"])

        # Ankle flexion: angle between shin and vertical axis downward
        ang_left_ankle  = angle_between_points(lm["left_knee"],  lm["left_ankle"],  (lm["left_ankle"][0],  lm["left_ankle"][1]  + 100))
        ang_right_ankle = angle_between_points(lm["right_knee"], lm["right_ankle"], (lm["right_ankle"][0], lm["right_ankle"][1] + 100))

        all_main   = [ang_left_knee, ang_right_knee, ang_left_hip, ang_right_hip]
        all_angles = [ang_left_knee, ang_right_knee, ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle]

        if any(np.isnan(a) for a in all_angles):
            raise ValueError("Ángulos inválidos (NaN)")

        rasgos = [
            f"Ángulo rodilla izquierda: {ang_left_knee:.1f}°",
            f"Ángulo rodilla derecha: {ang_right_knee:.1f}°",
            f"Ángulo cadera izquierda: {ang_left_hip:.1f}°",
            f"Ángulo cadera derecha: {ang_right_hip:.1f}°",
            f"Ángulo tobillo izquierdo: {ang_left_ankle:.1f}°",
            f"Ángulo tobillo derecho: {ang_right_ankle:.1f}°",
        ]

        chain = "Indeterminada"
        explanation = "No se pudo clasificar la cadena con los datos actuales."

        # Order matters: most specific/restrictive conditions first
        if all(a < 160 for a in all_angles):
            chain = "Cadena de espiración"
            explanation = "Postura global de cierre y espiración (todos los ángulos pequeños)."
        elif any(a < 160 for a in all_main):
            chain = "Cadena de flexión"
            explanation = "Se detecta flexión significativa en al menos una articulación principal (rodilla o cadera)."
        elif all(a > 175 for a in all_angles):
            chain = "Cadena de inspiración"
            explanation = "Postura global de apertura e inspiración (todos los ángulos grandes)."
        elif all(a > 170 for a in all_main):
            chain = "Cadena de extensión"
            explanation = "Todas las articulaciones principales están en extensión."
        elif (all(a > 170 for a in [ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle])
              and any(a < 170 for a in [ang_left_knee, ang_right_knee])):
            chain = "Cadena de apertura"
            explanation = "Caderas y tobillos en apertura, rodillas con ligera flexión."
        elif any(a < 160 for a in [ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle]):
            chain = "Cadena de cierre"
            explanation = "Caderas o tobillos en cierre (flexión o aducción marcada)."

        return {
            "chain": chain,
            "explanation": explanation,
            "rasgos": rasgos,
            "left_knee_angle":   ang_left_knee,
            "right_knee_angle":  ang_right_knee,
            "left_hip_angle":    ang_left_hip,
            "right_hip_angle":   ang_right_hip,
            "left_ankle_angle":  ang_left_ankle,
            "right_ankle_angle": ang_right_ankle,
            "imagen_original": img_b64,
        }
    except Exception as e:
        import traceback
        exc_type = type(e).__name__
        msg = str(e).strip() or "No se detectaron puntos de referencia o la imagen no es válida."
        tb = traceback.format_exc()
        return JSONResponse(
            status_code=500,
            content={
                "chain": None,
                "explanation": f"[{exc_type}] {msg}\nTraceback: {tb}",
                "rasgos": [],
                "left_knee_angle": None, "right_knee_angle": None,
                "left_hip_angle":  None, "right_hip_angle":  None,
                "left_ankle_angle": None, "right_ankle_angle": None,
            }
        )


def _classify_knee_frontal(angle_left, angle_right):
    """
    Classify each knee individually for frontal view.
    Clinical reference: normal tibiofemoral angle is 174–180°.
    Valgus (knock knees): angle < 170°
    Varus  (bow legs):    angle > 182°
    """
    def side_class(ang):
        if ang < 170:
            return "Valgo"
        elif ang > 182:
            return "Varo"
        return "Normal"

    left_class  = side_class(angle_left)
    right_class = side_class(angle_right)

    if left_class == "Normal" and right_class == "Normal":
        return "Normal"
    if left_class == right_class:
        return f"Genu {left_class} bilateral"
    return f"Genu {left_class} Izq / {right_class} Der"


def draw_knee_frontal(image: np.ndarray):
    annotated = image.copy()
    detector = PoseDetector()
    try:
        landmarks = detector.detect(image)
    except Exception:
        cv2.putText(annotated, "No se detectaron puntos de referencia", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return annotated, None, None

    l_ankle = landmarks["left_ankle"]
    l_knee  = landmarks["left_knee"]
    l_hip   = landmarks["left_hip"]
    r_ankle = landmarks["right_ankle"]
    r_knee  = landmarks["right_knee"]
    r_hip   = landmarks["right_hip"]

    # Draw anatomical points
    for pt in [l_ankle, l_knee, l_hip, r_ankle, r_knee, r_hip]:
        cv2.circle(annotated, pt, 8, (0, 255, 255), -1)

    # Draw limb segments
    cv2.line(annotated, l_hip,   l_knee,  (0, 255, 0), 3)
    cv2.line(annotated, l_knee,  l_ankle, (255, 0, 0), 3)
    cv2.line(annotated, r_hip,   r_knee,  (0, 255, 0), 3)
    cv2.line(annotated, r_knee,  r_ankle, (255, 0, 0), 3)

    # Tibiofemoral angle: hip → knee → ankle (clinically correct reference points)
    angle_left  = angle_between_points(l_hip, l_knee, l_ankle)
    angle_right = angle_between_points(r_hip, r_knee, r_ankle)

    cv2.putText(annotated, f"Izq: {angle_left:.1f}°",  (l_knee[0] - 60, l_knee[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    cv2.putText(annotated, f"Der: {angle_right:.1f}°", (r_knee[0] - 60, r_knee[1] - 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

    avg_angle      = (angle_left + angle_right) / 2
    classification = _classify_knee_frontal(angle_left, angle_right)
    return annotated, avg_angle, classification


def draw_knee_sagittal(image: np.ndarray):
    annotated = image.copy()
    detector = PoseDetector()
    try:
        landmarks = detector.detect(image)
    except Exception:
        cv2.putText(annotated, "No se detectaron puntos de referencia", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        return annotated, None, None

    # Use MediaPipe visibility scores to pick the more visible side
    left_vis  = landmarks["left_hip_vis"]  + landmarks["left_knee_vis"]  + landmarks["left_ankle_vis"]
    right_vis = landmarks["right_hip_vis"] + landmarks["right_knee_vis"] + landmarks["right_ankle_vis"]
    side = "left" if left_vis >= right_vis else "right"

    hip   = landmarks[f"{side}_hip"]
    knee  = landmarks[f"{side}_knee"]
    ankle = landmarks[f"{side}_ankle"]

    line_color  = (255, 140, 0)
    point_color = (0, 0, 0)

    for pt in [hip, knee, ankle]:
        cv2.circle(annotated, pt, 6, point_color, -1)

    cv2.line(annotated, hip,  knee,  line_color, 3)
    cv2.line(annotated, knee, ankle, line_color, 3)

    ang = angle_between_points(hip, knee, ankle)

    angle_text = f"{ang:.1f}°"
    (tw, th), _ = cv2.getTextSize(angle_text, cv2.FONT_HERSHEY_SIMPLEX, 0.8, 2)
    text_pos = (knee[0] - tw // 2, knee[1] - 28)
    cv2.putText(annotated, angle_text, (text_pos[0], text_pos[1] + th),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)

    if 175 <= ang <= 185:
        classification = "Normal"
    elif ang < 175:
        classification = "Genu Flexum"
    else:
        classification = "Genu Recurvatum"

    return annotated, ang, classification


@router.post("/analyze-knee/frontal/")
def analyze_knee_frontal(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "No se pudo leer la imagen"})
    annotated, angle, classification = draw_knee_frontal(img)
    _, buffer = cv2.imencode('.png', annotated)
    annotated_b64 = base64.b64encode(buffer).decode('utf-8')
    return {
        "metrics": {
            "plane": "frontal",
            "knee_angle_deg": angle,
            "classification": classification,
        },
        "images": {
            "annotated": f"data:image/png;base64,{annotated_b64}"
        }
    }


@router.post("/analyze-knee/sagittal/")
def analyze_knee_sagittal(file: UploadFile = File(...)):
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "No se pudo leer la imagen"})
    annotated, angle, classification = draw_knee_sagittal(img)
    _, buffer = cv2.imencode('.png', annotated)
    annotated_b64 = base64.b64encode(buffer).decode('utf-8')
    return {
        "metrics": {
            "plane": "sagittal",
            "knee_angle_deg": angle,
            "classification": classification,
        },
        "images": {
            "annotated": f"data:image/png;base64,{annotated_b64}"
        }
    }
