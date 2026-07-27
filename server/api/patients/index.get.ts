import { prisma } from '~/server/utils/prisma'
import { requireAuth } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event)
  const where = user.role === 'admin' ? {} : { userId: user.id }

  return prisma.patient.findMany({
    where,
    include: { analyses: true },
    orderBy: { createdAt: 'desc' },
  })
})
