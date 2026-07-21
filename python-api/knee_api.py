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


# -------- UTILIDADES --------

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
            "nose":           pt(mp_lm.NOSE),
            "left_ear":       pt(mp_lm.LEFT_EAR),
            "right_ear":      pt(mp_lm.RIGHT_EAR),
            # Visibility
            "left_hip_vis":    vis(mp_lm.LEFT_HIP),
            "left_knee_vis":   vis(mp_lm.LEFT_KNEE),
            "left_ankle_vis":  vis(mp_lm.LEFT_ANKLE),
            "right_hip_vis":   vis(mp_lm.RIGHT_HIP),
            "right_knee_vis":  vis(mp_lm.RIGHT_KNEE),
            "right_ankle_vis": vis(mp_lm.RIGHT_ANKLE),
            "left_ear_vis":    vis(mp_lm.LEFT_EAR),
            "right_ear_vis":   vis(mp_lm.RIGHT_EAR),
        }


# -------- RASGOS POR CADENA --------

CHAIN_TRAITS = {
    "Cadena de espiración": [
        "Pelvis anteriorizada",
        "Tórax trasladado posteriormente",
        "Hipercifosis",
        "Hiperlordosis lumbar",
        "Pie en pronación / plano",
        "Rotación interna de cadera",
    ],
    "Cadena de inspiración": [
        "Rectificación cervical",
        "Inversión cervical",
        "Dorso plano",
        "Pelvis posteriorizado",
        "Rotación externa de cadera",
        "Hiperlordosis lumbar",
        "Recurvatum de rodilla",
        "Pie en eversión",
        "Genu recurvatum",
        "Ascenso de rótula",
    ],
    "Cadena de flexión": [
        "Genu flexum",
        "Cifosis",
        "Hipercifosis",
        "Inversión de cervicales",
        "Proyección anterior de la cabeza",
        "Rectificación lumbar",
        "Valgo de rodilla",
        "Rotación interna",
        "MsSs: descenso, aducción, rotación interna",
        "Cierre de costillas",
        "Esternón hundido",
        "Flexión de Msls",
    ],
    "Cadena de extensión": [
        "Genu recurvatum",
        "Dorso plano",
        "Rectificación cervical",
        "Hiperlordosis baja",
        "Extensión de Msls",
        "MsSs: ascenso, rotación externa, abducción",
        "Apertura de costillas",
        "Rotación interna de cadera y rodilla",
        "Ascenso de rótula",
        "Pie cavo",
        "Dedos en garra",
        "Esternón horizontal",
        "Proyección posterior de la cabeza",
    ],
    "Cadena de apertura": [
        "Pie plano",
        "Genu flexum",
        "MsSs: ascenso, abducción, rotación externa, supinación",
        "Caderas en rotación externa",
        "Hipercifosis alta",
        "Rectificación lumbar",
        "Varo de rodilla",
        "Nutación del iliaco",
        "Anteproyección del cuello",
        "Báscula anterior del cuello",
        "Báscula anterior del tronco",
    ],
    "Cadena de cierre": [
        "MsSs: descenso, aducción, rotación interna, flexo-pronación",
        "Parrilla costal cerrada",
        "Rotación interna de cadera",
        "Valgo de rodilla",
        "Flexum de rodilla",
        "Pie plano",
        "Valgo de calcáneo",
        "Flexo de coxofemoral",
        "Contranutación de ilíacos",
        "Clavículas en V",
    ],
}


