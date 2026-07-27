import { prisma } from '~/server/utils/prisma'
import { requireAuth } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const user = await requireAuth(event)

  const analysis = await prisma.analysis.findUnique({
    where: { id },
    select: { patient: { select: { userId: true } } },
  })
  if (!analysis) throw createError({ statusCode: 404, message: 'Análisis no encontrado' })
  if (user.role !== 'admin' && analysis.patient.userId !== user.id) {
    throw createError({ statusCode: 403, message: 'Sin acceso a este análisis' })
  }

  await prisma.analysis.delete({ where: { id } })
  return { ok: true }
})
