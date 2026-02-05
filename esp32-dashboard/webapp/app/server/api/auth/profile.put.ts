import pool from '../../utils/db'
import { requireAuth, hashPassword, verifyPassword } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const body = await readBody(event)
  const { nome, email, currentPassword, newPassword } = body

  try {
    const updates: string[] = []
    const values: any[] = []

    if (nome && nome.trim()) {
      updates.push('nome = ?')
      values.push(nome.trim())
    }

    if (email && email.trim()) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(email)) {
        throw createError({
          statusCode: 400,
          message: 'Email inválido'
        })
      }
      
      const [existing] = await pool.execute(
        'SELECT id FROM utilizadores WHERE email = ? AND id != ?',
        [email.toLowerCase(), user.id]
      )
      if ((existing as any[]).length > 0) {
        throw createError({
          statusCode: 409,
          message: 'Este email já está em uso'
        })
      }
      
      updates.push('email = ?')
      values.push(email.toLowerCase().trim())
    }

    if (newPassword) {
      if (!currentPassword) {
        throw createError({
          statusCode: 400,
          message: 'Password actual é obrigatória para alterar password'
        })
      }

      const [rows] = await pool.execute(
        'SELECT password_hash FROM utilizadores WHERE id = ?',
        [user.id]
      )
      const users = rows as any[]
      
      if (users.length === 0) {
        throw createError({
          statusCode: 404,
          message: 'Utilizador não encontrado'
        })
      }

      const validPassword = await verifyPassword(currentPassword, users[0].password_hash)
      if (!validPassword) {
        throw createError({
          statusCode: 401,
          message: 'Password actual incorrecta'
        })
      }

      if (newPassword.length < 6) {
        throw createError({
          statusCode: 400,
          message: 'Nova password deve ter pelo menos 6 caracteres'
        })
      }

      const hashedPassword = await hashPassword(newPassword)
      updates.push('password_hash = ?')
      values.push(hashedPassword)
    }

    if (updates.length === 0) {
      return { success: true, message: 'Sem alterações' }
    }

    values.push(user.id)
    await pool.execute(
      `UPDATE utilizadores SET ${updates.join(', ')} WHERE id = ?`,
      values
    )

    return {
      success: true,
      message: 'Perfil actualizado com sucesso'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    
    console.error('[PROFILE UPDATE] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao actualizar perfil'
    })
  }
})