def _detect_single_trait(name, lm, ang_lk, ang_rk, ang_lh, ang_rh, ang_la, ang_ra, scale):
    """
    Retorna (cumple: bool, auto: bool).
    auto=False significa que no se puede detectar automáticamente desde la imagen.
    scale = distancia hombro-tobillo para normalizar desplazamientos.
    """
    n = name.lower()

    sh_x = (lm["left_shoulder"][0] + lm["right_shoulder"][0]) / 2
    sh_y = (lm["left_shoulder"][1] + lm["right_shoulder"][1]) / 2
    hip_x = (lm["left_hip"][0] + lm["right_hip"][0]) / 2
    ank_x = (lm["left_ankle"][0] + lm["right_ankle"][0]) / 2
    ank_y = (lm["left_ankle"][1] + lm["right_ankle"][1]) / 2
    ear_x = (lm["left_ear"][0] + lm["right_ear"][0]) / 2
    nose_x = lm["nose"][0]

    # Determinar dirección de la mirada en sagital
    face_dir = 1 if nose_x > sh_x else -1

    # Desplazamientos A-P normalizados (positivo = anterior)
    ref = max(scale, 50)
    ear_vs_sh  = face_dir * (ear_x  - sh_x)  / ref
    sh_vs_hip  = face_dir * (sh_x   - hip_x) / ref
    hip_vs_ank = face_dir * (hip_x  - ank_x) / ref

    avg_knee = (ang_lk + ang_rk) / 2
    avg_hip  = (ang_lh + ang_rh) / 2

    # === Detecciones automáticas ===

    if "genu flexum" in n or "flexum de rodilla" in n:
        return any(a < 175 for a in [ang_lk, ang_rk]), True

    if "genu recurvatum" in n or "recurvatum de rodilla" in n:
        return any(a > 185 for a in [ang_lk, ang_rk]), True

    if "proyección anterior de la cabeza" in n or "anteproyección del cuello" in n:
        return ear_vs_sh > 0.08, True

    if "proyección posterior de la cabeza" in n:
        return ear_vs_sh < -0.08, True

    if "báscula anterior del cuello" in n:
        return ear_vs_sh > 0.06, True

    if "pelvis anteriorizada" in n:
        return hip_vs_ank > 0.08, True

    if "pelvis posteriorizado" in n:
        return hip_vs_ank < -0.08, True

    if "hipercifosis alta" in n:
        return sh_vs_hip < -0.18, True

    if "hipercifosis" in n:
        return sh_vs_hip < -0.10, True

    if "cifosis" in n:
        return sh_vs_hip < -0.06, True

    if "hiperlordosis" in n or "hiperlordorsis" in n:
        return avg_hip > 175, True

    if "rectificación lumbar" in n:
        return avg_hip < 165, True

    if "dorso plano" in n:
        return abs(sh_vs_hip) < 0.05, True

    if "tórax trasladado posteriormente" in n:
        return sh_vs_hip < -0.12, True

    if "báscula anterior del tronco" in n:
        return sh_vs_hip > 0.12, True

    if "rectificación cervical" in n or "inversión cervical" in n or "inversión de cervicales" in n:
        return abs(ear_vs_sh) < 0.04, True

    if "flexo de coxofemoral" in n:
        return avg_hip < 165, True

    # Traits that require frontal view or specialized instruments
    return False, False


def _detect_chain_traits(chain, lm, ang_lk, ang_rk, ang_lh, ang_rh, ang_la, ang_ra):
    traits_names = CHAIN_TRAITS.get(chain, [])
    sh_y = (lm["left_shoulder"][1] + lm["right_shoulder"][1]) / 2
    ank_y = (lm["left_ankle"][1]   + lm["right_ankle"][1])   / 2
    scale = abs(sh_y - ank_y)

    rasgos = []
    for name in traits_names:
        cumple, auto = _detect_single_trait(name, lm, ang_lk, ang_rk, ang_lh, ang_rh, ang_la, ang_ra, scale)
        rasgos.append({"nombre": name, "cumple": bool(cumple), "auto": bool(auto)})

    total = len(rasgos)
    cumplidos = sum(1 for r in rasgos if r["cumple"])
    porcentaje = round((cumplidos / total * 100) if total > 0 else 0, 1)

    return rasgos, porcentaje


# -------- ENDPOINTS --------

