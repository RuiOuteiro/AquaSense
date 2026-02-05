import pool from '../../utils/db'
import { requireAuth, hashPassword, verifyPassword } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  
  const body = await readBody(event)
  const { currentPassword, newPassword } = body
  
  if (!currentPassword || !newPassword) {
    throw createError({
      statusCode: 400,
      message: 'Palavras-passe obrigatórias'
    })
  }
  
  if (newPassword.length < 6) {
    throw createError({
      statusCode: 400,
      message: 'Nova palavra-passe deve ter pelo menos 6 caracteres'
    })
  }
  
  try {
    // Obter password atual
    const [rows] = await pool.query(
      'SELECT password_hash FROM utilizadores WHERE id = ?',
      [user.id]
    ) as any[]
    
    if (!rows.length) {
      throw createError({
        statusCode: 404,
        message: 'Utilizador não encontrado'
      })
    }
    
    // Verificar password atual
    const isValid = await verifyPassword(currentPassword, rows[0].password_hash)
    if (!isValid) {
      throw createError({
        statusCode: 400,
        message: 'Palavra-passe actual incorrecta'
      })
    }
    
    // Hash da nova password
    const newHash = await hashPassword(newPassword)
    
    await pool.query(
      'UPDATE utilizadores SET password_hash = ? WHERE id = ?',
      [newHash, user.id]
    )
    
    return {
      success: true,
      message: 'Palavra-passe alterada com sucesso'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('[Auth] Erro ao alterar password:', error)
    throw createError({
      statusCode: 500,
      message: 'Erro ao alterar palavra-passe'
    })
  }
})
