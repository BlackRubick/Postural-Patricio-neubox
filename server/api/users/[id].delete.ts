import { prisma } from '~/server/utils/prisma'
import { requireAdmin } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  const admin = await requireAdmin(event)
  const id = Number(getRouterParam(event, 'id'))

  if (admin.id === id) {
    throw createError({ statusCode: 400, message: 'No puedes eliminar tu propia cuenta' })
  }

  await prisma.user.delete({ where: { id } })
  return { ok: true }
})
