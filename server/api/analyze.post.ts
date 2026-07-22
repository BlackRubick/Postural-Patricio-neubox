import Anthropic from '@anthropic-ai/sdk'
import sharp from 'sharp'
import { readMultipartFormData } from 'h3'

type MimeType = 'image/jpeg' | 'image/png' | 'image/gif' | 'image/webp'

interface MultipartFile {
  name?: string
  data: Buffer
  type?: string
}

interface Keypoint {
  x: number
  y: number
}

// ─── Image annotation helpers ────────────────────────────────────────────────

async function annotateFootContour(imageBuffer: Buffer): Promise<string> {
  const meta = await sharp(imageBuffer).metadata()
  const w = meta.width ?? 800
  const h = meta.height ?? 600

  // Threshold the image to isolate the dark footprint
  const maskBuffer = await sharp(imageBuffer)
    .greyscale()
    .blur(2)
    .threshold(100)
    .negate()
    .toBuffer()

  // Detect edges using Laplacian kernel
  const edgeBuffer = await sharp(maskBuffer)
    .convolve({
      width: 3,
      height: 3,
      kernel: [-1, -1, -1, -1, 8, -1, -1, -1, -1],
    })
    .threshold(20)
    .toBuffer()

  // Tint edges in bright green and composite on original
  const coloredEdge = await sharp({
    create: { width: w, height: h, channels: 4, background: { r: 0, g: 0, b: 0, alpha: 0 } },
  })
    .composite([
      {
        input: await sharp(edgeBuffer)
          .ensureAlpha()
          .toBuffer(),
        blend: 'over',
      },
    ])
    .png()
    .toBuffer()

  // Overlay on original
  const annotated = await sharp(imageBuffer)
    .composite([
      {
        input: await sharp(edgeBuffer)
          .tint({ r: 0, g: 220, b: 80 })
          .ensureAlpha()
          .toBuffer(),
        blend: 'over',
      },
    ])
    .jpeg({ quality: 85 })
    .toBuffer()

  return 'data:image/jpeg;base64,' + annotated.toString('base64')
}

async function annotateWithSvg(imageBuffer: Buffer, svgContent: string): Promise<string> {
  const meta = await sharp(imageBuffer).metadata()
  const w = meta.width ?? 800
  const h = meta.height ?? 600

  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}">${svgContent}</svg>`

  const annotated = await sharp(imageBuffer)
    .composite([{ input: Buffer.from(svg), blend: 'over' }])
    .jpeg({ quality: 85 })
    .toBuffer()

  return 'data:image/jpeg;base64,' + annotated.toString('base64')
}

function kp(keypoints: Record<string, Keypoint>, name: string, w: number, h: number) {
  const p = keypoints[name]
  if (!p) return null
  return { x: Math.round(p.x * w), y: Math.round(p.y * h) }
}

async function buildKneeAnnotation(
  imageBuffer: Buffer,
  keypoints: Record<string, Keypoint>,
  angleDeg: number,
): Promise<string> {
  const meta = await sharp(imageBuffer).metadata()
  const w = meta.width ?? 800
  const h = meta.height ?? 600

  const hip = kp(keypoints, 'hip', w, h)
  const knee = kp(keypoints, 'knee', w, h)
  const ankle = kp(keypoints, 'ankle', w, h)

  if (!hip || !knee || !ankle) return ''

  const svg = `
    <line x1="${hip.x}" y1="${hip.y}" x2="${knee.x}" y2="${knee.y}" stroke="#00e066" stroke-width="3" stroke-linecap="round"/>
    <line x1="${knee.x}" y1="${knee.y}" x2="${ankle.x}" y2="${ankle.y}" stroke="#00e066" stroke-width="3" stroke-linecap="round"/>
    <circle cx="${hip.x}" cy="${hip.y}" r="6" fill="#00e066"/>
    <circle cx="${knee.x}" cy="${knee.y}" r="8" fill="#ffcc00"/>
    <circle cx="${ankle.x}" cy="${ankle.y}" r="6" fill="#00e066"/>
    <rect x="${knee.x + 10}" y="${knee.y - 18}" width="80" height="26" rx="5" fill="rgba(0,0,0,0.55)"/>
    <text x="${knee.x + 50}" y="${knee.y - 1}" text-anchor="middle" font-family="sans-serif" font-size="16" font-weight="bold" fill="#ffcc00">${angleDeg.toFixed(1)}°</text>
  `
  return annotateWithSvg(imageBuffer, svg)
}

