import pool from '../utils/db'
import { getAuthUser } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const limit = parseInt(query.limit as string) || 50
  const device_id = query.device_id as string
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
  if (!aquarioId) aquarioId = 1 // Fallback ESP32

  try {
    // Se autenticado, verificar permissão
    if (user && aquarioId) {
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

    let sql = 'SELECT id, aquario_id, id_dispositivo as device_id, tipo_sensor as sensor_type, valor as value, unidade as unit, data_hora as created_at FROM leituras_sensores WHERE aquario_id = ? ORDER BY data_hora DESC LIMIT ?'
    let params: any[] = [aquarioId, limit]

    if (device_id) {
      sql = 'SELECT id, aquario_id, id_dispositivo as device_id, tipo_sensor as sensor_type, valor as value, unidade as unit, data_hora as created_at FROM leituras_sensores WHERE aquario_id = ? AND id_dispositivo = ? ORDER BY data_hora DESC LIMIT ?'
      params = [aquarioId, device_id, limit]
    }

    const [rows] = await pool.execute(sql, params)
    
    return {
      success: true,
      data: rows
    }
  } catch (error: any) {
    if (error.statusCode) throw error
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
