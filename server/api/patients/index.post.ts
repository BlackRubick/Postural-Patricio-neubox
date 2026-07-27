import { prisma } from '~/server/utils/prisma'
import { requireAuth } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const user = await requireAuth(event)
  const body = await readBody(event)

  return prisma.patient.create({
    data: {
      nombre: body.nombre,
      edad: Number(body.edad),
      sexo: body.sexo,
      altura: body.altura ? Number(body.altura) : null,
      userId: user.id,
    },
    include: { analyses: true },
  })
})