async function buildSagitalAlignmentAnnotation(
  imageBuffer: Buffer,
  keypoints: Record<string, Keypoint>,
): Promise<string> {
  const meta = await sharp(imageBuffer).metadata()
  const w = meta.width ?? 800
  const h = meta.height ?? 600

  const ear = kp(keypoints, 'ear', w, h)
  const shoulder = kp(keypoints, 'shoulder', w, h)
  const hip = kp(keypoints, 'hip', w, h)
  const ankle = kp(keypoints, 'ankle', w, h)

  const points = [ear, shoulder, hip, ankle].filter(Boolean) as { x: number; y: number }[]
  if (points.length < 2) return ''

  // Plumb line from ear to ankle
  const topY = ear?.y ?? 20
  const botY = ankle?.y ?? h - 20
  const refX = ankle?.x ?? w / 2

  const circlesSvg = points
    .map(p => `<circle cx="${p.x}" cy="${p.y}" r="6" fill="#00e066" stroke="#fff" stroke-width="1.5"/>`)
    .join('')

  const linesSvg = points
    .slice(0, -1)
    .map((p, i) => {
      const next = points[i + 1]
      return `<line x1="${p.x}" y1="${p.y}" x2="${next.x}" y2="${next.y}" stroke="#00e066" stroke-width="2.5" stroke-linecap="round"/>`
    })
    .join('')

  const svg = `
    <line x1="${refX}" y1="${topY}" x2="${refX}" y2="${botY}" stroke="#ff4d4d" stroke-width="2" stroke-dasharray="8,5"/>
    ${linesSvg}
    ${circlesSvg}
  `
  return annotateWithSvg(imageBuffer, svg)
}

async function buildBarreAnnotation(
  imageBuffer: Buffer,
  keypoints: Record<string, Keypoint>,
): Promise<string> {
  const meta = await sharp(imageBuffer).metadata()
  const w = meta.width ?? 800
  const h = meta.height ?? 600

  const head = kp(keypoints, 'head', w, h)
  const navel = kp(keypoints, 'navel', w, h)
  const feet = kp(keypoints, 'feet', w, h)

  const centerX = feet?.x ?? Math.round(w / 2)
  const topY = head?.y ?? 20
  const botY = feet?.y ?? h - 20

  const markers = [head, navel, feet]
    .filter(Boolean)
    .map((p) => {
      const dev = p!.x - centerX
      const color = Math.abs(dev) < 8 ? '#00e066' : '#ff4d4d'
      return `
        <circle cx="${p!.x}" cy="${p!.y}" r="7" fill="${color}" stroke="#fff" stroke-width="1.5"/>
        <line x1="${centerX}" y1="${p!.y}" x2="${p!.x}" y2="${p!.y}" stroke="${color}" stroke-width="1.5" stroke-dasharray="4,3"/>
      `
    })
    .join('')

  const svg = `
    <line x1="${centerX}" y1="${topY}" x2="${centerX}" y2="${botY}" stroke="#ff4d4d" stroke-width="2.5" stroke-dasharray="10,6"/>
    ${markers}
  `
  return annotateWithSvg(imageBuffer, svg)
}

// ─── Claude helpers ───────────────────────────────────────────────────────────

function toBase64Image(part: MultipartFile): { type: 'base64'; media_type: MimeType; data: string } {
  return {
    type: 'base64',
    media_type: (part.type || 'image/jpeg') as MimeType,
    data: part.data.toString('base64'),
  }
}

function buildImageContent(source: ReturnType<typeof toBase64Image>) {
  return { type: 'image' as const, source }
}

