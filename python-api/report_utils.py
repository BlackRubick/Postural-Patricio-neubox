from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import base64


PRIMARY       = colors.HexColor("#0D2B4E")
ACCENT        = colors.HexColor("#1A7ABA")
ACCENT_LIGHT  = colors.HexColor("#E8F4FD")
GOLD          = colors.HexColor("#C8962E")
TEXT_DARK     = colors.HexColor("#1C1C2E")
TEXT_MID      = colors.HexColor("#4A5568")
TEXT_LIGHT    = colors.HexColor("#718096")
DIVIDER       = colors.HexColor("#CBD5E0")
WHITE         = colors.white
PAGE_BG       = colors.HexColor("#F7FAFC")
GREEN_OK      = colors.HexColor("#16a34a")
RED_NO        = colors.HexColor("#dc2626")
GRAY_NA       = colors.HexColor("#94a3b8")

MARGIN_L = 48
MARGIN_R = 48
COL_WIDTH = letter[0] - MARGIN_L - MARGIN_R

IMG_W = 340
IMG_H = 260


def draw_background(c, width, height):
    c.setFillColor(PAGE_BG)
    c.rect(0, 0, width, height, fill=1, stroke=0)


def draw_header(c, width, height):
    c.setFillColor(PRIMARY)
    c.rect(0, height - 72, width, 72, fill=1, stroke=0)

    c.setFillColor(GOLD)
    c.rect(0, height - 75, width, 3, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(MARGIN_L, height - 46, "NEXO POSTURAL")

    c.setFillColor(ACCENT_LIGHT)
    c.setFont("Helvetica", 9)
    c.drawString(MARGIN_L, height - 62, "Análisis Clínico Postural  ·  Reporte Profesional")

    return height - 90  # y inicial tras header


def draw_footer(c, width, page_num):
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.6)
    c.line(MARGIN_L, 36, width - MARGIN_R, 36)

    c.setFillColor(TEXT_LIGHT)
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN_L, 22, "Nexo Postural  ·  Documento clínico confidencial")
    c.drawRightString(width - MARGIN_R, 22, f"Página {page_num}")


def draw_section_title(c, y, title, width):
    c.setFillColor(ACCENT_LIGHT)
    c.roundRect(MARGIN_L, y - 4, COL_WIDTH, 24, 3, fill=1, stroke=0)

    c.setFillColor(ACCENT)
    c.rect(MARGIN_L, y - 4, 4, 24, fill=1, stroke=0)

    c.setFillColor(PRIMARY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_L + 12, y + 7, title.upper())
    return y - 34


def draw_patient_card(c, y, paciente, fecha, width):
    card_h = 58
    c.setFillColor(DIVIDER)
    c.roundRect(MARGIN_L + 2, y - card_h - 2, COL_WIDTH, card_h, 5, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.roundRect(MARGIN_L, y - card_h, COL_WIDTH, card_h, 5, fill=1, stroke=0)
    c.setFillColor(ACCENT)
    c.roundRect(MARGIN_L, y - card_h, 6, card_h, 5, fill=1, stroke=0)
    c.rect(MARGIN_L, y - card_h, 3, card_h, fill=1, stroke=0)

    c.setFillColor(TEXT_LIGHT)
    c.setFont("Helvetica", 7.5)
    c.drawString(MARGIN_L + 16, y - 16, "PACIENTE")
    c.drawString(MARGIN_L + 230, y - 16, "FECHA")

    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 12)
    nombre = paciente.get("nombre", "N/A")
    c.drawString(MARGIN_L + 16, y - 30, nombre)

    c.setFont("Helvetica", 11)
    c.drawString(MARGIN_L + 230, y - 30, fecha)

    extras = [("edad", "Edad"), ("sexo", "Sexo"), ("id", "ID")]
    ex_x = MARGIN_L + 16
    c.setFillColor(TEXT_MID)
    c.setFont("Helvetica", 8.5)
    extra_parts = [f"{label}: {paciente.get(key)}" for key, label in extras if paciente.get(key)]
    if extra_parts:
        c.drawString(ex_x, y - 46, "  ·  ".join(extra_parts))

    return y - card_h - 16


def draw_report_title_block(c, y, width):
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN_L, y, "Reporte de Análisis Clínico")
    c.setFillColor(GOLD)
    c.rect(MARGIN_L, y - 5, 44, 2, fill=1, stroke=0)
    return y - 22


def draw_metric_row(c, y, text, width, alternate=False):
    row_h = 22
    padding_top = 6

    if alternate:
        c.setFillColor(colors.HexColor("#EDF2F7"))
        c.rect(MARGIN_L + 10, y - row_h, COL_WIDTH - 10, row_h, fill=1, stroke=0)

    bullet_y = y - (row_h / 2)
    c.setFillColor(ACCENT)
    c.circle(MARGIN_L + 22, bullet_y, 2.8, fill=1, stroke=0)

    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica", 9.5)
    c.drawString(MARGIN_L + 32, bullet_y - 3.5, text)

    return y - row_h


