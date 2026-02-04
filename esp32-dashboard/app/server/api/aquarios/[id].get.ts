import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)
  const id = getRouterParam(event, 'id')

  if (!id) {
    throw createError({
      statusCode: 400,
      message: 'ID do aquário é obrigatório'
    })
  }

  try {
    const [rows] = await pool.execute(
      `SELECT a.*, 
              (SELECT COUNT(*) FROM leituras_sensores WHERE aquario_id = a.id) as total_leituras,
              (SELECT MAX(data_hora) FROM leituras_sensores WHERE aquario_id = a.id) as ultima_leitura
       FROM aquarios a 
       WHERE a.id = ? AND a.utilizador_id = ? AND a.ativo = 1`,
      [id, user.id]
    )

    const aquarios = rows as any[]
    if (aquarios.length === 0) {
      throw createError({
        statusCode: 404,
        message: 'Aquário não encontrado'
      })
    }

    return {
      success: true,
      aquario: aquarios[0]
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    console.error('[AQUARIO GET] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter aquário'
    })
  }
})