function extractJson(text: string): unknown {
  const codeBlock = text.match(/```json\s*([\s\S]*?)```/)
  if (codeBlock) return JSON.parse(codeBlock[1])
  const jsonMatch = text.match(/(\{[\s\S]*\})/)
  if (jsonMatch) return JSON.parse(jsonMatch[1])
  throw new Error('No JSON encontrado en la respuesta de Claude')
}

async function callClaude(
  client: Anthropic,
  images: ReturnType<typeof buildImageContent>[],
  prompt: string,
): Promise<unknown> {
  const stream = await client.messages.stream({
    model: 'claude-opus-4-8',
    max_tokens: 8000,
    thinking: { type: 'adaptive' },
    messages: [
      {
        role: 'user',
        content: [...images, { type: 'text', text: prompt }],
      },
    ],
  })
  const msg = await stream.finalMessage()
  const textBlock = msg.content.find(b => b.type === 'text')
  if (!textBlock || textBlock.type !== 'text') throw new Error('Sin respuesta de texto')
  return extractJson(textBlock.text)
}

// ─── Prompts ──────────────────────────────────────────────────────────────────

const PROMPTS: Record<string, string> = {
  podometria: `Eres un especialista en podología. Analiza esta imagen de huella plantar (mancha oscura sobre fondo claro).

Determina:
1. Si hay uno o dos pies visibles
2. El tipo de pie: Normal, Plano o Cavo (según el índice plantar de Hernández Corvo)
3. El índice plantar estimado (0-1, donde >0.45 es plano, <0.3 es cavo)

Responde SOLO con JSON válido:
\`\`\`json
{
  "metrics": [
    {
      "side": "right",
      "classification": "Normal",
      "plantar_index": 0.42,
      "calibrated": false,
      "x_width_px": 120,
      "y_width_px": 80,
      "x_width_cm": null,
      "y_width_cm": null
    }
  ]
}
\`\`\`
Si hay dos pies incluye dos objetos. side puede ser "right", "left" o "unknown".`,

  frontal: `Eres un especialista en fisioterapia. Analiza esta imagen de vista frontal de rodillas.

Determina el ángulo tibiofemoral y la clasificación. Además estima las coordenadas de los puntos clave como proporción de la imagen (0.0 = izquierda/arriba, 1.0 = derecha/abajo).

Responde SOLO con JSON válido:
\`\`\`json
{
  "metrics": {
    "classification": "Normal",
    "knee_angle_deg": 178.5
  },
  "keypoints": {
    "hip": { "x": 0.45, "y": 0.28 },
    "knee": { "x": 0.44, "y": 0.55 },
    "ankle": { "x": 0.43, "y": 0.82 }
  }
}
\`\`\`
classification: "Normal" (170-180°), "Varo" (>180°, rodillas en O) o "Valgo" (<170°, rodillas en X).`,

  sagital: `Eres un especialista en fisioterapia. Analiza esta imagen de vista sagital (lateral) de la rodilla.

Determina el ángulo tibiofemoral sagital y estima coordenadas de puntos clave como proporción de la imagen.

Responde SOLO con JSON válido:
\`\`\`json
{
  "metrics": {
    "classification": "Normal",
    "knee_angle_deg": 175.0
  },
  "keypoints": {
    "hip": { "x": 0.48, "y": 0.30 },
    "knee": { "x": 0.47, "y": 0.55 },
    "ankle": { "x": 0.46, "y": 0.80 }
  }
}
\`\`\`
classification: "Normal" (~180°), "Recurvatum" (hiperextensión >180°) o "Flexum" (flexión persistente <165°).`,

  'alineacion-sagital': `Eres un especialista en fisioterapia. Analiza esta imagen de vista lateral (sagital) del cuerpo completo.

Evalúa la alineación postural vertical y estima coordenadas de puntos clave como proporción de la imagen.

Responde SOLO con JSON válido:
\`\`\`json
{
  "metrics": {
    "classification": "Normal",
    "shoulder_deviation_pct": 2.5,
    "ear_deviation_pct": 1.8,
    "side": "anterior"
  },
  "keypoints": {
    "ear": { "x": 0.47, "y": 0.12 },
    "shoulder": { "x": 0.44, "y": 0.25 },
    "hip": { "x": 0.50, "y": 0.50 },
    "ankle": { "x": 0.49, "y": 0.88 }
  }
}
\`\`\`
classification: "Normal", "Inclinación anterior" o "Inclinación posterior". side: "anterior", "posterior" o "none".`,

  'vertical-barre': `Eres un especialista en fisioterapia. Analiza esta imagen de vista posterior del cuerpo completo.

Evalúa la simetría respecto a la línea vertical de Barré y estima coordenadas de puntos clave como proporción de la imagen.

Responde SOLO con JSON válido:
\`\`\`json
{
  "metrics": {
    "classification": "Normal",
    "barre_class": "Tipo I",
    "barre_description": "Desviación leve de la cabeza hacia la derecha",
    "nose_deviation_pct": 1.2,
    "inferior_deviation_pct": 3.5,
    "superior_deviation_pct": 2.1
  },
  "keypoints": {
    "head": { "x": 0.52, "y": 0.08 },
    "navel": { "x": 0.48, "y": 0.50 },
    "feet": { "x": 0.50, "y": 0.90 }
  }
}
\`\`\`
classification: "Normal" o "Alterado". barre_class: "Normal", "Tipo I" (superior), "Tipo II" (inferior) o "Tipo III" (bilateral).`,

  miofascial: `Eres un especialista en fisioterapia y cadenas musculares (método Busquet). Analiza estas imágenes posturales.

Las cadenas son: "Cadena Posterior", "Cadena Anterior", "Cadena de Apertura", "Cadena de Cierre", "Cadena Inspiratoria", "Cadena Espiratoria", "Cadena Estática Derecha", "Cadena Estática Izquierda".

Responde SOLO con JSON válido:
\`\`\`json
{
  "chain": "Cadena Posterior",
  "explanation": "Descripción detallada del patrón postural y por qué corresponde a esta cadena.",
  "rasgos": ["Hiperlordosis lumbar", "Hombros proyectados", "Cabeza adelantada"],
  "rasgos_detallados": [
    { "nombre": "Hiperlordosis lumbar", "cumple": true, "auto": "Curvatura lumbar aumentada visualmente" },
    { "nombre": "Hombros proyectados", "cumple": true, "auto": "Hombros en protracción visible" },
    { "nombre": "Cabeza adelantada", "cumple": false, "auto": "Posición cervical dentro de la norma" },
    { "nombre": "Rodillas en recurvatum", "cumple": false, "auto": "No se aprecia hiperextensión de rodillas" }
  ],
  "porcentaje": 78
}
\`\`\``,
}

