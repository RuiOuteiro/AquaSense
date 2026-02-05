import pool from '../utils/db'
import { getAuthUser } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const aquarioId = query.aquario_id ? parseInt(query.aquario_id as string) : 1
  
  // Verificar autenticação (opcional para retrocompatibilidade com ESP32)
  const user = getAuthUser(event)
  
  try {
    // Se autenticado, verificar se o aquário pertence ao utilizador
    if (user) {
      const [check] = await pool.execute(
        'SELECT id FROM aquarios WHERE id = ? AND utilizador_id = ?',
        [aquarioId, user.id]
      )
      if ((check as any[]).length === 0) {
        throw createError({
          statusCode: 403,
          message: 'Aquário não pertence ao utilizador'
        })
      }
    }

    const [rows] = await pool.execute(
      'SELECT * FROM configuracoes WHERE aquario_id = ?',
      [aquarioId]
    )
    
    return {
      success: true,
      data: (rows as any[])[0] || null
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
