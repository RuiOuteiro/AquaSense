import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  
  const body = await readBody(event)
  const { email } = body
  
  if (!email || !email.includes('@')) {
    throw createError({
      statusCode: 400,
      message: 'Email inválido'
    })
  }
  
  try {
    // Verificar se email já existe
    const [existing] = await pool.query(
      'SELECT id FROM utilizadores WHERE email = ? AND id != ?',
      [email.trim(), user.id]
    ) as any[]
    
    if (existing.length > 0) {
      throw createError({
        statusCode: 400,
        message: 'Este email já está em uso'
      })
    }
    
    await pool.query(
      'UPDATE utilizadores SET email = ? WHERE id = ?',
      [email.trim(), user.id]
    )
    
    return {
      success: true,
      message: 'Email actualizado com sucesso'
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('[Auth] Erro ao actualizar email:', error)
    throw createError({
      statusCode: 500,
      message: 'Erro ao actualizar email'
    })
  }
})
