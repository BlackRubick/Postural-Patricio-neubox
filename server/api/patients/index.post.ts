import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  return prisma.patient.create({
    data: {
      nombre: body.nombre,
      edad: Number(body.edad),
      sexo: body.sexo,
      altura: body.altura ? Number(body.altura) : null,
    },
    include: { analyses: true },
  })
})
