import pool from '../../utils/db'
import { hashPassword, generateToken, setAuthCookie } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  const { email, password, nome } = body

  // Validação
  if (!email || !password || !nome) {
    throw createError({
      statusCode: 400,
      message: 'Campos obrigatórios: email, password, nome'
    })
  }

  if (password.length < 6) {
    throw createError({
      statusCode: 400,
      message: 'Password deve ter pelo menos 6 caracteres'
    })
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    throw createError({
      statusCode: 400,
      message: 'Email inválido'
    })
  }

  try {
    // Verificar se email já existe
    const [existing] = await pool.execute(
      'SELECT id FROM utilizadores WHERE email = ?',
      [email.toLowerCase()]
    )

    if ((existing as any[]).length > 0) {
      throw createError({
        statusCode: 409,
        message: 'Email já registado'
      })
    }

    // Hash da password
    const passwordHash = await hashPassword(password)

    // Inserir utilizador
    const [result] = await pool.execute(
      'INSERT INTO utilizadores (email, password_hash, nome) VALUES (?, ?, ?)',
      [email.toLowerCase(), passwordHash, nome]
    )

    const userId = (result as any).insertId

    // Criar aquário default para o novo utilizador
    await pool.execute(
      'INSERT INTO aquarios (utilizador_id, nome, descricao) VALUES (?, ?, ?)',
      [userId, 'Meu Aquário', 'Aquário criado automaticamente']
    )

    // Gerar token
    const user = { id: userId, email: email.toLowerCase(), nome }
    const token = generateToken(user)

    // Definir cookie
    setAuthCookie(event, token)

    return {
      success: true,
      message: 'Registo efectuado com sucesso',
      user,
      token
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    
    console.error('[AUTH REGISTER] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao registar utilizador'
    })
  }
})
