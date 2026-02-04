import pool from '../utils/db'
import { getAuthUser } from '../utils/auth'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const limit = parseInt(query.limit as string) || 50
  const device_id = query.device_id as string
  const aquarioId = query.aquario_id ? parseInt(query.aquario_id as string) : 1

  const user = getAuthUser(event)

  try {
    // Se autenticado, verificar permissão
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
