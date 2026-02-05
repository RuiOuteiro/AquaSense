import pool from '../../utils/db'
import { verifyPassword, generateToken, setAuthCookie } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { email, password } = body

  if (!email || !password) {
    throw createError({
      statusCode: 400,
      message: 'Campos obrigatórios: email, password'
    })
  }

  try {
    const [rows] = await pool.execute(
      'SELECT id, email, password_hash, nome, ativo FROM utilizadores WHERE email = ?',
      [email.toLowerCase()]
    )

    const users = rows as any[]
    if (users.length === 0) {
      throw createError({
        statusCode: 401,
        message: 'Credenciais inválidas'
      })
    }

    const dbUser = users[0]

    if (!dbUser.ativo) {
      throw createError({
        statusCode: 403,
        message: 'Conta desactivada'
      })
    }

    const validPassword = await verifyPassword(password, dbUser.password_hash)
    if (!validPassword) {
      throw createError({
        statusCode: 401,
        message: 'Credenciais inválidas'
      })
    }

    await pool.execute(
      'UPDATE utilizadores SET ultimo_login = NOW() WHERE id = ?',
      [dbUser.id]
    )

    const user = { id: dbUser.id, email: dbUser.email, nome: dbUser.nome }
    const token = generateToken(user)

    setAuthCookie(event, token)

    return {
      success: true,
      message: 'Login efectuado com sucesso',
      user,
      token
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    
    console.error('[AUTH LOGIN] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao efectuar login'
    })
  }
})
