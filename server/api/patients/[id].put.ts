import { prisma } from '~/server/utils/prisma'
import { requirePatientAccess } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  await requirePatientAccess(event, id)

  const body = await readBody(event)
  return prisma.patient.update({
    where: { id },
    data: {
      nombre: body.nombre,
      edad: Number(body.edad),
      sexo: body.sexo,
      altura: body.altura ? Number(body.altura) : null,
    },
    include: { analyses: true },
  })
})
