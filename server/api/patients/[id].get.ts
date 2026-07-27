import { prisma } from '~/server/utils/prisma'
import { requirePatientAccess } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  await requirePatientAccess(event, id)

  const patient = await prisma.patient.findUnique({
    where: { id },
    include: { analyses: true },
  })
  if (!patient) throw createError({ statusCode: 404, message: 'Paciente no encontrado' })
  return patient
})
