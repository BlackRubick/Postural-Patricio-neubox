import bcrypt from 'bcryptjs'
import { prisma } from '~/server/utils/prisma'
import { signToken } from '~/server/utils/jwt'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { email, password } = body

  if (!email || !password) {
    throw createError({ statusCode: 400, message: 'Email y contraseña requeridos' })
  }

  const user = await prisma.user.findUnique({ where: { email } })
  if (!user) {
    throw createError({ statusCode: 401, message: 'Credenciales inválidas' })
  }

  const valid = await bcrypt.compare(password, user.password)
  if (!valid) {
    throw createError({ statusCode: 401, message: 'Credenciales inválidas' })
  }

  const token = await signToken({ userId: user.id, email: user.email, role: user.role })

  setCookie(event, 'auth_token', token, {
    httpOnly: true,
    maxAge: 60 * 60 * 24 * 7,
    path: '/',
    sameSite: 'lax',
  })

  return {
    user: { id: user.id, email: user.email, name: user.name, role: user.role },
  }
})
