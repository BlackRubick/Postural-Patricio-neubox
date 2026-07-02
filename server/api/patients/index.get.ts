import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async () => {
  return prisma.patient.findMany({
    include: { analyses: true },
    orderBy: { createdAt: 'desc' },
  })
})
