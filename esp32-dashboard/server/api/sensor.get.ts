import pool from '../utils/db'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const limit = parseInt(query.limit as string) || 50
  const device_id = query.device_id as string

  try {
    let sql = 'SELECT id, id_dispositivo as device_id, tipo_sensor as sensor_type, valor as value, unidade as unit, data_hora as created_at FROM leituras_sensores ORDER BY data_hora DESC LIMIT ?'
    let params: any[] = [limit]

    if (device_id) {
      sql = 'SELECT id, id_dispositivo as device_id, tipo_sensor as sensor_type, valor as value, unidade as unit, data_hora as created_at FROM leituras_sensores WHERE id_dispositivo = ? ORDER BY data_hora DESC LIMIT ?'
      params = [device_id, limit]
    }

    const [rows] = await pool.execute(sql, params)
    
    return {
      success: true,
      data: rows
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