@router.post("/analyze-muscle-chain/")
def analyze_muscle_chain(
    file: UploadFile = File(...),
    file_frontal: UploadFile = File(None),
    file_posterior: UploadFile = File(None),
):
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Imagen inválida"})
    img_b64 = base64.b64encode(image_bytes).decode('utf-8')

    frontal_b64 = None
    if file_frontal:
        fb = file_frontal.file.read()
        if fb:
            frontal_b64 = base64.b64encode(fb).decode('utf-8')

    posterior_b64 = None
    if file_posterior:
        pb = file_posterior.file.read()
        if pb:
            posterior_b64 = base64.b64encode(pb).decode('utf-8')

    detector = PoseDetector()
    try:
        lm = detector.detect(img)
        ang_left_knee  = angle_between_points(lm["left_hip"],      lm["left_knee"],  lm["left_ankle"])
        ang_right_knee = angle_between_points(lm["right_hip"],     lm["right_knee"], lm["right_ankle"])

        ang_left_hip  = angle_between_points(lm["left_shoulder"],  lm["left_hip"],  lm["left_knee"])
        ang_right_hip = angle_between_points(lm["right_shoulder"], lm["right_hip"], lm["right_knee"])

        ang_left_ankle  = angle_between_points(lm["left_knee"],  lm["left_ankle"],  (lm["left_ankle"][0],  lm["left_ankle"][1]  + 100))
        ang_right_ankle = angle_between_points(lm["right_knee"], lm["right_ankle"], (lm["right_ankle"][0], lm["right_ankle"][1] + 100))

        all_main   = [ang_left_knee, ang_right_knee, ang_left_hip, ang_right_hip]
        all_angles = [ang_left_knee, ang_right_knee, ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle]

        if any(np.isnan(a) for a in all_angles):
            raise ValueError("Ángulos inválidos (NaN)")

        chain = None
        explanation = ""

        if all(a < 160 for a in all_angles):
            chain = "Cadena de espiración"
            explanation = "Postura global de cierre y espiración (todos los ángulos pequeños)."
        elif any(a < 160 for a in all_main):
            chain = "Cadena de flexión"
            explanation = "Se detecta flexión significativa en al menos una articulación principal (rodilla o cadera)."
        elif all(a > 175 for a in all_angles):
            chain = "Cadena de inspiración"
            explanation = "Postura global de apertura e inspiración (todos los ángulos grandes)."
        elif all(a > 165 for a in all_main):
            chain = "Cadena de extensión"
            explanation = "Las articulaciones principales están en extensión."
        elif (all(a > 165 for a in [ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle])
              and any(a < 170 for a in [ang_left_knee, ang_right_knee])):
            chain = "Cadena de apertura"
            explanation = "Caderas y tobillos en apertura, rodillas con ligera flexión."
        elif any(a < 160 for a in [ang_left_hip, ang_right_hip, ang_left_ankle, ang_right_ankle]):
            chain = "Cadena de cierre"
            explanation = "Caderas o tobillos en cierre (flexión o aducción marcada)."

        # Fallback: pick chain with highest rasgo match
        if chain is None:
            best_chain = None
            best_pct = -1
            for c in CHAIN_TRAITS:
                _, pct = _detect_chain_traits(c, lm, ang_left_knee, ang_right_knee,
                                              ang_left_hip, ang_right_hip,
                                              ang_left_ankle, ang_right_ankle)
                if pct > best_pct:
                    best_pct = pct
                    best_chain = c
            chain = best_chain or "Cadena de extensión"
            explanation = f"Clasificación por rasgos dominantes ({best_pct:.0f}% de coincidencia)."

        rasgos_detallados, porcentaje = _detect_chain_traits(
            chain, lm,
            ang_left_knee, ang_right_knee,
            ang_left_hip, ang_right_hip,
            ang_left_ankle, ang_right_ankle,
        )

        rasgos_legacy = [
            f"Ángulo rodilla izquierda: {ang_left_knee:.1f}°",
            f"Ángulo rodilla derecha: {ang_right_knee:.1f}°",
            f"Ángulo cadera izquierda: {ang_left_hip:.1f}°",
            f"Ángulo cadera derecha: {ang_right_hip:.1f}°",
            f"Ángulo tobillo izquierdo: {ang_left_ankle:.1f}°",
            f"Ángulo tobillo derecho: {ang_right_ankle:.1f}°",
        ]

        return {
            "chain": chain,
            "explanation": explanation,
            "rasgos": rasgos_legacy,
            "rasgos_detallados": rasgos_detallados,
            "porcentaje": float(porcentaje),
            "left_knee_angle":   float(ang_left_knee),
            "right_knee_angle":  float(ang_right_knee),
            "left_hip_angle":    float(ang_left_hip),
            "right_hip_angle":   float(ang_right_hip),
            "left_ankle_angle":  float(ang_left_ankle),
            "right_ankle_angle": float(ang_right_ankle),
            "imagen_original": img_b64,
            "imagen_frontal": frontal_b64,
            "imagen_posterior": posterior_b64,
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
                "rasgos_detallados": [],
                "porcentaje": 0,
            }
        )