// ─── Response builders ────────────────────────────────────────────────────────

async function buildPodometria(data: unknown, imageBuffer: Buffer) {
  const d = data as Record<string, unknown>
  const raw = Array.isArray(d.metrics) ? d.metrics : [d.metrics]
  const annotated = await annotateFootContour(imageBuffer)
  return {
    metrics: (raw as Record<string, unknown>[]).map(m => ({
      side: m.side ?? 'right',
      classification: m.classification ?? 'Normal',
      plantar_index: Number(m.plantar_index ?? 0),
      calibrated: Boolean(m.calibrated ?? false),
      x_width_px: Number(m.x_width_px ?? 0),
      y_width_px: Number(m.y_width_px ?? 0),
      x_width_cm: m.x_width_cm != null ? Number(m.x_width_cm) : null,
      y_width_cm: m.y_width_cm != null ? Number(m.y_width_cm) : null,
    })),
    images: { annotated },
  }
}

async function buildKnee(data: unknown, imageBuffer: Buffer) {
  const d = data as Record<string, unknown>
  const m = (d.metrics ?? d) as Record<string, unknown>
  const kps = (d.keypoints ?? {}) as Record<string, Keypoint>
  const angleDeg = Number(m.knee_angle_deg ?? 180)
  const annotated = await buildKneeAnnotation(imageBuffer, kps, angleDeg)
  return {
    metrics: {
      classification: m.classification ?? 'Normal',
      knee_angle_deg: angleDeg,
    },
    images: { annotated: annotated || null },
  }
}

