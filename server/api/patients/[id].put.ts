import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody(event)
  return prisma.patient.update({
    where: { id },
    data: {
      nombre: body.nombre,
      edad: Number(body.edad),
      sexo: body.sexo,
    },
    include: { analyses: true },
  })
})