# -------- ALINEACIÓN SAGITAL --------

@router.post("/analyze-alignment/sagittal/")
def analyze_alignment_sagittal(file: UploadFile = File(...)):
    """Línea vertical desde el tobillo — mide desviación de hombro y oreja."""
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Imagen inválida"})

    detector = PoseDetector()
    try:
        lm = detector.detect(img)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Elegir el lado más visible
    left_vis  = lm["left_hip_vis"]  + lm["left_knee_vis"]  + lm["left_ankle_vis"]
    right_vis = lm["right_hip_vis"] + lm["right_knee_vis"] + lm["right_ankle_vis"]
    side = "left" if left_vis >= right_vis else "right"

    ankle    = lm[f"{side}_ankle"]
    shoulder = lm[f"{side}_shoulder"]
    ear      = lm[f"{side}_ear"]
    nose     = lm["nose"]

    # Referencia: X del tobillo
    ref_x = ankle[0]
    nose_x = nose[0]

    # Dirección de la cara (positivo = paciente mira hacia la derecha en imagen)
    face_dir = 1 if nose_x > shoulder[0] else -1

    # Escala: distancia vertical hombro-tobillo
    scale = max(abs(shoulder[1] - ankle[1]), 50)

    shoulder_ant = face_dir * (shoulder[0] - ref_x) / scale * 100  # % de la altura
    ear_ant      = face_dir * (ear[0]      - ref_x) / scale * 100

    THRESH = 8.0
    if abs(shoulder_ant) < THRESH and abs(ear_ant) < THRESH:
        classification = "Normal"
    elif shoulder_ant > THRESH and ear_ant > THRESH:
        classification = "Proyección anterior de tronco y cabeza"
    elif shoulder_ant < -THRESH and ear_ant < -THRESH:
        classification = "Proyección posterior de tronco y cabeza"
    elif ear_ant > THRESH:
        classification = "Proyección anterior de la cabeza"
    elif ear_ant < -THRESH:
        classification = "Proyección posterior de la cabeza"
    elif shoulder_ant > THRESH:
        classification = "Proyección anterior del tronco"
    elif shoulder_ant < -THRESH:
        classification = "Proyección posterior del tronco"
    else:
        classification = "Desalineación postural"

    annotated = img.copy()
    line_color = (200, 0, 200)

    # Línea vertical de referencia desde tobillo hacia arriba
    top_y = max(ear[1] - 30, 0)
    cv2.line(annotated, (ref_x, ankle[1] + 20), (ref_x, top_y), line_color, 2)

    # Puntos anatómicos
    cv2.circle(annotated, ankle,    9, (0, 220, 0),   -1)
    cv2.circle(annotated, shoulder, 9, (0, 140, 255), -1)
    cv2.circle(annotated, ear,      9, (0, 0, 255),   -1)

    # Líneas de desviación horizontal
    cv2.line(annotated, (ref_x, shoulder[1]), (shoulder[0], shoulder[1]), (0, 140, 255), 2)
    cv2.line(annotated, (ref_x, ear[1]),      (ear[0],      ear[1]),      (0, 0, 255),   2)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(annotated, f"Hombro: {shoulder_ant:+.1f}%", (max(shoulder[0] - 120, 5), shoulder[1] - 10), font, 0.55, (0, 0, 0), 2)
    cv2.putText(annotated, f"Oreja: {ear_ant:+.1f}%",       (max(ear[0] - 100, 5),      ear[1] - 10),      font, 0.55, (0, 0, 0), 2)
    cv2.putText(annotated, f"Ref. tobillo", (ref_x + 5, ankle[1] + 18), font, 0.5, (0, 180, 0), 2)

    _, buffer = cv2.imencode('.png', annotated)
    annotated_b64 = base64.b64encode(buffer).decode('utf-8')

    return {
        "metrics": {
            "classification": classification,
            "shoulder_deviation_pct": round(shoulder_ant, 1),
            "ear_deviation_pct": round(ear_ant, 1),
            "side": side,
        },
        "images": {"annotated": f"data:image/png;base64,{annotated_b64}"},
    }


