import { prisma } from '~/server/utils/prisma'
import { verifyToken } from '~/server/utils/jwt'

export default defineEventHandler(async (event) => {
  const token = getCookie(event, 'auth_token')
  if (!token) throw createError({ statusCode: 401, message: 'No autenticado' })

  try {
    const payload = await verifyToken(token)
    const user = await prisma.user.findUnique({
      where: { id: payload.userId as number },
      select: { id: true, email: true, name: true, role: true },
    })
    if (!user) throw createError({ statusCode: 401, message: 'Usuario no encontrado' })
    return user
  } catch {
    throw createError({ statusCode: 401, message: 'Token inválido' })
  }
})
