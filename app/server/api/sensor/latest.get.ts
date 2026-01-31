import pool from '../../utils/db'

export default defineEventHandler(async () => {
  try {
    const [rows] = await pool.execute(
      'SELECT id, id_dispositivo as device_id, tipo_sensor as sensor_type, valor as value, unidade as unit, data_hora as created_at FROM leituras_sensores ORDER BY data_hora DESC LIMIT 1'
    )
    
    return {
      success: true,
      data: (rows as any[])[0] || null
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
