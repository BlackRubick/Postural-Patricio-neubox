import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  const hashed = await bcrypt.hash('123123123', 10)

  const user = await prisma.user.upsert({
    where: { email: 'doctor@gmail.com' },
    update: { password: hashed, name: 'Doctor', role: 'doctor' },
    create: {
      email: 'doctor@gmail.com',
      password: hashed,
      name: 'Doctor',
      role: 'doctor',
    },
  })

  console.log('Usuario creado:', user.email)
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect())
