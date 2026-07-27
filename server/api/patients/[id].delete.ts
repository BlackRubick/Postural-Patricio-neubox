import { prisma } from '~/server/utils/prisma'
import { requirePatientAccess } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  await requirePatientAccess(event, id)

  await prisma.patient.delete({ where: { id } })
  return { ok: true }
})
