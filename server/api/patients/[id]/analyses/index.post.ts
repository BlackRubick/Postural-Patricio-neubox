import { prisma } from '~/server/utils/prisma'
import { requirePatientAccess } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const patientId = Number(getRouterParam(event, 'id'))
  await requirePatientAccess(event, patientId)

  const body = await readBody(event)
  return prisma.analysis.create({
    data: {
      patientId,
      tipoTest: body.tipoTest ?? 'Podometría digital',
      fecha: body.fecha ?? new Date().toISOString().slice(0, 10),
      completado: body.completado ?? false,
      pdfUrl: body.pdfUrl ?? null,
      podometriaResult: body.podometriaResult ?? null,
      podometriaDebugImg: body.podometriaDebugImg ?? null,
      podometriaHuella: body.podometriaHuella ?? null,
      frontalResult: body.frontalResult ?? null,
      frontalDebugImg: body.frontalDebugImg ?? null,
      sagitalResult: body.sagitalResult ?? null,
      sagitalDebugImg: body.sagitalDebugImg ?? null,
      miofascialResult: body.miofascialResult ?? null,
      miofascialDebugImg: body.miofascialDebugImg ?? null,
      miofascialImagenOriginal: body.miofascialImagenOriginal ?? null,
      alineacionSagitalResult: body.alineacionSagitalResult ?? null,
      alineacionSagitalDebugImg: body.alineacionSagitalDebugImg ?? null,
      alineacionFrontalResult: body.alineacionFrontalResult ?? null,
      alineacionFrontalDebugImg: body.alineacionFrontalDebugImg ?? null,
      notas: body.notas ?? null,
      miofascialFrontalImg: body.miofascialFrontalImg ?? null,
      miofascialPosteriorImg: body.miofascialPosteriorImg ?? null,
    },
  })
})
