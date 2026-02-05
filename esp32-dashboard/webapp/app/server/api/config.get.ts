import pool from '../utils/db'
import { getAuthUser } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const user = getAuthUser(event)
  
  // Obter aquario_id do query ou do primeiro aquário do utilizador
  let aquarioId = query.aquario_id ? parseInt(query.aquario_id as string) : null
  
  if (!aquarioId && user) {
    const [userAquarios] = await pool.execute(
      'SELECT id FROM aquarios WHERE utilizador_id = ? AND ativo = 1 ORDER BY id ASC LIMIT 1',
      [user.id]
    )
    if ((userAquarios as any[]).length > 0) {
      aquarioId = (userAquarios as any[])[0].id
    }
  }
  
  if (!aquarioId) {
    aquarioId = 1 // Fallback para ESP32 sem autenticação
  }
  
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
