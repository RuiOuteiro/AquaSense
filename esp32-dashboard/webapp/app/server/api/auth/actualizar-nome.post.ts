import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  
  const body = await readBody(event)
  const { nome } = body
  
  if (!nome || nome.trim().length < 2) {
    throw createError({
      statusCode: 400,
      message: 'Nome inválido (mínimo 2 caracteres)'
    })
  }
  
  try {
    await pool.execute(
      'UPDATE utilizadores SET nome = ? WHERE id = ?',
      [nome.trim(), user.id]
    )
    
    return {
      success: true,
      message: 'Nome actualizado com sucesso'
    }
  } catch (error) {
    console.error('[Auth] Erro ao actualizar nome:', error)
    throw createError({
      statusCode: 500,
      message: 'Erro ao actualizar nome'
    })
  }
})
