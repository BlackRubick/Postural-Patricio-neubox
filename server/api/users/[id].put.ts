import bcrypt from 'bcryptjs'
import { prisma } from '~/server/utils/prisma'
import { requireAdmin } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  await requireAdmin(event)
  const id = Number(getRouterParam(event, 'id'))
  const body = await readBody(event)

  if (!body.email?.trim()) {
    throw createError({ statusCode: 400, message: 'El email es requerido' })
  }

  const data: Record<string, unknown> = {
    email: body.email.trim().toLowerCase(),
    name: body.name?.trim() || null,
    role: body.role === 'admin' ? 'admin' : 'doctor',
  }

  if (body.password) {
    data.password = await bcrypt.hash(body.password, 10)
  }

  return prisma.user.update({
    where: { id },
    data,
    select: { id: true, email: true, name: true, role: true, createdAt: true },
  })
})
