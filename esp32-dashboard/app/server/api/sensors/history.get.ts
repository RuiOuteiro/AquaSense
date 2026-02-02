import pool from '../../utils/db'

export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  const hours = parseInt(query.hours as string) || 24
  const type = query.type as string

  try {
    let sql = `
      SELECT 
        tipo_sensor as sensor_type,
        valor as value,
        data_hora as created_at
      FROM leituras_sensores 
      WHERE data_hora >= DATE_SUB(NOW(), INTERVAL ? HOUR)
    `
    let params: any[] = [hours]

    if (type) {
      sql += ` AND tipo_sensor = ?`
      params.push(type)
    }

    sql += ` ORDER BY data_hora ASC`

    const [rows] = await pool.execute(sql, params)
    
    // Agrupar por tipo de sensor
    const grouped: Record<string, { value: number; created_at: string }[]> = {}
    
    for (const row of rows as any[]) {
      const sensorType = row.sensor_type
      if (!grouped[sensorType]) {
        grouped[sensorType] = []
      }
      grouped[sensorType].push({
        value: parseFloat(row.value),
        created_at: row.created_at
      })
    }
    
    return {
      success: true,
      data: grouped,
      period: `${hours}h`
    }
  } catch (error: any) {
    throw createError({
      statusCode: 500,
      message: `Erro na base de dados: ${error.message}`
    })
  }
})