def draw_rasgo_row(c, y, nombre, cumple, auto_detected=True, alternate=False):
    """Fila de rasgo con palomita o X según cumple."""
    row_h = 18

    if alternate:
        c.setFillColor(colors.HexColor("#EDF2F7"))
        c.rect(MARGIN_L + 10, y - row_h, COL_WIDTH - 10, row_h, fill=1, stroke=0)

    center_y = y - (row_h / 2)

    if not auto_detected:
        # Círculo gris: no evaluado automáticamente
        c.setFillColor(GRAY_NA)
        c.circle(MARGIN_L + 22, center_y, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(MARGIN_L + 22, center_y - 2.5, "?")
    elif cumple:
        # Círculo verde: cumple
        c.setFillColor(GREEN_OK)
        c.circle(MARGIN_L + 22, center_y, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(MARGIN_L + 22, center_y - 2.5, "✓")
    else:
        # Círculo rojo: no cumple
        c.setFillColor(RED_NO)
        c.circle(MARGIN_L + 22, center_y, 5, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(MARGIN_L + 22, center_y - 2.5, "✗")

    color = GREEN_OK if (cumple and auto_detected) else (GRAY_NA if not auto_detected else RED_NO)
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica", 8.5)
    c.drawString(MARGIN_L + 34, center_y - 3, nombre)

    return y - row_h


def draw_percentage_bar(c, y, porcentaje, label="Porcentaje de cadena"):
    """Barra de progreso con porcentaje."""
    bar_h = 14
    bar_w = COL_WIDTH - 20
    bar_x = MARGIN_L + 10

    c.setFillColor(TEXT_MID)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(bar_x, y, label)
    y -= 16

    # Background bar
    c.setFillColor(colors.HexColor("#E2E8F0"))
    c.roundRect(bar_x, y, bar_w, bar_h, 4, fill=1, stroke=0)

    # Progress bar
    fill_w = bar_w * (porcentaje / 100)
    if fill_w > 0:
        if porcentaje >= 50:
            fill_color = GREEN_OK
        elif porcentaje >= 25:
            fill_color = colors.HexColor("#d97706")
        else:
            fill_color = RED_NO
        c.setFillColor(fill_color)
        c.roundRect(bar_x, y, fill_w, bar_h, 4, fill=1, stroke=0)

    # Percentage text
    c.setFillColor(TEXT_DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawRightString(bar_x + bar_w - 4, y + 3, f"{porcentaje:.0f}%")

    return y - bar_h - 10


def new_page(c, width, height, page_num):
    c.showPage()
    draw_background(c, width, height)
    draw_footer(c, width, page_num)
    y = draw_header(c, width, height)
    return y


def _draw_image_block(c, y, width, height, page_num, img_b64, titulo):
    """Dibuja un bloque de imagen con título. Retorna (y_nuevo, page_num)."""
    try:
        img_bytes = base64.b64decode(img_b64)
        img_reader = ImageReader(BytesIO(img_bytes))

        if y < IMG_H + 60:
            page_num += 1
            y = new_page(c, width, height, page_num)
            y -= 10

        c.setStrokeColor(DIVIDER)
        c.setLineWidth(0.8)
        c.setFillColor(WHITE)
        c.roundRect(MARGIN_L + 8, y - IMG_H - 24, IMG_W + 8, IMG_H + 22, 5, fill=1, stroke=1)
        c.setFillColor(PRIMARY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(MARGIN_L + 16, y - 14, titulo)
        c.drawImage(
            img_reader,
            MARGIN_L + 12, y - IMG_H - 18,
            width=IMG_W, height=IMG_H,
            preserveAspectRatio=True,
            mask='auto'
        )
        y -= IMG_H + 32

        if y < 150:
            page_num += 1
            y = new_page(c, width, height, page_num)
            y -= 10
    except Exception as e:
        c.setFillColor(colors.HexColor("#FFF5F5"))
        c.roundRect(MARGIN_L + 8, y - 20, COL_WIDTH - 8, 20, 3, fill=1, stroke=0)
        c.setFillColor(colors.HexColor("#C53030"))
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN_L + 16, y - 13, f"Error al cargar imagen: {e}")
        y -= 28
    return y, page_num


# ─── FUNCIÓN PRINCIPAL ───────────────────────────────────────────────────────

def generate_report_pdf(data):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    page_num = 1

    draw_background(c, width, height)
    draw_footer(c, width, page_num)
    y = draw_header(c, width, height)

    y -= 10
    y = draw_report_title_block(c, y, width)
    y -= 14

    paciente = data.get("paciente", {})
    fecha = data.get("fecha", "N/A")
    y = draw_patient_card(c, y, paciente, fecha, width)
    y -= 10

    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.8)
    c.line(MARGIN_L, y, width - MARGIN_R, y)
    y -= 18

    analisis = data.get("analisis", [])

    for bloque in analisis:
        if y < 140:
            page_num += 1
            y = new_page(c, width, height, page_num)
            y -= 10

        y = draw_section_title(c, y, bloque.get("titulo", "Análisis"), width)
        y -= 4

        titulo = bloque.get("titulo", "").lower()
        es_cadena = "cadena" in titulo

        # Tipo de cadena destacado
        if es_cadena and bloque.get("tipo"):
            c.setFillColor(GOLD)
            c.setFont("Helvetica-Bold", 10.5)
            c.drawString(MARGIN_L + 16, y, f"Tipo de cadena: {bloque['tipo']}")
            y -= 22

        # Explicación
        if bloque.get("explicacion"):
            exp_text = bloque["explicacion"]
            c.setFillColor(colors.HexColor("#EBF8FF"))
            c.roundRect(MARGIN_L + 8, y - 18, COL_WIDTH - 8, 22, 3, fill=1, stroke=0)
            c.setFillColor(ACCENT)
            c.setFont("Helvetica-BoldOblique", 8)
            c.drawString(MARGIN_L + 16, y - 7, "Explicación:")
            c.setFillColor(TEXT_MID)
            c.setFont("Helvetica", 8.5)
            max_chars = 90
            if len(exp_text) > max_chars:
                exp_text = exp_text[:max_chars] + "…"
            c.drawString(MARGIN_L + 80, y - 7, exp_text)
            y -= 28

        # Métricas normales (no cadena)
        if bloque.get("metricas") and not es_cadena:
            c.setFillColor(TEXT_LIGHT)
            c.setFont("Helvetica", 7.5)
            c.drawString(MARGIN_L + 10, y, "INDICADORES")
            y -= 18
            for idx, met in enumerate(bloque["metricas"]):
                if y < 100:
                    page_num += 1
                    y = new_page(c, width, height, page_num)
                    y -= 10
                y = draw_metric_row(c, y, met, width, alternate=(idx % 2 == 0))

        # Rasgos detallados de cadena miofascial (Corrección 5)
        if es_cadena and bloque.get("rasgos_detallados"):
            rasgos = bloque["rasgos_detallados"]
            c.setFillColor(TEXT_LIGHT)
            c.setFont("Helvetica", 7.5)
            c.drawString(MARGIN_L + 10, y, "RASGOS DE LA CADENA")
            y -= 16
            for idx, rasgo in enumerate(rasgos):
                if y < 100:
                    page_num += 1
                    y = new_page(c, width, height, page_num)
                    y -= 10
                y = draw_rasgo_row(
                    c, y,
                    rasgo.get("nombre", ""),
                    rasgo.get("cumple", False),
                    rasgo.get("auto", True),
                    alternate=(idx % 2 == 0)
                )
            y -= 6
            # Barra de porcentaje
            if y < 80:
                page_num += 1
                y = new_page(c, width, height, page_num)
                y -= 10
            porcentaje = bloque.get("porcentaje", 0)
            y = draw_percentage_bar(c, y, porcentaje)

        y -= 10

        # Imagen original de cadena miofascial
        if es_cadena and data.get("imagen_original"):
            if y < IMG_H + 60:
                page_num += 1
                y = new_page(c, width, height, page_num)
                y -= 10
            y, page_num = _draw_image_block(c, y, width, height, page_num,
                                             data["imagen_original"], "Imagen original subida")

        # Imágenes asociadas al bloque
        for img_dict in bloque.get("imagenes", []):
            img_titulo = img_dict.get("titulo", "Imagen")
            img_b64 = img_dict.get("base64")
            if img_b64:
                y, page_num = _draw_image_block(c, y, width, height, page_num, img_b64, img_titulo)

        y -= 8

        # Separador entre bloques
        c.setStrokeColor(DIVIDER)
        c.setLineWidth(0.4)
        c.setDash(3, 3)
        c.line(MARGIN_L + 20, y, width - MARGIN_R - 20, y)
        c.setDash()
        y -= 16

    # Firma
    if y < 80:
        page_num += 1
        y = new_page(c, width, height, page_num)
        y -= 10

    y -= 10
    c.setStrokeColor(DIVIDER)
    c.setLineWidth(0.6)
    c.line(MARGIN_L, y, width - MARGIN_R, y)
    y -= 16
    c.setFillColor(TEXT_LIGHT)
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(MARGIN_L, y, "Este documento fue generado automáticamente por Nexo Postural.")
    c.drawRightString(width - MARGIN_R, y, f"Total de análisis: {len(analisis)}")

    c.save()
    buffer.seek(0)
    return buffer.getvalue()
