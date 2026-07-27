import { prisma } from '~/server/utils/prisma'
import { requirePatientAccess } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const patientId = Number(getRouterParam(event, 'id'))
  await requirePatientAccess(event, patientId)

  return prisma.analysis.findMany({
    where: { patientId },
    orderBy: { createdAt: 'desc' },
  })
})
