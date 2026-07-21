import bcrypt from 'bcryptjs'
import { prisma } from '~/server/utils/prisma'
import { requireAdmin } from '~/server/utils/auth'

export default defineEventHandler(async (event) => {
  await requireAdmin(event)
  const body = await readBody(event)
  const { email, password, name, role } = body

  if (!email?.trim() || !password) {
    throw createError({ statusCode: 400, message: 'Email y contraseña son requeridos' })
  }

  const existing = await prisma.user.findUnique({ where: { email } })
  if (existing) throw createError({ statusCode: 409, message: 'Ya existe un usuario con ese email' })

  const hashed = await bcrypt.hash(password, 10)
  return prisma.user.create({
    data: {
      email: email.trim().toLowerCase(),
      password: hashed,
      name: name?.trim() || null,
      role: role === 'admin' ? 'admin' : 'doctor',
    },
    select: { id: true, email: true, name: true, role: true, createdAt: true },
  })
})