# -------- VERTICAL DE BARRÉ --------

_BARRE_DESCRIPTIONS = {
    "A": "Tipo A — Tren inferior desviado: caderas/tobillos desviados lateralmente, tronco superior compensado.",
    "B": "Tipo B — Tren superior desviado: hombros desviados lateralmente, tren inferior compensado.",
    "C": "Tipo C — Compensado: tren inferior y tren superior se desvían en sentidos opuestos, compensándose.",
    "D": "Tipo D — Neutro: sin desviación lateral significativa en ningún segmento corporal.",
    "E": "Tipo E — Todo el cuerpo desviado: tren inferior y tren superior se desvían hacia el mismo lado.",
}

@router.post("/analyze-alignment/frontal/")
def analyze_alignment_frontal(file: UploadFile = File(...)):
    """Vertical de Barré — clasifica desviación lateral en tipos A-E."""
    image_bytes = file.file.read()
    npimg = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if img is None:
        return JSONResponse(status_code=400, content={"error": "Imagen inválida"})

    detector = PoseDetector()
    try:
        lm = detector.detect(img)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

    # Reference line: midpoint of ankles (plumb line base)
    ank_center_x = (lm["left_ankle"][0] + lm["right_ankle"][0]) // 2
    ank_center_y = (lm["left_ankle"][1] + lm["right_ankle"][1]) // 2
    hip_center_x = (lm["left_hip"][0]  + lm["right_hip"][0])  // 2
    sh_center_x  = (lm["left_shoulder"][0] + lm["right_shoulder"][0]) // 2
    nose = lm["nose"]

    # Scale: shoulder width
    sh_width = max(abs(lm["right_shoulder"][0] - lm["left_shoulder"][0]), 50)

    # Deviations from the ankle plumb line (normalised by shoulder width → %)
    inferior_dev = (hip_center_x - ank_center_x) / sh_width * 100   # hip vs ankle
    superior_dev = (sh_center_x  - ank_center_x) / sh_width * 100   # shoulder vs ankle
    nose_dev_pct = (nose[0]      - ank_center_x) / sh_width * 100   # nose vs ankle

    THRESH = 10.0

    inf_sig = abs(inferior_dev) >= THRESH
    sup_sig = abs(superior_dev) >= THRESH

    if not inf_sig and not sup_sig:
        barre_class = "D"
    elif inf_sig and not sup_sig:
        barre_class = "A"
    elif sup_sig and not inf_sig:
        barre_class = "B"
    elif inf_sig and sup_sig:
        # Same side or opposite?
        if (inferior_dev > 0) == (superior_dev > 0):
            barre_class = "E"
        else:
            barre_class = "C"
    else:
        barre_class = "D"

    classification = f"Tipo {barre_class}"
    barre_desc = _BARRE_DESCRIPTIONS[barre_class]

    # Annotated image
    annotated = img.copy()
    font = cv2.FONT_HERSHEY_SIMPLEX
    top_y = max(lm["nose"][1] - 40, 0)

    # Plumb line from ankle center
    cv2.line(annotated, (ank_center_x, ank_center_y + 20), (ank_center_x, top_y), (200, 0, 200), 2)

    # Hip deviation
    cv2.circle(annotated, (hip_center_x, (lm["left_hip"][1] + lm["right_hip"][1]) // 2), 9, (0, 200, 80), -1)
    cv2.line(annotated, (ank_center_x, (lm["left_hip"][1] + lm["right_hip"][1]) // 2),
             (hip_center_x, (lm["left_hip"][1] + lm["right_hip"][1]) // 2), (0, 200, 80), 2)

    # Shoulder deviation
    cv2.circle(annotated, (sh_center_x, (lm["left_shoulder"][1] + lm["right_shoulder"][1]) // 2), 9, (0, 140, 255), -1)
    cv2.line(annotated, (ank_center_x, (lm["left_shoulder"][1] + lm["right_shoulder"][1]) // 2),
             (sh_center_x, (lm["left_shoulder"][1] + lm["right_shoulder"][1]) // 2), (0, 140, 255), 2)

    # Ankle center
    cv2.circle(annotated, (ank_center_x, ank_center_y), 9, (255, 200, 0), -1)

    hip_y = (lm["left_hip"][1] + lm["right_hip"][1]) // 2
    sh_y  = (lm["left_shoulder"][1] + lm["right_shoulder"][1]) // 2
    cv2.putText(annotated, f"Inf: {inferior_dev:+.1f}%", (hip_center_x + 12, hip_y - 10), font, 0.52, (0, 120, 0), 2)
    cv2.putText(annotated, f"Sup: {superior_dev:+.1f}%", (sh_center_x + 12, sh_y - 10), font, 0.52, (0, 80, 200), 2)
    cv2.putText(annotated, f"Barre: {barre_class}", (ank_center_x + 5, ank_center_y + 22), font, 0.65, (150, 0, 200), 2)

    _, buffer = cv2.imencode('.png', annotated)
    annotated_b64 = base64.b64encode(buffer).decode('utf-8')

    return {
        "metrics": {
            "classification": classification,
            "barre_class": barre_class,
            "barre_description": barre_desc,
            "inferior_deviation_pct": round(inferior_dev, 1),
            "superior_deviation_pct": round(superior_dev, 1),
            "nose_deviation_pct": round(nose_dev_pct, 1),
        },
        "images": {"annotated": f"data:image/png;base64,{annotated_b64}"},
    }


# -------- RODILLA FRONTAL --------

def _classify_knee_frontal(angle_left, angle_right):
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

    for pt in [l_ankle, l_knee, l_hip, r_ankle, r_knee, r_hip]:
        cv2.circle(annotated, pt, 8, (0, 255, 255), -1)

    cv2.line(annotated, l_hip,  l_knee,  (0, 255, 0), 3)
    cv2.line(annotated, l_knee, l_ankle, (255, 0, 0), 3)
    cv2.line(annotated, r_hip,  r_knee,  (0, 255, 0), 3)
    cv2.line(annotated, r_knee, r_ankle, (255, 0, 0), 3)

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
            "knee_angle_deg": float(angle) if angle is not None else None,
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
            "knee_angle_deg": float(angle) if angle is not None else None,
            "classification": classification,
        },
        "images": {
            "annotated": f"data:image/png;base64,{annotated_b64}"
        }
    }
