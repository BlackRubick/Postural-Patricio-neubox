import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody(event)
  return prisma.analysis.update({
    where: { id },
    data: {
      tipoTest: body.tipoTest,
      fecha: body.fecha,
      completado: body.completado,
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
    },
  })
})
