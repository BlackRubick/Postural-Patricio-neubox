import { prisma } from './prisma'
import { verifyToken } from './jwt'

export async function requireAuth(event: Parameters<typeof getCookie>[0]) {
  const token = getCookie(event, 'auth_token')
  if (!token) throw createError({ statusCode: 401, message: 'No autenticado' })

  let payload: Awaited<ReturnType<typeof verifyToken>>
  try {
    payload = await verifyToken(token)
  } catch {
    throw createError({ statusCode: 401, message: 'Token inválido' })
  }

  const user = await prisma.user.findUnique({
    where: { id: payload.userId as number },
    select: { id: true, email: true, name: true, role: true },
  })
  if (!user) throw createError({ statusCode: 401, message: 'Usuario no encontrado' })
  return user
}

export async function requireAdmin(event: Parameters<typeof getCookie>[0]) {
  const user = await requireAuth(event)
  if (user.role !== 'admin') throw createError({ statusCode: 403, message: 'Acceso denegado: se requiere rol admin' })
  return user
}
