import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const patient = await prisma.patient.findUnique({
    where: { id },
    include: { analyses: true },
  })
  if (!patient) throw createError({ statusCode: 404, message: 'Paciente no encontrado' })
  return patient
})