async function buildAlineacionSagital(data: unknown, imageBuffer: Buffer) {
  const d = data as Record<string, unknown>
  const m = (d.metrics ?? d) as Record<string, unknown>
  const kps = (d.keypoints ?? {}) as Record<string, Keypoint>
  const annotated = await buildSagitalAlignmentAnnotation(imageBuffer, kps)
  return {
    metrics: {
      classification: m.classification ?? 'Normal',
      shoulder_deviation_pct: Number(m.shoulder_deviation_pct ?? 0),
      ear_deviation_pct: Number(m.ear_deviation_pct ?? 0),
      side: m.side ?? 'none',
    },
    images: { annotated: annotated || null },
  }
}

async function buildVerticalBarre(data: unknown, imageBuffer: Buffer) {
  const d = data as Record<string, unknown>
  const m = (d.metrics ?? d) as Record<string, unknown>
  const kps = (d.keypoints ?? {}) as Record<string, Keypoint>
  const annotated = await buildBarreAnnotation(imageBuffer, kps)
  return {
    metrics: {
      classification: m.classification ?? 'Normal',
      barre_class: m.barre_class ?? m.classification ?? 'Normal',
      barre_description: m.barre_description ?? '',
      nose_deviation_pct: Number(m.nose_deviation_pct ?? 0),
      inferior_deviation_pct: Number(m.inferior_deviation_pct ?? 0),
      superior_deviation_pct: Number(m.superior_deviation_pct ?? 0),
    },
    images: { annotated: annotated || null },
  }
}

function buildMiofascial(data: unknown) {
  const d = data as Record<string, unknown>
  return {
    chain: d.chain ?? '',
    explanation: d.explanation ?? '',
    rasgos: Array.isArray(d.rasgos) ? d.rasgos : [],
    rasgos_detallados: Array.isArray(d.rasgos_detallados) ? d.rasgos_detallados : [],
    porcentaje: Number(d.porcentaje ?? 0),
    imagen_original: null,
    imagen_frontal: null,
    imagen_posterior: null,
    images: { annotated: null },
  }
}

// ─── Handler ──────────────────────────────────────────────────────────────────

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  if (!config.anthropicApiKey) {
    throw createError({ statusCode: 500, statusMessage: 'ANTHROPIC_API_KEY no configurada' })
  }

  const parts = await readMultipartFormData(event)
  if (!parts) throw createError({ statusCode: 400, statusMessage: 'No se recibió form data' })

  const getString = (name: string) => parts.find(p => p.name === name)?.data.toString()
  const getFile = (name: string) => parts.find(p => p.name === name)

  const analysisType = getString('type')
  const fileMain = getFile('file')

  if (!analysisType || !fileMain) {
    throw createError({ statusCode: 400, statusMessage: 'Faltan campos: type y file son requeridos' })
  }

  const prompt = PROMPTS[analysisType]
  if (!prompt) {
    throw createError({ statusCode: 400, statusMessage: `Tipo de análisis desconocido: ${analysisType}` })
  }

  const client = new Anthropic({ apiKey: config.anthropicApiKey })
  const images = [buildImageContent(toBase64Image(fileMain))]

  if (analysisType === 'miofascial') {
    const fileFrontal = getFile('file_frontal')
    const filePosterior = getFile('file_posterior')
    if (fileFrontal) images.push(buildImageContent(toBase64Image(fileFrontal)))
    if (filePosterior) images.push(buildImageContent(toBase64Image(filePosterior)))
  }

  const rawData = await callClaude(client, images, prompt)

  switch (analysisType) {
    case 'podometria': return buildPodometria(rawData, fileMain.data)
    case 'frontal': return buildKnee(rawData, fileMain.data)
    case 'sagital': return buildKnee(rawData, fileMain.data)
    case 'alineacion-sagital': return buildAlineacionSagital(rawData, fileMain.data)
    case 'vertical-barre': return buildVerticalBarre(rawData, fileMain.data)
    case 'miofascial': return buildMiofascial(rawData)
    default: throw createError({ statusCode: 400, statusMessage: 'Tipo no manejado' })
  }
})
