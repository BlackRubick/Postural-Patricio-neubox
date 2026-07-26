import bcrypt from 'bcryptjs'
import { prisma } from '~/server/utils/prisma'

export default defineEventHandler(async (event) => {
  const { name, email, password } = await readBody(event)

  if (!email?.trim() || !password || password.length < 6) {
    throw createError({ statusCode: 400, message: 'Email y contraseña (mín. 6 caracteres) son requeridos' })
  }

  const existing = await prisma.user.findUnique({ where: { email: email.trim().toLowerCase() } })
  if (existing) throw createError({ statusCode: 409, message: 'Ya existe una cuenta con ese correo' })

  const hashed = await bcrypt.hash(password, 10)
  return prisma.user.create({
    data: {
      email: email.trim().toLowerCase(),
      password: hashed,
      name: name?.trim() || null,
      role: 'doctor',
    },
    select: { id: true, email: true, name: true, role: true },
  })
})
