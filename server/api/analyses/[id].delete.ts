import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  await prisma.analysis.delete({ where: { id } })
  return { ok: true }
})
