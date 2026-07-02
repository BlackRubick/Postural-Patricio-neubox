import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const patientId = Number(getRouterParam(event, 'id'))
  return prisma.analysis.findMany({
    where: { patientId },
    orderBy: { createdAt: 'desc' },
  })
})
