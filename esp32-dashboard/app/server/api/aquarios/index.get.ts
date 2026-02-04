import pool from '../../utils/db'
import { requireAuth } from '../../utils/auth'

export default defineEventHandler(async (event) => {
  const user = requireAuth(event)

  try {
    const [aquarios] = await pool.execute(
      `SELECT a.id, a.nome, a.descricao, a.device_id, a.criado_em,
              (SELECT COUNT(*) FROM leituras_sensores WHERE aquario_id = a.id) as total_leituras,
              (SELECT MAX(data_hora) FROM leituras_sensores WHERE aquario_id = a.id) as ultima_leitura
       FROM aquarios a 
       WHERE a.utilizador_id = ? AND a.ativo = 1
       ORDER BY a.criado_em DESC`,
      [user.id]
    )

    return {
      success: true,
      aquarios
    }
  } catch (error: any) {
    console.error('[AQUARIOS GET] Erro:', error.message)
    throw createError({
      statusCode: 500,
      message: 'Erro ao obter aquários'
    })
  }
})
